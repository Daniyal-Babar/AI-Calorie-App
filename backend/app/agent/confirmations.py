import uuid
from typing import Dict, Any

class ConfirmationManager:
    @staticmethod
    def create_pending_action(
        tool_name: str,
        tool_args: Dict[str, Any],
        description: str,
    ) -> Dict[str, Any]:
        """Create a pending destructive action descriptor."""
        action_id = f"act_{uuid.uuid4().hex[:12]}"
        return {
            "action_id": action_id,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "description": description,
            "status": "pending",
        }

    @staticmethod
    def build_confirmation_block(pending_action: Dict[str, Any]) -> Dict[str, Any]:
        """Format an action block for the frontend to render interactive confirmation buttons."""
        return {
            "type": "actions",
            "data": {
                "action_id": pending_action["action_id"],
                "description": pending_action["description"],
                "options": [
                    {"label": "Confirm", "value": "confirm", "variant": "danger"},
                    {"label": "Cancel", "value": "cancel", "variant": "secondary"},
                ],
            },
        }
