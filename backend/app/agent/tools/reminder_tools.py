from typing import Dict, Any
from app.extensions import db
from app.models.reminder import Reminder

def tool_set_reminder(user_id: int, schedule_time: str, text: str = "Time to log your meal!") -> Dict[str, Any]:
    """Schedule a recurring daily reminder for the user."""
    reminder = Reminder(
        user_id=user_id,
        schedule_time=schedule_time,
        text=text,
        is_active=True,
    )
    db.session.add(reminder)
    db.session.commit()

    return {
        "status": "success",
        "reminder": reminder.to_dict(),
        "message": f"Reminder set for {schedule_time}: '{text}'",
    }

def tool_list_reminders(user_id: int) -> Dict[str, Any]:
    """List all scheduled reminders for the user."""
    reminders = Reminder.query.filter_by(user_id=user_id, is_active=True).all()
    return {
        "status": "success",
        "count": len(reminders),
        "reminders": [r.to_dict() for r in reminders],
    }
