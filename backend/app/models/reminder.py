from datetime import datetime, timezone
from app.extensions import db

class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    schedule_time = db.Column(db.String(50), nullable=False)  # e.g., "08:00", "13:00", "20:00"
    text = db.Column(db.String(255), nullable=False, default="Time to log your meal!")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "schedule_time": self.schedule_time,
            "text": self.text,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
