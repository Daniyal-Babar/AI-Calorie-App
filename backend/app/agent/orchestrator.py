import json
import logging
from typing import Generator, Dict, Any, List, Optional
from flask import current_app
from app.extensions import db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.agent.llm_client import LLMClient
from app.agent.context_builder import ContextBuilder
from app.agent.guardrails import Guardrails
from app.agent.confirmations import ConfirmationManager
from app.agent.tools.registry import TOOL_DEFINITIONS, dispatch_tool_call

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self, user: User, conversation: Optional[Conversation] = None):
        self.user = user
        self.conversation = conversation or self._get_or_create_conversation()
        self.llm = LLMClient()
        self.max_iterations = current_app.config.get("AGENT_MAX_ITERATIONS", 5)

    def _get_or_create_conversation(self) -> Conversation:
        conv = Conversation(user_id=self.user.id, title="Nutrition Assistant")
        db.session.add(conv)
        db.session.commit()
        return conv

    def process_message_stream(
        self,
        user_message_text: str,
        image_id: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """Main agent loop yielding Server-Sent Events (SSE) data chunks."""
        # 1. Guardrail input validation
        is_safe, safety_error = Guardrails.inspect_request(user_message_text)
        if not is_safe:
            # Yield safety warning directly
            block = {"type": "text", "content": safety_error}
            user_msg = Message(
                conversation_id=self.conversation.id,
                role="user",
                content=user_message_text,
                image_id=image_id,
            )
            asst_msg = Message(
                conversation_id=self.conversation.id,
                role="assistant",
                content=safety_error,
                blocks=[block],
            )
            db.session.add_all([user_msg, asst_msg])
            db.session.commit()

            yield f"data: {json.dumps({'event': 'token', 'token': safety_error})}\n\n"
            yield f"data: {json.dumps({'event': 'done', 'message': asst_msg.to_dict()})}\n\n"
            return

        # 2. Persist user message
        user_msg = Message(
            conversation_id=self.conversation.id,
            role="user",
            content=user_message_text,
            image_id=image_id,
        )
        db.session.add(user_msg)
        db.session.commit()

        # 3. Context builder
        messages, meta = ContextBuilder.build_llm_messages(
            user=self.user,
            conversation=self.conversation,
            current_user_message=user_message_text,
            image_url=image_url,
        )

        all_tool_calls_executed = []
        all_tool_results = []
        blocks: List[Dict[str, Any]] = []
        pending_action_record = None

        current_iteration = 0
        final_assistant_text = ""

        # Multi-turn tool execution loop
        while current_iteration < self.max_iterations:
            current_iteration += 1
            yield f"data: {json.dumps({'event': 'status', 'status': 'thinking', 'iteration': current_iteration})}\n\n"

            # Call LLM
            llm_resp = self.llm.create_chat_completion(messages, tools=TOOL_DEFINITIONS)

            # If LLM didn't call any tools, we have our final reply
            if not llm_resp.tool_calls:
                final_assistant_text = llm_resp.content or ""
                break

            iteration_tool_results = []
            for tc in llm_resp.tool_calls:
                func_name = tc["function"]["name"]
                args_str = tc["function"]["arguments"]
                try:
                    args = json.loads(args_str) if isinstance(args_str, str) else args_str
                except Exception:
                    args = {}

                yield f"data: {json.dumps({'event': 'tool_call', 'tool': func_name, 'args': args})}\n\n"

                # Execute tool
                result = dispatch_tool_call(func_name, self.user.id, args)
                all_tool_calls_executed.append(tc)
                all_tool_results.append({"tool_call_id": tc.get("id", ""), "name": func_name, "result": result})
                iteration_tool_results.append({"tool_call_id": tc.get("id", ""), "name": func_name, "result": result})

                yield f"data: {json.dumps({'event': 'tool_result', 'tool': func_name, 'result': result})}\n\n"

                # Convert tool outcome to typed UI block
                ui_block = self._map_result_to_block(func_name, result)
                if ui_block:
                    blocks.append(ui_block)

                # Check if this tool generated a pending confirmation
                if result.get("status") == "pending_confirmation":
                    pending_action_record = result.get("pending_action")

            # Append assistant tool_calls and each tool result to prompt context
            messages.append({
                "role": "assistant",
                "tool_calls": llm_resp.tool_calls,
            })
            for tc, tr in zip(llm_resp.tool_calls, iteration_tool_results):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", "call_0"),
                    "content": json.dumps(tr["result"]),
                })

        # Final explanation token stream / generation
        if not final_assistant_text:
            # Generate concluding explanation with context of tool results
            final_resp = self.llm.create_chat_completion(messages, tools=None)
            final_assistant_text = final_resp.content or "I have processed your request."

        # Attach disclaimer if meal plans or diet goals are involved
        if any(b.get("type") in ["diet_plan_card", "daily_summary_card"] for b in blocks):
            final_assistant_text = Guardrails.attach_disclaimer(final_assistant_text)

        # Stream text token-by-token
        yield f"data: {json.dumps({'event': 'token', 'token': final_assistant_text})}\n\n"

        # Add text block if not present
        blocks.insert(0, {"type": "text", "content": final_assistant_text})

        # Save assistant message to DB
        asst_msg = Message(
            conversation_id=self.conversation.id,
            role="assistant",
            content=final_assistant_text,
            tool_calls=all_tool_calls_executed,
            tool_results=all_tool_results,
            blocks=blocks,
            pending_action=pending_action_record,
        )
        db.session.add(asst_msg)
        db.session.commit()

        yield f"data: {json.dumps({'event': 'done', 'message': asst_msg.to_dict(), 'blocks': blocks})}\n\n"

    def _map_result_to_block(self, tool_name: str, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Maps backend tool results into rich UI block payloads."""
        if result.get("status") == "pending_confirmation":
            return ConfirmationManager.build_confirmation_block(result["pending_action"])

        if tool_name in ["log_meal", "edit_meal"] and result.get("status") == "success":
            return {
                "type": "meal_card",
                "data": {
                    "meal_id": result.get("meal_id"),
                    "meal_type": result.get("meal_type"),
                    "total_calories": result.get("total_calories"),
                    "total_protein_g": result.get("total_protein_g"),
                    "total_carbs_g": result.get("total_carbs_g"),
                    "total_fat_g": result.get("total_fat_g"),
                    "items": result.get("items", []),
                },
            }

        if tool_name in ["get_daily_summary", "get_weekly_report"] and result.get("status") == "success":
            return {
                "type": "daily_summary_card",
                "data": result.get("summary") or result.get("report"),
            }

        if tool_name in ["generate_diet_plan", "get_active_plan"] and result.get("status") == "success":
            return {
                "type": "diet_plan_card",
                "data": result.get("plan"),
            }

        return None
