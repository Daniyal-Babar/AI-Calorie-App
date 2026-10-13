from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequestSchema(BaseModel):
    message: str = Field(..., description="User message text")
    conversation_id: Optional[int] = Field(None, description="Existing conversation id or null for new")
    image_id: Optional[str] = Field(None, description="Optional uploaded image ID")

class ConfirmActionSchema(BaseModel):
    action_id: str = Field(..., description="Action ID to confirm or cancel")
    conversation_id: int = Field(..., description="Conversation ID containing the action")
    confirmed: bool = Field(..., description="True to execute, False to reject")
