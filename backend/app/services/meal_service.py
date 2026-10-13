from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.extensions import db
from app.models.meal import Meal, MealItem

class MealService:
    @staticmethod
    def log_meal(
        user_id: int,
        meal_type: str,
        items: List[Dict[str, Any]],
        notes: Optional[str] = None,
        image_id: Optional[str] = None,
    ) -> Meal:
        """Create a new meal and its constituent items for a user."""
        meal = Meal(
            user_id=user_id,
            meal_type=meal_type,
            notes=notes,
            image_path=image_id,
            logged_at=datetime.now(timezone.utc),
        )
        db.session.add(meal)
        db.session.flush()  # get meal.id

        for item_data in items:
            item = MealItem(
                meal_id=meal.id,
                name=item_data["name"],
                quantity=float(item_data.get("quantity", 1.0)),
                unit=item_data.get("unit", "serving"),
                calories=float(item_data["calories"]),
                protein_g=float(item_data.get("protein_g", 0.0)),
                carbs_g=float(item_data.get("carbs_g", 0.0)),
                fat_g=float(item_data.get("fat_g", 0.0)),
            )
            db.session.add(item)

        db.session.commit()
        return meal

    @staticmethod
    def get_meal(meal_id: int, user_id: int) -> Optional[Meal]:
        """Retrieve a specific meal ensuring user ownership."""
        return Meal.query.filter_by(id=meal_id, user_id=user_id).first()

    @staticmethod
    def edit_meal(
        meal_id: int,
        user_id: int,
        meal_type: Optional[str] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        notes: Optional[str] = None,
    ) -> Optional[Meal]:
        """Edit an existing meal and optionally replace its items."""
        meal = MealService.get_meal(meal_id, user_id)
        if not meal:
            return None

        if meal_type:
            meal.meal_type = meal_type
        if notes is not None:
            meal.notes = notes

        if items is not None:
            # Delete existing items and add new ones
            for old_item in meal.items:
                db.session.delete(old_item)
            db.session.flush()

            for item_data in items:
                new_item = MealItem(
                    meal_id=meal.id,
                    name=item_data["name"],
                    quantity=float(item_data.get("quantity", 1.0)),
                    unit=item_data.get("unit", "serving"),
                    calories=float(item_data["calories"]),
                    protein_g=float(item_data.get("protein_g", 0.0)),
                    carbs_g=float(item_data.get("carbs_g", 0.0)),
                    fat_g=float(item_data.get("fat_g", 0.0)),
                )
                db.session.add(new_item)

        db.session.commit()
        return meal

    @staticmethod
    def delete_meal(meal_id: int, user_id: int) -> bool:
        """Delete a meal belonging to the user."""
        meal = MealService.get_meal(meal_id, user_id)
        if not meal:
            return False

        db.session.delete(meal)
        db.session.commit()
        return True

    @staticmethod
    def get_recent_meals(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch the most recent meals for the user."""
        meals = (
            Meal.query.filter_by(user_id=user_id)
            .order_by(Meal.logged_at.desc())
            .limit(limit)
            .all()
        )
        return [m.to_dict() for m in meals]
