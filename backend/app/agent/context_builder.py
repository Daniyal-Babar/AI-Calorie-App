from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.services.calorie_service import CalorieService
from app.services.diet_service import DietService
from app.agent.prompts.system import get_system_prompt

class ContextBuilder:
    @staticmethod
    def build_llm_messages(
        user: User,
        conversation: Conversation,
        current_user_message: str,
        image_url: str | None = None,
        max_history: int = 10,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Build the complete messages array for the LLM request."""
        # 1. Profile and Daily Snapshot
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

        messages = [
            {"role": "system", "content": full_system_content}
        ]

        # 2. Add last N conversation messages
        recent_msgs = (
            Message.query.filter_by(conversation_id=conversation.id)
            .order_by(Message.created_at.desc())
            .limit(max_history)
            .all()
        )
        recent_msgs.reverse()

        for m in recent_msgs:
            if m.role == "user":
                messages.append({"role": "user", "content": m.content or ""})
            elif m.role == "assistant":
                msg_dict = {"role": "assistant", "content": m.content or ""}
                if m.tool_calls:
                    msg_dict["tool_calls"] = m.tool_calls
                messages.append(msg_dict)
            elif m.role == "tool":
                messages.append({
                    "role": "tool",
                    "content": m.content or "",
                    "tool_call_id": m.tool_calls[0]["id"] if m.tool_calls else "tool_0",
                })

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
