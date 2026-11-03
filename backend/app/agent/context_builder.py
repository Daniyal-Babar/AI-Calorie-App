import json
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.services.calorie_service import CalorieService
from app.services.diet_service import DietService
from app.services.upload_service import UploadService
from app.agent.prompts.system import get_system_prompt

class ContextBuilder:
    @staticmethod
    def build_llm_messages(
        user: User,
        conversation: Conversation,
        current_user_message: str,
        image_url: str | None = None,
        max_history: int = 10,
        exclude_message_id: Optional[int] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Build the complete messages array for the LLM request adhering to OpenAI/Ollama standards."""
        # 1. Profile and Daily Snapshot using consistent UTC date
        today = datetime.now(timezone.utc).date()
        daily_summary = CalorieService.get_daily_summary(user.id, today)
        tdee = CalorieService.calculate_tdee(user)
        bmr = CalorieService.calculate_bmr(user)
        active_plan = DietService.get_active_plan(user.id)
        missing_fields = user.missing_profile_fields()

        system_instruction = get_system_prompt(user.name, missing_fields)

        snapshot_lines = [
            "CURRENT USER SNAPSHOT:",
            f"- User Name: {user.name}",
            f"- Profile: Age: {user.age or 'Not set'}, Gender: {user.gender or 'Not set'}, Height: {user.height_cm or 'Not set'}cm, Weight: {user.current_weight_kg or 'Not set'}kg, Target Weight: {user.target_weight_kg or 'Not set'}kg, Activity: {user.activity_level or 'Not set'}",
        ]
        if bmr and tdee:
            snapshot_lines.append(f"- Calculated BMR: {bmr} kcal | TDEE: {tdee} kcal")
        else:
            snapshot_lines.append("- Calculated BMR/TDEE: Unavailable until age, height, weight, gender, and activity are provided.")

        consumed = daily_summary["consumed"]
        targets = daily_summary["targets"]
        snapshot_lines.append(
            f"- Today's Nutrition ({today.isoformat()}): Consumed {consumed['calories']} / {targets['calories']} kcal (Remaining: {daily_summary['remaining_calories']} kcal). "
            f"Protein: {consumed['protein_g']}g/{targets['protein_g']}g, Carbs: {consumed['carbs_g']}g/{targets['carbs_g']}g, Fat: {consumed['fat_g']}g/{targets['fat_g']}g. Meals logged: {daily_summary['meals_count']}."
        )

        if active_plan:
            snapshot_lines.append(f"- Active Diet Plan: '{active_plan.title}' ({active_plan.goal_type}, target: {active_plan.target_daily_calories} kcal/day).")

        full_system_content = f"{system_instruction}\n\n" + "\n".join(snapshot_lines)

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": full_system_content}
        ]

        # 2. Add last N conversation messages, excluding the current pending user message to prevent duplication
        query = Message.query.filter(Message.conversation_id == conversation.id)
        if exclude_message_id is not None:
            query = query.filter(Message.id != exclude_message_id)

        recent_msgs = (
            query.order_by(Message.created_at.desc())
            .limit(max_history)
            .all()
        )
        recent_msgs.reverse()

        for m in recent_msgs:
            if m.role == "user":
                if m.image_id:
                    img_path = UploadService.get_file_path(m.image_id, user_id=user.id)
                    if img_path:
                        messages.append({
                            "role": "user",
                            "content": [
                                {"type": "text", "text": m.content or "Uploaded food photo."},
                                {"type": "image_url", "image_url": {"url": img_path}},
                            ],
                        })
                    else:
                        messages.append({"role": "user", "content": m.content or ""})
                else:
                    messages.append({"role": "user", "content": m.content or ""})

            elif m.role == "assistant":
                # Ensure tool_calls and tool results are reconstructed in complete pairs
                if m.tool_calls and m.tool_results:
                    results_by_id = {
                        tr.get("tool_call_id"): tr.get("result")
                        for tr in m.tool_results
                        if tr.get("tool_call_id")
                    }
                    messages.append({
                        "role": "assistant",
                        "content": m.content or "",
                        "tool_calls": m.tool_calls,
                    })
                    for tc in m.tool_calls:
                        tc_id = tc.get("id")
                        tr_result = results_by_id.get(tc_id, {"status": "success"})
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc_id or "call_0",
                            "content": json.dumps(tr_result),
                        })
                else:
                    messages.append({"role": "assistant", "content": m.content or ""})

        # 3. Append current user message (with optional image)
        if image_url:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": current_user_message or "Analyze this meal photo."},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            })
        else:
            messages.append({"role": "user", "content": current_user_message})

        snapshot_meta = {
            "daily_summary": daily_summary,
            "missing_fields": missing_fields,
            "has_active_plan": bool(active_plan),
        }

        return messages, snapshot_meta

        return messages, snapshot_meta
