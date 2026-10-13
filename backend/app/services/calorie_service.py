from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import func
from app.extensions import db
from app.models.meal import Meal, MealItem
from app.models.daily_goal import DailyGoal
from app.models.user import User

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

class CalorieService:
    @staticmethod
    def calculate_bmr(user: User) -> Optional[float]:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor formula."""
        if not user.current_weight_kg or not user.height_cm or not user.age:
            return None
        
        weight = float(user.current_weight_kg)
        height = float(user.height_cm)
        age = int(user.age)
        gender = (user.gender or "").lower()

        base = (10 * weight) + (6.25 * height) - (5 * age)
        if gender == "male":
            return round(base + 5, 1)
        elif gender == "female":
            return round(base - 161, 1)
        else:
            return round(base - 78, 1)

    @staticmethod
    def calculate_tdee(user: User) -> Optional[float]:
        """Calculate Total Daily Energy Expenditure."""
        bmr = CalorieService.calculate_bmr(user)
        if not bmr:
            return None
        
        level = (user.activity_level or "sedentary").lower()
        multiplier = ACTIVITY_MULTIPLIERS.get(level, 1.2)
        return round(bmr * multiplier, 1)

    @staticmethod
    def calculate_recommended_target(user: User, goal_type: str = "weight_loss") -> Dict[str, float]:
        """Calculate target calories and macros based on TDEE and goal."""
        tdee = CalorieService.calculate_tdee(user) or 2000.0
        weight = user.current_weight_kg or 70.0

        if goal_type == "weight_loss":
            calories = max(1200.0, round(tdee - 500, 0))
            protein_g = round(weight * 2.0, 1)  # High protein during deficit
        elif goal_type == "muscle_gain":
            calories = round(tdee + 300, 0)
            protein_g = round(weight * 2.2, 1)
        else:  # maintenance
            calories = round(tdee, 0)
            protein_g = round(weight * 1.6, 1)

        # Macro calories: Protein = 4 kcal/g, Fat = 9 kcal/g, Carbs = 4 kcal/g
        fat_calories = calories * 0.25
        fat_g = round(fat_calories / 9.0, 1)
        protein_calories = protein_g * 4.0
        carbs_calories = max(0.0, calories - (protein_calories + fat_calories))
        carbs_g = round(carbs_calories / 4.0, 1)

        return {
            "calories": calories,
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
        }

    @staticmethod
    def get_daily_summary(user_id: int, target_date: Optional[datetime.date] = None) -> Dict[str, Any]:
        """Aggregate all meals for a given date and compare to the user's active goal."""
        if target_date is None:
            target_date = datetime.now(timezone.utc).date()

        start_dt = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_dt = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)

        meals = (
            Meal.query.filter(
                Meal.user_id == user_id,
                Meal.logged_at >= start_dt,
                Meal.logged_at <= end_dt,
            )
            .order_by(Meal.logged_at.asc())
            .all()
        )

        total_calories = round(sum(m.total_calories for m in meals), 1)
        total_protein = round(sum(m.total_protein_g for m in meals), 1)
        total_carbs = round(sum(m.total_carbs_g for m in meals), 1)
        total_fat = round(sum(m.total_fat_g for m in meals), 1)

        # Fetch active goal
        goal = DailyGoal.query.filter_by(user_id=user_id, is_active=True).first()
        calorie_target = goal.calorie_target if goal else 2000.0
        protein_target = goal.protein_g if goal else 120.0
        carbs_target = goal.carbs_g if goal else 220.0
        fat_target = goal.fat_g if goal else 65.0

        remaining_calories = round(calorie_target - total_calories, 1)
        pct_consumed = round((total_calories / calorie_target) * 100, 1) if calorie_target > 0 else 0

        meal_breakdowns = []
        for m in meals:
            meal_breakdowns.append({
                "id": m.id,
                "meal_type": m.meal_type,
                "time": m.logged_at.strftime("%H:%M") if m.logged_at else "",
                "calories": m.total_calories,
                "protein_g": m.total_protein_g,
                "carbs_g": m.total_carbs_g,
                "fat_g": m.total_fat_g,
                "items_count": len(m.items),
                "items": [it.name for it in m.items],
            })

        return {
            "date": target_date.isoformat(),
            "consumed": {
                "calories": total_calories,
                "protein_g": total_protein,
                "carbs_g": total_carbs,
                "fat_g": total_fat,
            },
            "targets": {
                "calories": calorie_target,
                "protein_g": protein_target,
                "carbs_g": carbs_target,
                "fat_g": fat_target,
            },
            "remaining_calories": remaining_calories,
            "percent_consumed": pct_consumed,
            "meals_count": len(meals),
            "meals": meal_breakdowns,
        }

    @staticmethod
    def get_weekly_report(user_id: int) -> Dict[str, Any]:
        """Aggregate the last 7 days of nutrition intake."""
        today = datetime.now(timezone.utc).date()
        days_data = []

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            summary = CalorieService.get_daily_summary(user_id, day)
            days_data.append({
                "date": day.strftime("%a (%m/%d)"),
                "calories": summary["consumed"]["calories"],
                "target": summary["targets"]["calories"],
                "protein_g": summary["consumed"]["protein_g"],
            })

        avg_calories = round(sum(d["calories"] for d in days_data) / 7.0, 1)
        total_logged_days = sum(1 for d in days_data if d["calories"] > 0)

        return {
            "days": days_data,
            "average_daily_calories": avg_calories,
            "days_logged": total_logged_days,
            "period": f"{(today - timedelta(days=6)).isoformat()} to {today.isoformat()}",
        }
