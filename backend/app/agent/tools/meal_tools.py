import re
from typing import Dict, Any, List, Optional
from app.services.meal_service import MealService
from app.services.nutrition_lookup import lookup_food_nutrition
from app.services.upload_service import UploadService
from app.agent.confirmations import ConfirmationManager
from app.schemas.tool_schemas import LogMealInput, EditMealInput, DeleteMealInput

def tool_analyze_meal(user_id: int, description: Optional[str] = None, image_id: Optional[str] = None) -> Dict[str, Any]:
    """Analyze a food item or meal from text description or image reference."""
    clean_desc = (description or "").strip()
    clean_img = (image_id or "").strip()

    if not clean_desc and not clean_img:
        return {
            "status": "error",
            "message": "Please provide a food description or an image reference to analyze.",
        }

    # Validate image ownership if image_id provided
    if clean_img:
        img_path = UploadService.get_file_path(clean_img, user_id=user_id)
        if not img_path:
            return {
                "status": "error",
                "message": f"Image '{clean_img}' not found or unauthorized.",
            }

    # Extract food items and check nutritional database
    breakdown = []
    items = []
    total_cals = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0

    if clean_desc:
        # Normalize punctuation and scan 1-word, 2-word, and 3-word n-grams
        cleaned_text = re.sub(r"[^\w\s]", " ", clean_desc.lower())
        words = cleaned_text.split()
        matched_keys = set()

        for n in (3, 2, 1):
            for i in range(len(words) - n + 1):
                phrase = " ".join(words[i : i + n])
                found = lookup_food_nutrition(phrase)
                if found and found["name"] not in matched_keys:
                    matched_keys.add(found["name"])
                    breakdown.append(found)

        # Estimate item quantities from description (e.g. "2 eggs" or "1 boiled egg")
        for match in breakdown:
            name = match.get("name", "Food item").title()
            cal = float(match.get("calories", 0.0))
            protein = float(match.get("protein_g", 0.0))
            carbs = float(match.get("carbs_g", 0.0))
            fat = float(match.get("fat_g", 0.0))
            unit = match.get("unit", "serving")

            # Check for quantity prefix before this food name
            qty = 1.0
            num_match = re.search(r"\b(\d+(?:\.\d+)?)\s*" + re.escape(match.get("name", "").lower()), clean_desc.lower())
            if num_match:
                try:
                    qty = float(num_match.group(1))
                except Exception:
                    qty = 1.0

            item_cals = round(cal * qty, 1)
            item_protein = round(protein * qty, 1)
            item_carbs = round(carbs * qty, 1)
            item_fat = round(fat * qty, 1)

            items.append({
                "name": name,
                "quantity": qty,
                "unit": unit,
                "calories": item_cals,
                "protein_g": item_protein,
                "carbs_g": item_carbs,
                "fat_g": item_fat,
            })
            total_cals += item_cals
            total_protein += item_protein
            total_carbs += item_carbs
            total_fat += item_fat

    return {
        "status": "success",
        "message": f"Meal analyzed: estimated {total_cals} kcal across {len(items)} identified food items.",
        "input_description": clean_desc or None,
        "image_id": clean_img or None,
        "items": items,
        "total_calories": round(total_cals, 1),
        "total_protein_g": round(total_protein, 1),
        "total_carbs_g": round(total_carbs, 1),
        "total_fat_g": round(total_fat, 1),
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
    if not items:
        return {"status": "error", "message": "Cannot log a meal without food items."}

    # Validate image ownership if provided
    if image_id:
        img_path = UploadService.get_file_path(image_id, user_id=user_id)
        if not img_path:
            return {"status": "error", "message": f"Image '{image_id}' not found or unauthorized."}

    # Validate with Pydantic
    try:
        validated = LogMealInput(meal_type=meal_type, items=items, notes=notes, image_id=image_id)
    except Exception as e:
        return {"status": "error", "message": f"Invalid meal input: {str(e)}"}

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
        "message": f"Successfully logged {meal.meal_type} (#{meal.id}) with {meal.total_calories} kcal.",
    }

def tool_edit_meal(
    user_id: int,
    meal_id: int,
    meal_type: Optional[str] = None,
    items: Optional[List[Dict[str, Any]]] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Edit an existing logged meal."""
    try:
        EditMealInput(meal_id=meal_id, meal_type=meal_type, items=items, notes=notes)
    except Exception as e:
        return {"status": "error", "message": f"Invalid edit input: {str(e)}"}

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
        "total_protein_g": meal.total_protein_g,
        "total_carbs_g": meal.total_carbs_g,
        "total_fat_g": meal.total_fat_g,
        "items": [it.to_dict() for it in meal.items],
        "message": f"Updated meal #{meal_id} ({meal.total_calories} kcal).",
    }

def tool_delete_meal(user_id: int, meal_id: int) -> Dict[str, Any]:
    """Request confirmation to delete a logged meal."""
    meal = MealService.get_meal(meal_id, user_id)
    if not meal:
        return {"status": "error", "message": f"Meal #{meal_id} was not found or unauthorized."}

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
    return {"status": "error", "message": f"Meal #{meal_id} could not be deleted or unauthorized."}
