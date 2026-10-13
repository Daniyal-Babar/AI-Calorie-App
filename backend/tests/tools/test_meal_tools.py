from app.agent.tools.meal_tools import (
    tool_log_meal,
    tool_edit_meal,
    tool_delete_meal,
    execute_delete_meal,
    tool_analyze_meal,
)
from app.agent.tools.tracking_tools import tool_get_daily_summary, tool_get_weekly_report
from app.agent.tools.goal_tools import tool_set_calorie_goal

def test_meal_tools_flow(app, test_user):
    with app.app_context():
        # 1. Set goal
        goal_res = tool_set_calorie_goal(test_user, calorie_target=2200.0)
        assert goal_res["status"] == "success"
        assert goal_res["goal"]["calorie_target"] == 2200.0

        # 2. Log meal
        items = [
            {"name": "Oatmeal", "quantity": 1, "unit": "bowl", "calories": 250, "protein_g": 8, "carbs_g": 45, "fat_g": 4},
            {"name": "Boiled Eggs", "quantity": 2, "unit": "pieces", "calories": 156, "protein_g": 12, "carbs_g": 1, "fat_g": 10},
        ]
        log_res = tool_log_meal(test_user, meal_type="breakfast", items=items, notes="Pre-workout breakfast")
        assert log_res["status"] == "success"
        meal_id = log_res["meal_id"]
        assert log_res["total_calories"] == 406.0

        # 3. Check daily summary
        summary_res = tool_get_daily_summary(test_user)
        assert summary_res["status"] == "success"
        assert summary_res["summary"]["consumed"]["calories"] == 406.0
        assert summary_res["summary"]["remaining_calories"] == 1794.0

        # 4. Edit meal
        edit_res = tool_edit_meal(
            test_user,
            meal_id=meal_id,
            items=[{"name": "Large Oatmeal", "quantity": 1.5, "unit": "bowl", "calories": 375, "protein_g": 12, "carbs_g": 65, "fat_g": 6}],
        )
        assert edit_res["status"] == "success"
        assert edit_res["total_calories"] == 375.0

        # 5. Delete meal (should trigger confirmation)
        del_pending = tool_delete_meal(test_user, meal_id=meal_id)
        assert del_pending["status"] == "pending_confirmation"
        assert "pending_action" in del_pending

        # 6. Execute delete
        del_exec = execute_delete_meal(test_user, meal_id=meal_id)
        assert del_exec["status"] == "success"

        # 7. Verify deletion reflected in summary
        summary_after = tool_get_daily_summary(test_user)
        assert summary_after["summary"]["consumed"]["calories"] == 0.0
