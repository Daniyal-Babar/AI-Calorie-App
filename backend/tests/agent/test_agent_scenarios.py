import json
import pytest
from unittest.mock import MagicMock, patch
from app.extensions import db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.meal import Meal, MealItem
from app.agent.orchestrator import AgentOrchestrator
from app.agent.llm_client import LLMResponse
from app.agent.tools.registry import dispatch_tool_call
from app.services.meal_service import MealService
from app.services.upload_service import UploadService

def parse_sse_events(generator):
    events = []
    for chunk in generator:
        for line in chunk.split("\n\n"):
            line = line.strip()
            if line.startswith("data: "):
                try:
                    payload = json.loads(line[6:].strip())
                    events.append(payload)
                except Exception:
                    pass
    return events

def make_turn_mock(tool_calls, final_text="Operation completed."):
    """Returns a mock create_chat_completion side-effect that emits tool_calls on turn 1
    and completes with final_text on turn 2 once tools have returned.
    """
    def _side_effect(messages, tools=None):
        if not tools or any(m.get("role") == "tool" for m in messages):
            return LLMResponse(content=final_text, tool_calls=[])
        return LLMResponse(content=None, tool_calls=tool_calls)
    return _side_effect

# 1. User asks how many calories are in an apple
def test_scenario_01_calories_in_apple(app, test_user):
    with app.app_context():
        user = db.session.get(User, test_user)
        orchestrator = AgentOrchestrator(user=user)

        mock_tool_call = {
            "id": "call_apple_01",
            "type": "function",
            "function": {
                "name": "analyze_meal",
                "arguments": json.dumps({"description": "apple"}),
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=make_turn_mock([mock_tool_call], "A medium apple has approximately 95 calories.")), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "A medium apple has approximately 95 calories."}])):

            events = parse_sse_events(orchestrator.process_message_stream("How many calories are in an apple?"))

        # Verify tool was called
        tool_call_events = [e for e in events if e.get("event") == "tool_call"]
        assert len(tool_call_events) == 1
        assert tool_call_events[0]["tool"] == "analyze_meal"

        # Verify NO meal was logged to database
        assert Meal.query.filter_by(user_id=test_user).count() == 0

        # Verify final message
        done_events = [e for e in events if e.get("event") == "done"]
        assert len(done_events) == 1
        assert "apple" in done_events[0]["message"]["content"].lower()

# 2. User says they ate two eggs
def test_scenario_02_user_ate_two_eggs(app, test_user):
    with app.app_context():
        user = db.session.get(User, test_user)
        orchestrator = AgentOrchestrator(user=user)

        mock_tool_call = {
            "id": "call_eggs_02",
            "type": "function",
            "function": {
                "name": "log_meal",
                "arguments": json.dumps({
                    "meal_type": "breakfast",
                    "items": [
                        {"name": "Boiled Eggs", "quantity": 2, "unit": "large eggs", "calories": 156, "protein_g": 12.6, "carbs_g": 1.2, "fat_g": 10.6}
                    ],
                }),
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=make_turn_mock([mock_tool_call], "Logged 2 boiled eggs (156 kcal).")), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "Logged 2 boiled eggs (156 kcal)."}])):

            events = parse_sse_events(orchestrator.process_message_stream("I ate two eggs for breakfast"))

        # Verify meal was saved to DB
        meals = Meal.query.filter_by(user_id=test_user).all()
        assert len(meals) == 1
        assert meals[0].meal_type == "breakfast"
        assert meals[0].total_calories == 156.0

# 3. User explicitly asks to log two eggs
def test_scenario_03_explicit_log_two_eggs(app, test_user):
    with app.app_context():
        user = db.session.get(User, test_user)
        orchestrator = AgentOrchestrator(user=user)

        mock_tool_call = {
            "id": "call_log_03",
            "type": "function",
            "function": {
                "name": "log_meal",
                "arguments": json.dumps({
                    "meal_type": "breakfast",
                    "items": [
                        {"name": "Eggs", "quantity": 2, "unit": "large", "calories": 156, "protein_g": 12.6, "carbs_g": 1.2, "fat_g": 10.6}
                    ],
                }),
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=make_turn_mock([mock_tool_call], "Logged 2 eggs for breakfast.")), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "Logged 2 eggs for breakfast."}])):

            events = parse_sse_events(orchestrator.process_message_stream("Please log two eggs for breakfast"))

        # Verify meal card in blocks
        done_event = next(e for e in events if e.get("event") == "done")
        block_types = [b.get("type") for b in done_event.get("blocks", [])]
        assert "meal_card" in block_types

# 4. User uploads a food image without text
def test_scenario_04_image_upload_without_text(app, test_user, tmp_path):
    with app.app_context():
        app.config["UPLOAD_FOLDER"] = str(tmp_path)
        # Create an owned image file
        img_id = "img_food_04"
        img_file = tmp_path / f"{img_id}_{test_user}.jpg"
        img_file.write_text("dummy image data")

        user = db.session.get(User, test_user)
        orchestrator = AgentOrchestrator(user=user)

        mock_tool_call = {
            "id": "call_img_04",
            "type": "function",
            "function": {
                "name": "analyze_meal",
                "arguments": json.dumps({"image_id": img_id}),
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=make_turn_mock([mock_tool_call], "I analyzed your uploaded photo.")), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "I analyzed your uploaded photo."}])):

            events = parse_sse_events(orchestrator.process_message_stream("", image_id=img_id))

        assert not any(e.get("event") == "error" for e in events)
        tool_calls = [e for e in events if e.get("event") == "tool_call"]
        assert len(tool_calls) == 1
        assert tool_calls[0]["tool"] == "analyze_meal"

# 5. User asks for today's calorie summary
def test_scenario_05_daily_summary(app, test_user):
    with app.app_context():
        user = db.session.get(User, test_user)
        # Pre-log a meal
        MealService.log_meal(test_user, "lunch", [{"name": "Salad", "quantity": 1, "unit": "bowl", "calories": 200, "protein_g": 5, "carbs_g": 10, "fat_g": 5}])

        orchestrator = AgentOrchestrator(user=user)
        mock_tool_call = {
            "id": "call_sum_05",
            "type": "function",
            "function": {
                "name": "get_daily_summary",
                "arguments": "{}",
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=make_turn_mock([mock_tool_call], "Today you consumed 200 kcal.")), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "Today you consumed 200 kcal."}])):

            events = parse_sse_events(orchestrator.process_message_stream("What is my calorie summary for today?"))

        done_event = next(e for e in events if e.get("event") == "done")
        block_types = [b.get("type") for b in done_event.get("blocks", [])]
        assert "daily_summary_card" in block_types

# 6. User asks for their weekly nutrition report
def test_scenario_06_weekly_report(app, test_user):
    with app.app_context():
        user = db.session.get(User, test_user)
        orchestrator = AgentOrchestrator(user=user)

        mock_tool_call = {
            "id": "call_week_06",
            "type": "function",
            "function": {
                "name": "get_weekly_report",
                "arguments": "{}",
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=make_turn_mock([mock_tool_call], "Here is your 7-day intake report.")), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "Here is your 7-day intake report."}])):

            events = parse_sse_events(orchestrator.process_message_stream("Can I see my weekly nutrition report?"))

        tool_results = [e for e in events if e.get("event") == "tool_result"]
        assert len(tool_results) == 1
        assert "average_daily_calories" in tool_results[0]["result"]["report"]

# 7. User asks to edit a previously logged meal
def test_scenario_07_edit_meal(app, test_user):
    with app.app_context():
        meal = MealService.log_meal(test_user, "breakfast", [{"name": "Toast", "quantity": 1, "unit": "slice", "calories": 80, "protein_g": 3, "carbs_g": 15, "fat_g": 1}])
        user = db.session.get(User, test_user)
        orchestrator = AgentOrchestrator(user=user)

        mock_tool_call = {
            "id": "call_edit_07",
            "type": "function",
            "function": {
                "name": "edit_meal",
                "arguments": json.dumps({
                    "meal_id": meal.id,
                    "items": [{"name": "Toast with Jam", "quantity": 2, "unit": "slices", "calories": 200, "protein_g": 4, "carbs_g": 35, "fat_g": 2}],
                }),
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=make_turn_mock([mock_tool_call], "Updated your breakfast toast.")), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "Updated your breakfast toast."}])):

            events = parse_sse_events(orchestrator.process_message_stream(f"Edit meal #{meal.id} to 2 slices of toast with jam"))

        updated_meal = MealService.get_meal(meal.id, test_user)
        assert updated_meal.total_calories == 200.0

# 8. User asks to delete a meal
def test_scenario_08_delete_meal_requires_confirmation(app, test_user):
    with app.app_context():
        meal = MealService.log_meal(test_user, "dinner", [{"name": "Steak", "quantity": 1, "unit": "serving", "calories": 500, "protein_g": 50, "carbs_g": 0, "fat_g": 30}])
        user = db.session.get(User, test_user)
        orchestrator = AgentOrchestrator(user=user)

        mock_tool_call = {
            "id": "call_del_08",
            "type": "function",
            "function": {
                "name": "delete_meal",
                "arguments": json.dumps({"meal_id": meal.id}),
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=make_turn_mock([mock_tool_call], "Please confirm if you want to delete this meal.")), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "Please confirm if you want to delete this meal."}])):

            events = parse_sse_events(orchestrator.process_message_stream(f"Delete meal #{meal.id}"))

        # Verify meal is NOT deleted yet
        assert MealService.get_meal(meal.id, test_user) is not None

        # Verify confirmation block was generated
        done_event = next(e for e in events if e.get("event") == "done")
        block_types = [b.get("type") for b in done_event.get("blocks", [])]
        assert "actions" in block_types

# 9. User asks to change their calorie goal
def test_scenario_09_change_calorie_goal(app, test_user):
    with app.app_context():
        user = db.session.get(User, test_user)
        orchestrator = AgentOrchestrator(user=user)

        mock_tool_call = {
            "id": "call_goal_09",
            "type": "function",
            "function": {
                "name": "set_calorie_goal",
                "arguments": json.dumps({"calorie_target": 2300, "protein_g": 160}),
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=make_turn_mock([mock_tool_call], "Your new calorie goal is 2300 kcal.")), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "Your new calorie goal is 2300 kcal."}])):

            events = parse_sse_events(orchestrator.process_message_stream("Set my calorie goal to 2300 kcal with 160g protein"))

        summary = dispatch_tool_call("get_daily_summary", test_user, {})
        assert summary["summary"]["targets"]["calories"] == 2300.0
        assert summary["summary"]["targets"]["protein_g"] == 160.0

# 10. User requests a personalized diet plan with incomplete profile information
def test_scenario_10_diet_plan_incomplete_profile(app):
    with app.app_context():
        # Create user missing height and weight
        incomplete_user = User(email="incomplete@example.com", name="Sam")
        incomplete_user.set_password("pass123")
        db.session.add(incomplete_user)
        db.session.commit()

        orchestrator = AgentOrchestrator(user=incomplete_user)
        mock_tool_call = {
            "id": "call_plan_10",
            "type": "function",
            "function": {
                "name": "generate_diet_plan",
                "arguments": json.dumps({"goal_type": "weight_loss"}),
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=make_turn_mock([mock_tool_call], "I created your plan. Please update your profile for more precision.")), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "I created your plan. Please update your profile for more precision."}])):

            events = parse_sse_events(orchestrator.process_message_stream("Generate a weight loss diet plan for me"))

        tool_result = next(e for e in events if e.get("event") == "tool_result")
        assert tool_result["result"]["status"] == "success"
        assert len(tool_result["result"]["missing_profile_fields"]) > 0

# 11. Ollama returns malformed tool arguments
def test_scenario_11_malformed_tool_arguments(app, test_user):
    with app.app_context():
        user = db.session.get(User, test_user)
        orchestrator = AgentOrchestrator(user=user)

        # Malformed JSON in arguments
        bad_tool_call = {
            "id": "call_bad_11",
            "type": "function",
            "function": {
                "name": "log_meal",
                "arguments": '{"meal_type": "lunch", "items": [{"name": broken',
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=make_turn_mock([bad_tool_call], "There was an error reading the meal details.")), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "There was an error reading the meal details."}])):

            events = parse_sse_events(orchestrator.process_message_stream("Log my lunch"))

        # Verify tool result returned error rather than crashing or running empty dict
        tool_result = next(e for e in events if e.get("event") == "tool_result")
        assert tool_result["result"]["status"] == "error"
        assert "malformed" in tool_result["result"]["message"].lower()

# 12. Ollama is unavailable
def test_scenario_12_ollama_unavailable(app, test_user):
    with app.app_context():
        user = db.session.get(User, test_user)
        orchestrator = AgentOrchestrator(user=user)

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=Exception("Failed to connect to Ollama service")):
            events = parse_sse_events(orchestrator.process_message_stream("Hello coach"))

        error_event = next(e for e in events if e.get("event") == "error")
        assert "Failed to connect to Ollama service" in error_event["error"]

# 13. A backend tool raises an exception
def test_scenario_13_tool_raises_exception(app, test_user):
    with app.app_context():
        user = db.session.get(User, test_user)
        orchestrator = AgentOrchestrator(user=user)

        mock_tool_call = {
            "id": "call_exc_13",
            "type": "function",
            "function": {
                "name": "log_meal",
                "arguments": json.dumps({"meal_type": "lunch", "items": [{"name": "Rice", "calories": 200}]}),
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", side_effect=make_turn_mock([mock_tool_call])), \
             patch("app.agent.orchestrator.dispatch_tool_call", side_effect=RuntimeError("Database lock timeout")), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "Database error occurred."}])):

            events = parse_sse_events(orchestrator.process_message_stream("Log rice"))

        # Verify stream captured exception gracefully
        error_events = [e for e in events if e.get("event") == "error"]
        assert len(error_events) == 1
        assert "Database lock timeout" in error_events[0]["error"]

# 14. The agent reaches its maximum tool iteration limit
def test_scenario_14_max_iteration_limit(app, test_user):
    with app.app_context():
        user = db.session.get(User, test_user)
        orchestrator = AgentOrchestrator(user=user)
        orchestrator.max_iterations = 2

        infinite_tool_call = {
            "id": "call_inf",
            "type": "function",
            "function": {
                "name": "get_daily_summary",
                "arguments": "{}",
            },
        }

        with patch.object(orchestrator.llm, "create_chat_completion", return_value=LLMResponse(content=None, tool_calls=[infinite_tool_call])), \
             patch.object(orchestrator.llm, "stream_chat_completion", return_value=iter([{"type": "content_delta", "content": "Step limit reached."}])):

            events = parse_sse_events(orchestrator.process_message_stream("Keep thinking"))

        status_events = [e for e in events if e.get("event") == "status"]
        assert len(status_events) == 2  # exactly max_iterations
        assert status_events[-1]["iteration"] == 2

# 15. A user attempts to access another user's meal record or conversation
def test_scenario_15_unauthorized_access(app, test_user):
    with app.app_context():
        # User 1 creates a meal
        meal = MealService.log_meal(test_user, "dinner", [{"name": "Pizza", "quantity": 2, "unit": "slices", "calories": 600, "protein_g": 24, "carbs_g": 72, "fat_g": 20}])
        
        # User 2
        user2 = User(email="user2@example.com", name="Bob")
        user2.set_password("pass123")
        db.session.add(user2)
        db.session.commit()

        # User 2 tries to delete User 1's meal
        del_res = dispatch_tool_call("delete_meal", user_id=user2.id, arguments={"meal_id": meal.id})
        assert del_res["status"] == "error"
        assert "unauthorized" in del_res["message"].lower() or "not found" in del_res["message"].lower()

        # User 2 tries to edit User 1's meal
        edit_res = dispatch_tool_call("edit_meal", user_id=user2.id, arguments={"meal_id": meal.id, "meal_type": "lunch"})
        assert edit_res["status"] == "error"
        assert "unauthorized" in edit_res["message"].lower() or "not found" in edit_res["message"].lower()

        # User 1's meal remains unchanged
        unchanged = MealService.get_meal(meal.id, test_user)
        assert unchanged.meal_type == "dinner"
        assert unchanged.total_calories == 600.0

        # Conversation ownership check
        conv1 = Conversation(user_id=test_user, title="User 1 Conv")
        db.session.add(conv1)
        db.session.commit()

        with pytest.raises(ValueError, match="Unauthorized conversation access"):
            AgentOrchestrator(user=user2, conversation=conv1)
