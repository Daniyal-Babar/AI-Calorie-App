from typing import Dict, Any, Optional
from app.extensions import db
from app.models.user import User
from app.services.calorie_service import CalorieService

def tool_get_profile(user_id: int) -> Dict[str, Any]:
    """Retrieve the user's personal biometrics and profile."""
    user = User.query.get(user_id)
    if not user:
        return {"status": "error", "message": "User not found."}

    bmr = CalorieService.calculate_bmr(user)
    tdee = CalorieService.calculate_tdee(user)

    data = user.to_dict()
    data["bmr"] = bmr
    data["tdee"] = tdee
    return {"status": "success", "profile": data}

def tool_update_profile(
    user_id: int,
    name: Optional[str] = None,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    height_cm: Optional[float] = None,
    current_weight_kg: Optional[float] = None,
    target_weight_kg: Optional[float] = None,
    activity_level: Optional[str] = None,
) -> Dict[str, Any]:
    """Update user biometric fields and recalculate metabolic metrics."""
    user = User.query.get(user_id)
    if not user:
        return {"status": "error", "message": "User not found."}

    if name:
        user.name = name
    if age is not None:
        user.age = int(age)
    if gender:
        user.gender = gender.lower()
    if height_cm is not None:
        user.height_cm = float(height_cm)
    if current_weight_kg is not None:
        user.current_weight_kg = float(current_weight_kg)
    if target_weight_kg is not None:
        user.target_weight_kg = float(target_weight_kg)
    if activity_level:
        user.activity_level = activity_level.lower()

    db.session.commit()

    bmr = CalorieService.calculate_bmr(user)
    tdee = CalorieService.calculate_tdee(user)

    return {
        "status": "success",
        "profile": user.to_dict(),
        "calculated_bmr": bmr,
        "calculated_tdee": tdee,
        "message": f"Profile updated! BMR is now {bmr} kcal and estimated TDEE is {tdee} kcal.",
    }
