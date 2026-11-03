from typing import Dict, Any, Optional
from app.extensions import db
from app.models.user import User
from app.services.diet_service import DietService
from app.services.calorie_service import CalorieService
from app.schemas.tool_schemas import GenerateDietPlanInput

def tool_generate_diet_plan(
    user_id: int,
    goal_type: str = "weight_loss",
    target_daily_calories: Optional[float] = None,
    duration_weeks: int = 4,
    dietary_preferences: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate and activate a structured diet plan for the user."""
    user = db.session.get(User, user_id)
    if not user:
        return {"status": "error", "message": "User not found."}

    # Validate inputs
    try:
        validated = GenerateDietPlanInput(
            goal_type=goal_type,
            target_daily_calories=target_daily_calories,
            duration_weeks=duration_weeks,
            dietary_preferences=dietary_preferences,
        )
    except Exception as e:
        return {"status": "error", "message": f"Invalid diet plan parameters: {str(e)}"}

    missing_fields = user.missing_profile_fields()
    calc = CalorieService.calculate_recommended_target(user, validated.goal_type)
    final_calories = validated.target_daily_calories or calc["calories"]

    structured_meals = DietService.build_structured_sample_plan(validated.goal_type, final_calories)
    title = f"{validated.goal_type.replace('_', ' ').title()} Plan ({final_calories} kcal)"

    recommendations = (
        f"Goal: {validated.goal_type.replace('_', ' ')}. Maintain consistent hydration (~2.5L water daily). "
        f"Target {final_calories} kcal daily."
    )
    if validated.dietary_preferences:
        recommendations += f" Focus on {validated.dietary_preferences}."
    if missing_fields:
        recommendations += f" Note: Calculated using standard assumptions because profile fields ({', '.join(missing_fields)}) are not set."

    plan = DietService.save_plan(
        user_id=user_id,
        title=title,
        goal_type=validated.goal_type,
        target_daily_calories=final_calories,
        duration_weeks=validated.duration_weeks or 4,
        meals_json=structured_meals,
        recommendations=recommendations,
    )

    msg = f"Generated and activated diet plan '{plan.title}' with target {plan.target_daily_calories} kcal/day."
    if missing_fields:
        msg += f" Note: For a fully personalized plan, please update your profile ({', '.join(missing_fields)})."

    return {
        "status": "success",
        "plan": plan.to_dict(),
        "missing_profile_fields": missing_fields,
        "message": msg,
    }

def tool_get_active_plan(user_id: int) -> Dict[str, Any]:
    """Retrieve the user's currently active diet plan."""
    plan = DietService.get_active_plan(user_id)
    if not plan:
        return {"status": "none", "message": "No active diet plan found."}
    return {"status": "success", "plan": plan.to_dict()}
