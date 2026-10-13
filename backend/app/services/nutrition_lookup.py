import re
from typing import Optional, Dict

# Reference database of common foods with typical macronutrients per 100g or typical serving
FOOD_NUTRITION_DB = {
    "egg": {"calories": 78, "protein_g": 6.3, "carbs_g": 0.6, "fat_g": 5.3, "unit": "large egg"},
    "boiled egg": {"calories": 78, "protein_g": 6.3, "carbs_g": 0.6, "fat_g": 5.3, "unit": "large egg"},
    "chicken breast": {"calories": 165, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6, "unit": "100g"},
    "grilled chicken": {"calories": 165, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6, "unit": "100g"},
    "rice": {"calories": 130, "protein_g": 2.7, "carbs_g": 28.0, "fat_g": 0.3, "unit": "100g cooked"},
    "white rice": {"calories": 130, "protein_g": 2.7, "carbs_g": 28.0, "fat_g": 0.3, "unit": "100g cooked"},
    "brown rice": {"calories": 111, "protein_g": 2.6, "carbs_g": 23.0, "fat_g": 0.9, "unit": "100g cooked"},
    "oatmeal": {"calories": 150, "protein_g": 5.0, "carbs_g": 27.0, "fat_g": 2.5, "unit": "1 cup cooked"},
    "banana": {"calories": 105, "protein_g": 1.3, "carbs_g": 27.0, "fat_g": 0.3, "unit": "medium (118g)"},
    "apple": {"calories": 95, "protein_g": 0.5, "carbs_g": 25.0, "fat_g": 0.3, "unit": "medium"},
    "salmon": {"calories": 208, "protein_g": 20.0, "carbs_g": 0.0, "fat_g": 13.0, "unit": "100g"},
    "avocado": {"calories": 160, "protein_g": 2.0, "carbs_g": 8.5, "fat_g": 14.7, "unit": "100g"},
    "olive oil": {"calories": 119, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 13.5, "unit": "1 tbsp (14g)"},
    "milk": {"calories": 122, "protein_g": 8.0, "carbs_g": 12.0, "fat_g": 4.8, "unit": "1 cup (240ml)"},
    "greek yogurt": {"calories": 100, "protein_g": 17.0, "carbs_g": 6.0, "fat_g": 0.7, "unit": "170g"},
    "almonds": {"calories": 164, "protein_g": 6.0, "carbs_g": 6.1, "fat_g": 14.2, "unit": "1 oz (28g)"},
    "peanut butter": {"calories": 188, "protein_g": 8.0, "carbs_g": 7.0, "fat_g": 16.0, "unit": "2 tbsp (32g)"},
    "bread": {"calories": 79, "protein_g": 2.7, "carbs_g": 15.0, "fat_g": 1.0, "unit": "1 slice"},
    "whole wheat bread": {"calories": 81, "protein_g": 4.0, "carbs_g": 13.8, "fat_g": 1.1, "unit": "1 slice"},
    "pasta": {"calories": 158, "protein_g": 5.8, "carbs_g": 31.0, "fat_g": 0.9, "unit": "100g cooked"},
    "salad": {"calories": 35, "protein_g": 1.5, "carbs_g": 7.0, "fat_g": 0.5, "unit": "1 bowl mixed greens"},
    "pizza": {"calories": 285, "protein_g": 12.0, "carbs_g": 36.0, "fat_g": 10.4, "unit": "1 slice (107g)"},
    "burger": {"calories": 540, "protein_g": 28.0, "carbs_g": 40.0, "fat_g": 27.0, "unit": "1 hamburger"},
    "french fries": {"calories": 365, "protein_g": 4.0, "carbs_g": 48.0, "fat_g": 17.0, "unit": "medium serving"},
}

def lookup_food_nutrition(food_name: str) -> Optional[Dict[str, any]]:
    """Look up nutrition information for a food item by fuzzy name matching."""
    cleaned = food_name.strip().lower()
    
    # Direct match
    if cleaned in FOOD_NUTRITION_DB:
        return {"name": food_name, **FOOD_NUTRITION_DB[cleaned]}
    
    # Substring match
    for key, data in FOOD_NUTRITION_DB.items():
        if key in cleaned or cleaned in key:
            return {"name": food_name, **data}
            
    return None
