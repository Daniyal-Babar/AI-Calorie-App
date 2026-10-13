from typing import Optional, Dict, Any
from app.extensions import db
from app.models.diet_plan import DietPlan
from app.models.user import User
from app.services.calorie_service import CalorieService

class DietService:
    @staticmethod
    def get_active_plan(user_id: int) -> Optional[DietPlan]:
        return DietPlan.query.filter_by(user_id=user_id, is_active=True).first()

    @staticmethod
    def save_plan(
        user_id: int,
        title: str,
        goal_type: str,
        target_daily_calories: float,
        duration_weeks: int,
        meals_json: Dict[str, Any],
        recommendations: str,
    ) -> DietPlan:
        # Deactivate existing plans
        DietPlan.query.filter_by(user_id=user_id, is_active=True).update({"is_active": False})
        
        plan = DietPlan(
            user_id=user_id,
            title=title,
            goal_type=goal_type,
            target_daily_calories=target_daily_calories,
            duration_weeks=duration_weeks,
            meals_json=meals_json,
            recommendations=recommendations,
            is_active=True,
        )
        db.session.add(plan)
        db.session.commit()
        return plan

    @staticmethod
    def build_structured_sample_plan(goal_type: str, calories: float) -> Dict[str, Any]:
        """Provides a balanced template meal schedule for the requested goal."""
        b_cals = round(calories * 0.25)
        l_cals = round(calories * 0.35)
        d_cals = round(calories * 0.30)
        s_cals = round(calories * 0.10)

        return {
            "daily_target_calories": calories,
            "meals": [
                {
                    "slot": "Breakfast",
                    "target_calories": b_cals,
                    "suggestions": ["Rolled oats with chia seeds and almond milk", "2 scrambled eggs with spinach"],
                    "protein_g": round(b_cals * 0.075),
                },
                {
                    "slot": "Lunch",
                    "target_calories": l_cals,
                    "suggestions": ["Grilled chicken or tofu bowl with brown rice and steamed broccoli", "Olive oil dressing"],
                    "protein_g": round(l_cals * 0.08),
                },
                {
                    "slot": "Dinner",
                    "target_calories": d_cals,
                    "suggestions": ["Pan-seared salmon or lentils with roasted sweet potato and mixed greens"],
                    "protein_g": round(d_cals * 0.075),
                },
                {
                    "slot": "Snacks / Hydration",
                    "target_calories": s_cals,
                    "suggestions": ["Greek yogurt with blueberries", "A handful of raw almonds"],
                    "protein_g": round(s_cals * 0.05),
                },
            ],
        }
