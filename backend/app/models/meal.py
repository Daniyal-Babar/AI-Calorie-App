from datetime import datetime, timezone
from app.extensions import db

class Meal(db.Model):
    __tablename__ = "meals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    meal_type = db.Column(db.String(50), nullable=False, default="lunch")  # breakfast, lunch, dinner, snack
    logged_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    notes = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    items = db.relationship("MealItem", backref="meal", lazy="joined", cascade="all, delete-orphan")

    @property
    def total_calories(self) -> float:
        return round(sum(item.calories or 0.0 for item in self.items), 1)

    @property
    def total_protein_g(self) -> float:
        return round(sum(item.protein_g or 0.0 for item in self.items), 1)

    @property
    def total_carbs_g(self) -> float:
        return round(sum(item.carbs_g or 0.0 for item in self.items), 1)

    @property
    def total_fat_g(self) -> float:
        return round(sum(item.fat_g or 0.0 for item in self.items), 1)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "meal_type": self.meal_type,
            "logged_at": self.logged_at.isoformat() if self.logged_at else None,
            "notes": self.notes,
            "image_path": self.image_path,
            "total_calories": self.total_calories,
            "total_protein_g": self.total_protein_g,
            "total_carbs_g": self.total_carbs_g,
            "total_fat_g": self.total_fat_g,
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MealItem(db.Model):
    __tablename__ = "meal_items"

    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey("meals.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Float, default=1.0)
    unit = db.Column(db.String(30), default="serving")
    calories = db.Column(db.Float, nullable=False, default=0.0)
    protein_g = db.Column(db.Float, default=0.0)
    carbs_g = db.Column(db.Float, default=0.0)
    fat_g = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {
            "id": self.id,
            "meal_id": self.meal_id,
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "calories": self.calories,
            "protein_g": self.protein_g,
            "carbs_g": self.carbs_g,
            "fat_g": self.fat_g,
        }
