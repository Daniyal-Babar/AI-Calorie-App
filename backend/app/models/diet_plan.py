from datetime import datetime, timezone
from app.extensions import db

class DietPlan(db.Model):
    __tablename__ = "diet_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False, default="Personalized Nutrition Plan")
    goal_type = db.Column(db.String(50), nullable=False, default="weight_loss")  # weight_loss, muscle_gain, maintenance
    target_daily_calories = db.Column(db.Float, nullable=False, default=2000.0)
    duration_weeks = db.Column(db.Integer, default=4)
    meals_json = db.Column(db.JSON, nullable=True)  # structured meal suggestions
    recommendations = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "goal_type": self.goal_type,
            "target_daily_calories": self.target_daily_calories,
            "duration_weeks": self.duration_weeks,
            "meals_json": self.meals_json or {},
            "recommendations": self.recommendations,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
