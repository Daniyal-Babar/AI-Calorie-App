from datetime import datetime, timezone
from app.extensions import db

class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(200), default="Nutrition Assistant")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    messages = db.relationship(
        "Message",
        backref="conversation",
        lazy=True,
        order_by="Message.created_at",
        cascade="all, delete-orphan",
    )

    def to_dict(self, include_messages=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_messages:
            data["messages"] = [m.to_dict() for m in self.messages]
        return data


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer, db.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system, tool
    content = db.Column(db.Text, nullable=True)

    # Tool calling tracking & context
    tool_calls = db.Column(db.JSON, nullable=True)  # [{id, name, arguments}]
    tool_results = db.Column(db.JSON, nullable=True)  # [{tool_call_id, name, result}]

    # Typed UI response blocks for modern frontend rendering
    blocks = db.Column(db.JSON, nullable=True)  # [{type: 'text'|'meal_card'|'daily_summary'|..., data: {...}}]

    # Pending destructive action confirmations (delete_meal, clear_history)
    pending_action = db.Column(db.JSON, nullable=True)  # {action_id, action_type, payload, status: 'pending'}

    # Optional image attachment reference
    image_id = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content or "",
            "tool_calls": self.tool_calls or [],
            "tool_results": self.tool_results or [],
            "blocks": self.blocks or [],
            "pending_action": self.pending_action,
            "image_id": self.image_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
