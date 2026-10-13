from typing import Dict, Any, List, Optional
from app.services.meal_service import MealService
from app.services.nutrition_lookup import lookup_food_nutrition
from app.agent.confirmations import ConfirmationManager
from app.schemas.tool_schemas import LogMealInput, EditMealInput, DeleteMealInput

def tool_analyze_meal(user_id: int, description: Optional[str] = None, image_id: Optional[str] = None) -> Dict[str, Any]:
    """Analyze a food item or meal from text description or image reference."""
    # Look up any mentioned foods to enhance accuracy
    breakdown = []
    if description:
        # Simple phrase scan against reference db
        words = description.split()
        for i in range(len(words)):
            phrase = " ".join(words[i:i+2])
            found = lookup_food_nutrition(phrase)
            if found:
                breakdown.append(found)

    return {
        "status": "success",
        "message": "Meal analyzed. You can now log this meal or adjust the ingredients.",
        "input_description": description,
        "image_id": image_id,
        "reference_matches": breakdown,
    }

def tool_log_meal(
    user_id: int,
    meal_type: str,
    items: List[Dict[str, Any]],
    notes: Optional[str] = None,
    image_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Log a meal and its itemized ingredients to the user's database."""
    # Validate with Pydantic
    validated = LogMealInput(meal_type=meal_type, items=items, notes=notes, image_id=image_id)
    
    meal = MealService.log_meal(
        user_id=user_id,
        meal_type=validated.meal_type,
        items=[it.model_dump() for it in validated.items],
        notes=validated.notes,
        image_id=validated.image_id,
    )

    return {
        "status": "success",
        "meal_id": meal.id,
        "meal_type": meal.meal_type,
        "total_calories": meal.total_calories,
        "total_protein_g": meal.total_protein_g,
        "total_carbs_g": meal.total_carbs_g,
        "total_fat_g": meal.total_fat_g,
        "items": [it.to_dict() for it in meal.items],
        "message": f"Successfully logged {meal.meal_type} with {meal.total_calories} kcal.",
    }

def tool_edit_meal(
    user_id: int,
    meal_id: int,
    meal_type: Optional[str] = None,
    items: Optional[List[Dict[str, Any]]] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Edit an existing logged meal."""
    meal = MealService.edit_meal(
        meal_id=meal_id,
        user_id=user_id,
        meal_type=meal_type,
        items=items,
        notes=notes,
    )
    if not meal:
        return {"status": "error", "message": f"Meal #{meal_id} not found or unauthorized."}

    return {
        "status": "success",
        "meal_id": meal.id,
        "meal_type": meal.meal_type,
        "total_calories": meal.total_calories,
        "message": f"Updated meal #{meal_id} ({meal.total_calories} kcal).",
    }

def tool_delete_meal(user_id: int, meal_id: int) -> Dict[str, Any]:
    """Request confirmation to delete a logged meal."""
    meal = MealService.get_meal(meal_id, user_id)
    if not meal:
        return {"status": "error", "message": f"Meal #{meal_id} was not found."}

    item_names = ", ".join(i.name for i in meal.items) if meal.items else "Meal"
    desc = f"Are you sure you want to delete {meal.meal_type} (#{meal.id}: {item_names} - {meal.total_calories} kcal)?"

    pending = ConfirmationManager.create_pending_action(
        tool_name="execute_delete_meal",
        tool_args={"meal_id": meal_id},
        description=desc,
    )

    return {
        "status": "pending_confirmation",
        "pending_action": pending,
        "message": desc,
    }

def execute_delete_meal(user_id: int, meal_id: int) -> Dict[str, Any]:
    """Actual execution of deletion after user confirmation."""
    success = MealService.delete_meal(meal_id, user_id)
    if success:
        return {"status": "success", "message": f"Meal #{meal_id} has been permanently deleted."}
    return {"status": "error", "message": f"Meal #{meal_id} could not be deleted."}
