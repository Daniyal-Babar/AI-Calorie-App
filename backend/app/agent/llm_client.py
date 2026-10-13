import json
import logging
from typing import List, Dict, Any, Generator, Optional
from flask import current_app

logger = logging.getLogger(__name__)

class LLMResponse:
    def __init__(self, content: Optional[str] = None, tool_calls: Optional[List[Dict[str, Any]]] = None):
        self.content = content
        self.tool_calls = tool_calls or []

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = (
            api_key
            or current_app.config.get("GEMINI_API_KEY", "")
            or current_app.config.get("OPENAI_API_KEY", "")
        )
        self.base_url = base_url or current_app.config.get(
            "GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = model or current_app.config.get("GEMINI_MODEL", "gemini-flash-lite-latest")
        self._client = None

        if self.api_key and not self.api_key.startswith("sk-placeholder") and len(self.api_key) > 10:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}. Falling back to smart offline mode.")

    def is_live(self) -> bool:
        return self._client is not None

    def create_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        """Non-streaming chat completion."""
        if self._client:
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"

                response = self._client.chat.completions.create(**kwargs)
                choice = response.choices[0].message

                parsed_tool_calls = []
                if choice.tool_calls:
                    for tc in choice.tool_calls:
                        parsed_tool_calls.append({
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        })

                return LLMResponse(content=choice.content, tool_calls=parsed_tool_calls)
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}. Using intelligent fallback.")
                return self._simulate_smart_fallback(messages, tools)

        return self._simulate_smart_fallback(messages, tools)

    def stream_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Streaming chat completion yielding SSE-ready delta tokens or tool calls."""
        if self._client:
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"

                stream = self._client.chat.completions.create(**kwargs)

                accumulated_tool_calls = {}
                for chunk in stream:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if not delta:
                        continue

                    # Text delta
                    if delta.content:
                        yield {"type": "content_delta", "content": delta.content}

                    # Tool call deltas
                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            idx = tc.index
                            if idx not in accumulated_tool_calls:
                                accumulated_tool_calls[idx] = {
                                    "id": tc.id or f"call_{idx}",
                                    "name": tc.function.name if tc.function and tc.function.name else "",
                                    "arguments": "",
                                }
                            if tc.id:
                                accumulated_tool_calls[idx]["id"] = tc.id
                            if tc.function:
                                if tc.function.name:
                                    accumulated_tool_calls[idx]["name"] += tc.function.name
                                if tc.function.arguments:
                                    accumulated_tool_calls[idx]["arguments"] += tc.function.arguments

                if accumulated_tool_calls:
                    formatted = []
                    for idx, tc_data in accumulated_tool_calls.items():
                        formatted.append({
                            "id": tc_data["id"],
                            "type": "function",
                            "function": {
                                "name": tc_data["name"],
                                "arguments": tc_data["arguments"],
                            },
                        })
                    yield {"type": "tool_calls", "tool_calls": formatted}
                return

            except Exception as e:
                logger.error(f"Streaming error with Gemini: {e}. Yielding fallback.")
                yield from self._stream_smart_fallback(messages, tools)
                return

        yield from self._stream_smart_fallback(messages, tools)

    def _simulate_smart_fallback(
        self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None
    ) -> LLMResponse:
        """Intelligent offline heuristic agent for testing without requiring an active Gemini key."""
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                content = m.get("content")
                if isinstance(content, str):
                    last_user_msg = content
                elif isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            last_user_msg = part.get("text", "")
                break

        msg_lower = last_user_msg.lower()

        # Tool detection patterns
        # 1. Summary / calories today
        if any(w in msg_lower for w in ["how many calories", "today's total", "daily summary", "my progress", "what did i eat"]):
            return LLMResponse(
                content=None,
                tool_calls=[{
                    "id": "mock_call_summary",
                    "type": "function",
                    "function": {"name": "get_daily_summary", "arguments": "{}"},
                }],
            )

        # 2. Delete meal
        if any(w in msg_lower for w in ["delete meal", "remove meal", "delete my last"]):
            return LLMResponse(
                content=None,
                tool_calls=[{
                    "id": "mock_call_del",
                    "type": "function",
                    "function": {"name": "delete_meal", "arguments": json.dumps({"meal_id": 1})},
                }],
            )

        # 3. Set goal
        if "goal" in msg_lower and any(char.isdigit() for char in msg_lower):
            import re
            numbers = re.findall(r"\d+", msg_lower)
            target = float(numbers[0]) if numbers else 2000.0
            return LLMResponse(
                content=None,
                tool_calls=[{
                    "id": "mock_call_goal",
                    "type": "function",
                    "function": {"name": "set_calorie_goal", "arguments": json.dumps({"calorie_target": target})},
                }],
            )

        # 4. Profile / weight
        if any(w in msg_lower for w in ["i weigh", "my weight is", "height is", "update profile"]):
            import re
            numbers = re.findall(r"\d+", msg_lower)
            weight = float(numbers[0]) if numbers else 70.0
            return LLMResponse(
                content=None,
                tool_calls=[{
                    "id": "mock_call_prof",
                    "type": "function",
                    "function": {"name": "update_profile", "arguments": json.dumps({"current_weight_kg": weight})},
                }],
            )

        # 5. Diet plan
        if any(w in msg_lower for w in ["diet plan", "meal plan", "weight loss plan"]):
            return LLMResponse(
                content=None,
                tool_calls=[{
                    "id": "mock_call_plan",
                    "type": "function",
                    "function": {"name": "generate_diet_plan", "arguments": json.dumps({"goal_type": "weight_loss"})},
                }],
            )

        # 6. Log meal / food detection
        food_keywords = ["lunch", "breakfast", "dinner", "snack", "ate", "eating", "eggs", "chicken", "rice", "salad", "pizza", "burger", "oatmeal", "apple"]
        if any(k in msg_lower for k in food_keywords):
            meal_type = "lunch"
            if "breakfast" in msg_lower:
                meal_type = "breakfast"
            elif "dinner" in msg_lower:
                meal_type = "dinner"
            elif "snack" in msg_lower:
                meal_type = "snack"

            # Parse rough foods
            items = []
            if "egg" in msg_lower:
                items.append({"name": "Scrambled Eggs", "quantity": 2, "unit": "large eggs", "calories": 156, "protein_g": 12.6, "carbs_g": 1.2, "fat_g": 10.6})
            if "chicken" in msg_lower:
                items.append({"name": "Grilled Chicken Breast", "quantity": 150, "unit": "g", "calories": 248, "protein_g": 46.5, "carbs_g": 0, "fat_g": 5.4})
            if "rice" in msg_lower:
                items.append({"name": "Steamed White Rice", "quantity": 1, "unit": "cup", "calories": 205, "protein_g": 4.2, "carbs_g": 44.5, "fat_g": 0.4})
            if "salad" in msg_lower:
                items.append({"name": "Mixed Garden Salad", "quantity": 1, "unit": "bowl", "calories": 75, "protein_g": 2.0, "carbs_g": 8.0, "fat_g": 3.5})

            if not items:
                items.append({"name": last_user_msg or "Healthy Meal", "quantity": 1, "unit": "serving", "calories": 450, "protein_g": 30.0, "carbs_g": 45.0, "fat_g": 15.0})

            return LLMResponse(
                content=None,
                tool_calls=[{
                    "id": "mock_call_log",
                    "type": "function",
                    "function": {
                        "name": "log_meal",
                        "arguments": json.dumps({"meal_type": meal_type, "items": items, "notes": last_user_msg}),
                    },
                }],
            )

        return LLMResponse(
            content=f"Hello! I'm your AI Calorie & Nutrition Coach. I can log meals, calculate your daily calories, update your biometrics, build custom meal plans, and keep you on track. What would you like to log or check?",
            tool_calls=[],
        )

    def _stream_smart_fallback(
        self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        sim = self._simulate_smart_fallback(messages, tools)
        if sim.tool_calls:
            yield {"type": "tool_calls", "tool_calls": sim.tool_calls}
        elif sim.content:
            for word in sim.content.split(" "):
                yield {"type": "content_delta", "content": word + " "}
