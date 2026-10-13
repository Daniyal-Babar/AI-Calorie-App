from datetime import datetime, timezone
from app.extensions import db

class DailyGoal(db.Model):
    __tablename__ = "daily_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    calorie_target = db.Column(db.Float, nullable=False, default=2000.0)
    protein_g = db.Column(db.Float, nullable=False, default=120.0)
    carbs_g = db.Column(db.Float, nullable=False, default=220.0)
    fat_g = db.Column(db.Float, nullable=False, default=65.0)
    water_ml = db.Column(db.Float, nullable=True, default=2500.0)
    is_active = db.Column(db.Boolean, default=True)
    effective_from = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "calorie_target": self.calorie_target,
            "protein_g": self.protein_g,
            "carbs_g": self.carbs_g,
            "fat_g": self.fat_g,
            "water_ml": self.water_ml,
            "is_active": self.is_active,
            "effective_from": self.effective_from.isoformat() if self.effective_from else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
