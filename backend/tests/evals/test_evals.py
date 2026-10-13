from app.models.user import User
from app.agent.llm_client import LLMClient

EVAL_CASES = [
    {
        "prompt": "How many calories have I eaten today?",
        "expected_tool": "get_daily_summary",
    },
    {
        "prompt": "Delete meal #5",
        "expected_tool": "delete_meal",
    },
    {
        "prompt": "Set my goal to 1800 kcal",
        "expected_tool": "set_calorie_goal",
    },
    {
        "prompt": "I weigh 72 kg now",
        "expected_tool": "update_profile",
    },
    {
        "prompt": "Make me a weight loss diet plan",
        "expected_tool": ["generate_diet_plan", "get_profile"],
    },
]

from app.agent.tools.registry import TOOL_DEFINITIONS

def test_eval_sample_prompts(app):
    client = LLMClient()
    for case in EVAL_CASES:
        messages = [{"role": "user", "content": case["prompt"]}]
        resp = client.create_chat_completion(messages, tools=TOOL_DEFINITIONS)
        
        called_names = [tc["function"]["name"] for tc in resp.tool_calls]
        expected = case["expected_tool"] if isinstance(case["expected_tool"], list) else [case["expected_tool"]]
        assert any(exp in called_names for exp in expected), (
            f"Prompt '{case['prompt']}' expected tool in '{expected}', got '{called_names}'"
        )
