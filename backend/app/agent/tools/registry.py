from typing import Dict, Any, Callable
from app.agent.tools.meal_tools import (
    tool_analyze_meal,
    tool_log_meal,
    tool_edit_meal,
    tool_delete_meal,
    execute_delete_meal,
)
from app.agent.tools.tracking_tools import (
    tool_get_daily_summary,
    tool_get_history,
    tool_get_weekly_report,
)
from app.agent.tools.goal_tools import tool_set_calorie_goal
from app.agent.tools.profile_tools import tool_get_profile, tool_update_profile
from app.agent.tools.diet_tools import tool_generate_diet_plan, tool_get_active_plan
from app.agent.tools.reminder_tools import tool_set_reminder, tool_list_reminders

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_meal",
            "description": "Analyze food description or photo to inspect ingredients and macronutrients before logging.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Text describing food consumed, e.g. '2 eggs, whole wheat toast with butter'",
                    },
                    "image_id": {
                        "type": "string",
                        "description": "Image ID of the uploaded food photo",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_meal",
            "description": "Log a meal with its itemized ingredients and macro values directly into the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "meal_type": {
                        "type": "string",
                        "enum": ["breakfast", "lunch", "dinner", "snack"],
                        "description": "Type of meal",
                    },
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Item name, e.g. 'Avocado Toast'"},
                                "quantity": {"type": "number", "description": "Portion quantity"},
                                "unit": {"type": "string", "description": "Portion unit, e.g. 'slice', 'cup', 'g'"},
                                "calories": {"type": "number", "description": "Calories in kcal"},
                                "protein_g": {"type": "number", "description": "Protein in grams"},
                                "carbs_g": {"type": "number", "description": "Carbs in grams"},
                                "fat_g": {"type": "number", "description": "Fat in grams"},
                            },
                            "required": ["name", "calories"],
                        },
                        "description": "List of foods in the meal",
                    },
                    "notes": {"type": "string", "description": "Optional user notes"},
                    "image_id": {"type": "string", "description": "Optional image id"},
                },
                "required": ["meal_type", "items"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_meal",
            "description": "Edit or update an existing meal record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "meal_id": {"type": "integer", "description": "Meal ID to edit"},
                    "meal_type": {"type": "string", "enum": ["breakfast", "lunch", "dinner", "snack"]},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "quantity": {"type": "number"},
                                "unit": {"type": "string"},
                                "calories": {"type": "number"},
                                "protein_g": {"type": "number"},
                                "carbs_g": {"type": "number"},
                                "fat_g": {"type": "number"},
                            },
                            "required": ["name", "calories"],
                        },
                    },
                    "notes": {"type": "string"},
                },
                "required": ["meal_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_meal",
            "description": "Request deletion of a logged meal. Prompts user confirmation before execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "meal_id": {"type": "integer", "description": "Meal ID to delete"},
                },
                "required": ["meal_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_summary",
            "description": "Get today's (or a specified date's) consumed calories, macros, and remaining allowance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format (defaults to today)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_history",
            "description": "Retrieve recent logged meals list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of meals to retrieve, default 10"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weekly_report",
            "description": "Get past 7 days average calories, trends, and adherence report.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_calorie_goal",
            "description": "Set the user's daily calorie target and optional macronutrient goals.",
            "parameters": {
                "type": "object",
                "properties": {
                    "calorie_target": {"type": "number", "description": "Target daily calories in kcal"},
                    "protein_g": {"type": "number", "description": "Target protein in grams"},
                    "carbs_g": {"type": "number", "description": "Target carbs in grams"},
                    "fat_g": {"type": "number", "description": "Target fat in grams"},
                },
                "required": ["calorie_target"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_profile",
            "description": "Retrieve user profile, biometrics, BMR, and TDEE.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_profile",
            "description": "Update user biometrics (age, gender, height, current weight, target weight, activity level).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "gender": {"type": "string", "enum": ["male", "female", "other"]},
                    "height_cm": {"type": "number"},
                    "current_weight_kg": {"type": "number"},
                    "target_weight_kg": {"type": "number"},
                    "activity_level": {
                        "type": "string",
                        "enum": ["sedentary", "light", "moderate", "active", "very_active"],
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_diet_plan",
            "description": "Generate and activate a structured nutrition meal plan based on calorie goal and preferences.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal_type": {
                        "type": "string",
                        "enum": ["weight_loss", "muscle_gain", "maintenance", "keto"],
                    },
                    "target_daily_calories": {"type": "number"},
                    "duration_weeks": {"type": "integer"},
                    "dietary_preferences": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_active_plan",
            "description": "Retrieve the user's active diet plan.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Set a daily reminder nudge to log meals.",
            "parameters": {
                "type": "object",
                "properties": {
                    "schedule_time": {"type": "string", "description": "Time format HH:MM, e.g. '20:00'"},
                    "text": {"type": "string", "description": "Reminder message"},
                },
                "required": ["schedule_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_reminders",
            "description": "List all scheduled reminders for the user.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

TOOL_DISPATCHER: Dict[str, Callable] = {
    "analyze_meal": tool_analyze_meal,
    "log_meal": tool_log_meal,
    "edit_meal": tool_edit_meal,
    "delete_meal": tool_delete_meal,
    "execute_delete_meal": execute_delete_meal,
    "get_daily_summary": tool_get_daily_summary,
    "get_history": tool_get_history,
    "get_weekly_report": tool_get_weekly_report,
    "set_calorie_goal": tool_set_calorie_goal,
    "get_profile": tool_get_profile,
    "update_profile": tool_update_profile,
    "generate_diet_plan": tool_generate_diet_plan,
    "get_active_plan": tool_get_active_plan,
    "set_reminder": tool_set_reminder,
    "list_reminders": tool_list_reminders,
}

def dispatch_tool_call(tool_name: str, user_id: int, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the tool function injecting the authenticated user_id server-side."""
    func = TOOL_DISPATCHER.get(tool_name)
    if not func:
        return {"status": "error", "message": f"Tool '{tool_name}' is not recognized."}

    # CRITICAL SECURITY RULE: inject user_id server-side; strip any user_id from arguments
    cleaned_args = dict(arguments)
    cleaned_args.pop("user_id", None)

    try:
        return func(user_id=user_id, **cleaned_args)
    except Exception as e:
        return {"status": "error", "message": f"Tool execution error: {str(e)}"}
