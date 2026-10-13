from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.extensions import db
from app.models.daily_goal import DailyGoal
from app.schemas.tool_schemas import SetCalorieGoalInput

def tool_set_calorie_goal(
    user_id: int,
    calorie_target: float,
    protein_g: Optional[float] = None,
    carbs_g: Optional[float] = None,
    fat_g: Optional[float] = None,
) -> Dict[str, Any]:
    """Set the user's daily calorie and macronutrient targets."""
    # Deactivate existing
    DailyGoal.query.filter_by(user_id=user_id, is_active=True).update({"is_active": False})

    # If macros omitted, calculate balanced distribution
    # Protein ~25%, Fat ~25%, Carbs ~50%
    if protein_g is None:
        protein_g = round((calorie_target * 0.25) / 4.0, 1)
    if fat_g is None:
        fat_g = round((calorie_target * 0.25) / 9.0, 1)
    if carbs_g is None:
        carbs_g = round((calorie_target * 0.50) / 4.0, 1)

    new_goal = DailyGoal(
        user_id=user_id,
        calorie_target=calorie_target,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        is_active=True,
        effective_from=datetime.now(timezone.utc),
    )
    db.session.add(new_goal)
    db.session.commit()

    return {
        "status": "success",
        "goal": new_goal.to_dict(),
        "message": f"Daily goal set to {calorie_target} kcal (Protein: {protein_g}g, Carbs: {carbs_g}g, Fat: {fat_g}g).",
    }
