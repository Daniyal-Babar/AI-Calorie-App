from typing import Dict, Any, Optional
from app.models.user import User
from app.services.diet_service import DietService
from app.services.calorie_service import CalorieService

def tool_generate_diet_plan(
    user_id: int,
    goal_type: str = "weight_loss",
    target_daily_calories: Optional[float] = None,
    duration_weeks: int = 4,
    dietary_preferences: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate and activate a structured diet plan for the user."""
    user = User.query.get(user_id)
    if not user:
        return {"status": "error", "message": "User not found."}

    if not target_daily_calories:
        calc = CalorieService.calculate_recommended_target(user, goal_type)
        target_daily_calories = calc["calories"]

    structured_meals = DietService.build_structured_sample_plan(goal_type, target_daily_calories)
    title = f"{goal_type.replace('_', ' ').title()} Plan ({target_daily_calories} kcal)"
    
    recommendations = (
        f"Goal: {goal_type.replace('_', ' ')}. Maintain consistent hydration (~2.5L water daily). "
        f"Target {target_daily_calories} kcal daily."
    )
    if dietary_preferences:
        recommendations += f" Focus on {dietary_preferences}."

    plan = DietService.save_plan(
        user_id=user_id,
        title=title,
        goal_type=goal_type,
        target_daily_calories=target_daily_calories,
        duration_weeks=duration_weeks,
        meals_json=structured_meals,
        recommendations=recommendations,
    )

    return {
        "status": "success",
        "plan": plan.to_dict(),
        "message": f"Generated and activated diet plan '{plan.title}' with target {plan.target_daily_calories} kcal/day.",
    }

def tool_get_active_plan(user_id: int) -> Dict[str, Any]:
    """Retrieve the user's currently active diet plan."""
    plan = DietService.get_active_plan(user_id)
    if not plan:
        return {"status": "none", "message": "No active diet plan found."}
    return {"status": "success", "plan": plan.to_dict()}
