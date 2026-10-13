from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class MealItemInput(BaseModel):
    name: str = Field(..., description="Name of the food item, e.g. 'Grilled Chicken Breast'")
    quantity: float = Field(1.0, description="Amount/portion size")
    unit: str = Field("serving", description="Unit, e.g. 'g', 'cup', 'slice', 'serving'")
    calories: float = Field(..., description="Calories in kcal")
    protein_g: float = Field(0.0, description="Protein in grams")
    carbs_g: float = Field(0.0, description="Carbohydrates in grams")
    fat_g: float = Field(0.0, description="Fat in grams")

class LogMealInput(BaseModel):
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"] = Field(
        "lunch", description="Type of meal: breakfast, lunch, dinner, or snack"
    )
    items: List[MealItemInput] = Field(..., min_length=1, description="List of items in the meal")
    notes: Optional[str] = Field(None, description="Optional notes or details")
    image_id: Optional[str] = Field(None, description="Optional image_id associated with this meal")

class AnalyzeMealInput(BaseModel):
    description: Optional[str] = Field(None, description="Textual description of the food/meal eaten")
    image_id: Optional[str] = Field(None, description="Image ID of the uploaded meal photo")

class EditMealInput(BaseModel):
    meal_id: int = Field(..., description="The ID of the meal to update")
    meal_type: Optional[Literal["breakfast", "lunch", "dinner", "snack"]] = None
    items: Optional[List[MealItemInput]] = None
    notes: Optional[str] = None

class DeleteMealInput(BaseModel):
    meal_id: int = Field(..., description="The ID of the meal to delete")

class SetCalorieGoalInput(BaseModel):
    calorie_target: float = Field(..., ge=800, le=8000, description="Daily calorie target in kcal")
    protein_g: Optional[float] = Field(None, ge=10, le=500, description="Target protein in grams")
    carbs_g: Optional[float] = Field(None, ge=10, le=800, description="Target carbs in grams")
    fat_g: Optional[float] = Field(None, ge=5, le=300, description="Target fat in grams")

class UpdateProfileInput(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=12, le=110, description="Age in years")
    gender: Optional[str] = Field(None, description="Gender: male, female, other")
    height_cm: Optional[float] = Field(None, ge=60, le=260, description="Height in cm")
    current_weight_kg: Optional[float] = Field(None, ge=25, le=350, description="Current body weight in kg")
    target_weight_kg: Optional[float] = Field(None, ge=25, le=350, description="Goal body weight in kg")
    activity_level: Optional[Literal["sedentary", "light", "moderate", "active", "very_active"]] = Field(
        None, description="Daily activity level"
    )

class GenerateDietPlanInput(BaseModel):
    goal_type: Literal["weight_loss", "muscle_gain", "maintenance", "keto"] = Field(
        "weight_loss", description="Fitness / diet goal type"
    )
    target_daily_calories: Optional[float] = Field(None, ge=1000, le=6000, description="Custom target calories if specified")
    duration_weeks: Optional[int] = Field(4, ge=1, le=24, description="Duration in weeks")
    dietary_preferences: Optional[str] = Field(None, description="E.g., high protein, vegetarian, vegan, low-carb")

class SetReminderInput(BaseModel):
    schedule_time: str = Field(..., description="Time of day for the reminder (e.g. '08:00', '13:00', '20:00')")
    text: str = Field("Time to log your meal!", description="Reminder text / nudge")

class GetDailySummaryInput(BaseModel):
    date: Optional[str] = Field(None, description="Optional date in YYYY-MM-DD format (defaults to today)")
