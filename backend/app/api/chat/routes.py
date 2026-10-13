import json
from flask import Blueprint, request, Response, jsonify, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.agent.orchestrator import AgentOrchestrator
from app.agent.tools.registry import dispatch_tool_call
from app.services.upload_service import UploadService
from app.utils.rate_limiter import check_rate_limit
from app.schemas.chat_schemas import ChatRequestSchema, ConfirmActionSchema
from pydantic import ValidationError

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")

@chat_bp.route("", methods=["POST"])
@jwt_required()
def send_chat_message():
    user_id = int(get_jwt_identity())
    check_rate_limit(f"user_{user_id}")

    data = request.get_json() or {}
    try:
        validated = ChatRequestSchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 422

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Resolve conversation
    conv = None
    if validated.conversation_id:
        conv = Conversation.query.filter_by(id=validated.conversation_id, user_id=user.id).first()

    orchestrator = AgentOrchestrator(user=user, conversation=conv)

    image_path = None
    if validated.image_id:
        image_path = UploadService.get_file_path(validated.image_id)

    stream = orchestrator.process_message_stream(
        user_message_text=validated.message,
        image_id=validated.image_id,
        image_url=image_path,
    )

    return Response(
        stream_with_context(stream),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )

@chat_bp.route("/history", methods=["GET"])
@jwt_required()
def get_chat_history():
    user_id = int(get_jwt_identity())
    conv_id = request.args.get("conversation_id", type=int)

    if conv_id:
        conv = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
        if not conv:
            return jsonify({"error": "Conversation not found"}), 404
        return jsonify(conv.to_dict(include_messages=True)), 200

    # Otherwise return latest conversation or list of all conversations
    conversations = (
        Conversation.query.filter_by(user_id=user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(20)
        .all()
    )

    # If there's an active one, include its messages
    active_conv = conversations[0] if conversations else None
    active_data = active_conv.to_dict(include_messages=True) if active_conv else None

    return jsonify({
        "conversations": [c.to_dict(include_messages=False) for c in conversations],
        "active_conversation": active_data,
    }), 200

@chat_bp.route("/confirm", methods=["POST"])
@jwt_required()
def confirm_action():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    try:
        validated = ConfirmActionSchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 422

    # Locate the message with this pending action
    msg = (
        Message.query.join(Conversation)
        .filter(
            Conversation.id == validated.conversation_id,
            Conversation.user_id == user_id,
        )
        .order_by(Message.created_at.desc())
        .first()
    )

    if not msg or not msg.pending_action:
        return jsonify({"error": "No pending action found for this conversation."}), 404

    action = msg.pending_action
    if action.get("action_id") != validated.action_id:
        return jsonify({"error": "Action ID mismatch."}), 400

    if not validated.confirmed:
        action["status"] = "cancelled"
        msg.pending_action = action
        db.session.commit()
        return jsonify({"status": "cancelled", "message": "Action cancelled by user."}), 200

    # Execute the underlying destructive tool
    tool_name = action.get("tool_name")
    tool_args = action.get("tool_args", {})
    result = dispatch_tool_call(tool_name, user_id, tool_args)

    action["status"] = "executed"
    action["result"] = result
    msg.pending_action = action

    # Add confirmation result message to chat
    reply_msg = Message(
        conversation_id=validated.conversation_id,
        role="assistant",
        content=result.get("message", "Action confirmed and executed."),
        blocks=[{"type": "text", "content": result.get("message", "Action confirmed and executed.")}],
    )
    db.session.add(reply_msg)
    db.session.commit()

    return jsonify({"status": "success", "result": result, "message": reply_msg.to_dict()}), 200
