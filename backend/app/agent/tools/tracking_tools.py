from datetime import datetime
from typing import Dict, Any, Optional
from app.services.calorie_service import CalorieService
from app.services.meal_service import MealService

def tool_get_daily_summary(user_id: int, date: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve consumed calories, macronutrients, and active goals for a given date."""
    target_date = None
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            target_date = None

    summary = CalorieService.get_daily_summary(user_id, target_date)
    return {
        "status": "success",
        "summary": summary,
        "message": f"Summary for {summary['date']}: Consumed {summary['consumed']['calories']} / {summary['targets']['calories']} kcal.",
    }

def tool_get_history(user_id: int, limit: int = 10) -> Dict[str, Any]:
    """Retrieve recent meal log history."""
    meals = MealService.get_recent_meals(user_id, limit=limit)
    return {
        "status": "success",
        "count": len(meals),
        "meals": meals,
    }

def tool_get_weekly_report(user_id: int) -> Dict[str, Any]:
    """Retrieve 7-day intake analytics and trends."""
    report = CalorieService.get_weekly_report(user_id)
    return {
        "status": "success",
        "report": report,
        "message": f"Weekly average: {report['average_daily_calories']} kcal/day over {report['days_logged']} logged days.",
    }
