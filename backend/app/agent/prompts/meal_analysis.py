MEAL_ANALYSIS_PROMPT = """Analyze the provided meal (from the image and/or text description).
Identify each constituent item, estimate realistic portion sizes, calories (kcal), protein (g), carbs (g), and fat (g).

Return a structured breakdown:
- meal_type: breakfast, lunch, dinner, or snack
- items: list of { name, quantity, unit, calories, protein_g, carbs_g, fat_g }
- confidence_note: brief note on portion assumptions
"""
