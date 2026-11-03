import json
import logging
import re
from typing import Generator, Dict, Any, List, Optional
from flask import current_app
from app.extensions import db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.agent.llm_client import LLMClient, parse_tool_arguments
from app.agent.context_builder import ContextBuilder
from app.agent.guardrails import Guardrails
from app.agent.confirmations import ConfirmationManager
from app.agent.tools.registry import TOOL_DEFINITIONS, dispatch_tool_call

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self, user: User, conversation: Optional[Conversation] = None):
        self.user = user
        self.user_id = user.id
        if conversation:
            if conversation.user_id != self.user_id:
                logger.error("Unauthorized conversation access attempt: user %s requested conversation %s belonging to user %s", self.user_id, conversation.id, conversation.user_id)
                raise ValueError("Unauthorized conversation access.")
            self.conversation = conversation
            self.conversation_id = conversation.id
        else:
            self.conversation = self._get_or_create_conversation()
            self.conversation_id = self.conversation.id
        self.llm = LLMClient()
        self.max_iterations = current_app.config.get("AGENT_MAX_ITERATIONS", 5) if current_app else 5

    def _get_or_create_conversation(self) -> Conversation:
        conv = Conversation(user_id=self.user_id, title="Nutrition Assistant")
        db.session.add(conv)
        db.session.commit()
        return conv

    def process_message_stream(
        self,
        user_message_text: Optional[str],
        image_id: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """Main agent loop yielding Server-Sent Events (SSE) data chunks."""
        try:
            # Rebind or re-fetch user and conversation in the streaming session
            fresh_user = db.session.get(User, self.user_id)
            if fresh_user:
                self.user = fresh_user

            fresh_conv = db.session.get(Conversation, self.conversation_id)
            if fresh_conv:
                if fresh_conv.user_id != self.user_id:
                    raise ValueError("Unauthorized conversation access.")
                self.conversation = fresh_conv
            elif not self.conversation:
                self.conversation = self._get_or_create_conversation()
                self.conversation_id = self.conversation.id

            # 1. Guardrail input validation
            is_safe, safety_error = Guardrails.inspect_request(user_message_text, image_id=image_id)
            if not is_safe:
                # Yield safety warning directly
                block = {"type": "text", "content": safety_error}
                user_msg = Message(
                    conversation_id=self.conversation_id,
                    role="user",
                    content=user_message_text or "Uploaded food photo.",
                    image_id=image_id,
                )
                asst_msg = Message(
                    conversation_id=self.conversation_id,
                    role="assistant",
                    content=safety_error,
                    blocks=[block],
                )
                db.session.add_all([user_msg, asst_msg])
                db.session.commit()

                yield f"data: {json.dumps({'event': 'token', 'token': safety_error})}\n\n"
                yield f"data: {json.dumps({'event': 'done', 'message': asst_msg.to_dict(), 'blocks': [block]})}\n\n"
                return

            display_user_text = (user_message_text or "").strip() or "Please analyze this food photo."

            # 2. Persist user message
            user_msg = Message(
                conversation_id=self.conversation_id,
                role="user",
                content=display_user_text,
                image_id=image_id,
            )
            db.session.add(user_msg)
            db.session.commit()

            # 3. Context builder (exclude the newly committed message ID to avoid duplicates)
            messages, meta = ContextBuilder.build_llm_messages(
                user=self.user,
                conversation=self.conversation,
                current_user_message=display_user_text,
                image_url=image_url,
                exclude_message_id=user_msg.id,
            )

            all_tool_calls_executed = []
            all_tool_results = []
            successful_tool_executions = []
            failed_tool_executions = []
            blocks: List[Dict[str, Any]] = []
            pending_action_record = None

            current_iteration = 0
            final_assistant_text = ""

            # Multi-turn tool execution loop
            while current_iteration < self.max_iterations:
                current_iteration += 1
                yield f"data: {json.dumps({'event': 'status', 'status': 'thinking', 'iteration': current_iteration})}\n\n"

                # Call LLM
                llm_resp = self.llm.create_chat_completion(messages, tools=TOOL_DEFINITIONS)

                # If LLM didn't call any tools, we have our final direct reply
                if not llm_resp.tool_calls:
                    final_assistant_text = llm_resp.content or ""
                    break

                iteration_tool_results = []
                for tc in llm_resp.tool_calls:
                    func_name = tc.get("function", {}).get("name", "")
                    args_val = tc.get("function", {}).get("arguments", "")

                    # Safely validate and parse tool arguments
                    is_valid, args, arg_err = parse_tool_arguments(args_val)

                    if not is_valid:
                        logger.warning("Tool call '%s' had malformed arguments: %s", func_name, arg_err)
                        result = {
                            "status": "error",
                            "message": f"Malformed arguments for tool '{func_name}': {arg_err}",
                        }
                        failed_tool_executions.append({"tool": func_name, "error": arg_err, "result": result})
                    else:
                        yield f"data: {json.dumps({'event': 'tool_call', 'tool': func_name, 'args': args})}\n\n"
                        result = dispatch_tool_call(func_name, self.user_id, args)

                        if result.get("status") == "error":
                            failed_tool_executions.append({"tool": func_name, "result": result})
                        else:
                            successful_tool_executions.append({"tool": func_name, "result": result})

                    all_tool_calls_executed.append(tc)
                    all_tool_results.append({"tool_call_id": tc.get("id", ""), "name": func_name, "result": result})
                    iteration_tool_results.append({"tool_call_id": tc.get("id", ""), "name": func_name, "result": result})

                    yield f"data: {json.dumps({'event': 'tool_result', 'tool': func_name, 'result': result})}\n\n"

                    # Convert tool outcome to typed UI block
                    ui_block = self._map_result_to_block(func_name, result)
                    if ui_block:
                        blocks.append(ui_block)

                    # Check if this tool generated a pending confirmation
                    if result.get("status") == "pending_confirmation":
                        pending_action_record = result.get("pending_action")

                # Append assistant tool_calls and each tool result to prompt context in exact paired format
                messages.append({
                    "role": "assistant",
                    "content": llm_resp.content or "",
                    "tool_calls": llm_resp.tool_calls,
                })
                for tc, tr in zip(llm_resp.tool_calls, iteration_tool_results):
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.get("id", "call_0"),
                        "content": json.dumps(tr["result"]),
                    })

            # Stream concluding explanation token by token
            if not final_assistant_text:
                if current_iteration >= self.max_iterations and not all_tool_results:
                    final_assistant_text = "I reached the maximum step limit before completing the request."
                    yield f"data: {json.dumps({'event': 'token', 'token': final_assistant_text})}\n\n"
                else:
                    streamed_tokens = []
                    try:
                        for chunk in self.llm.stream_chat_completion(messages, tools=None):
                            if chunk.get("type") == "content_delta":
                                delta = chunk.get("content", "")
                                if delta:
                                    streamed_tokens.append(delta)
                                    yield f"data: {json.dumps({'event': 'token', 'token': delta})}\n\n"
                        final_assistant_text = "".join(streamed_tokens)
                    except Exception as stream_err:
                        logger.warning("Streaming completion failed, using non-streaming fallback: %s", stream_err)
                        final_resp = self.llm.create_chat_completion(messages, tools=None)
                        final_assistant_text = final_resp.content or ""
                        if final_assistant_text:
                            yield f"data: {json.dumps({'event': 'token', 'token': final_assistant_text})}\n\n"
            else:
                yield f"data: {json.dumps({'event': 'token', 'token': final_assistant_text})}\n\n"

            # Clean any raw tool blocks, tool names, or redundant asterisks
            final_assistant_text = self._sanitize_text(final_assistant_text)

            # Prevent false success reporting if tools failed
            if not final_assistant_text:
                if failed_tool_executions and not successful_tool_executions:
                    first_err = failed_tool_executions[0].get("result", {}).get("message") or failed_tool_executions[0].get("error", "The requested operation could not be completed.")
                    final_assistant_text = f"I could not complete your request: {first_err}"
                elif successful_tool_executions:
                    first_msg = successful_tool_executions[0].get("result", {}).get("message", "Operation completed successfully.")
                    final_assistant_text = first_msg
                else:
                    final_assistant_text = "I have processed your request."

            # Attach disclaimer if meal plans or diet goals are involved
            if any(b.get("type") in ["diet_plan_card", "daily_summary_card"] for b in blocks):
                final_assistant_text = Guardrails.attach_disclaimer(final_assistant_text)

            # Add text block if not present
            blocks.insert(0, {"type": "text", "content": final_assistant_text})

            # Save assistant message to DB
            asst_msg = Message(
                conversation_id=self.conversation_id,
                role="assistant",
                content=final_assistant_text,
                tool_calls=all_tool_calls_executed,
                tool_results=all_tool_results,
                blocks=blocks,
                pending_action=pending_action_record,
            )
            db.session.add(asst_msg)
            db.session.commit()

            yield f"data: {json.dumps({'event': 'done', 'message': asst_msg.to_dict(), 'blocks': blocks})}\n\n"
        except Exception as e:
            logger.exception("Error in process_message_stream: %s", e)
            db.session.rollback()
            yield f"data: {json.dumps({'event': 'error', 'error': str(e)})}\n\n"

    def _map_result_to_block(self, tool_name: str, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Maps backend tool results into rich UI block payloads."""
        if result.get("status") == "pending_confirmation":
            return ConfirmationManager.build_confirmation_block(result["pending_action"])

        if tool_name in ["log_meal", "edit_meal"] and result.get("status") == "success":
            return {
                "type": "meal_card",
                "data": {
                    "meal_id": result.get("meal_id"),
                    "meal_type": result.get("meal_type"),
                    "total_calories": result.get("total_calories"),
                    "total_protein_g": result.get("total_protein_g"),
                    "total_carbs_g": result.get("total_carbs_g"),
                    "total_fat_g": result.get("total_fat_g"),
                    "items": result.get("items", []),
                },
            }

        if tool_name in ["get_daily_summary", "get_weekly_report"] and result.get("status") == "success":
            return {
                "type": "daily_summary_card",
                "data": result.get("summary") or result.get("report"),
            }

        if tool_name in ["generate_diet_plan", "get_active_plan"] and result.get("status") == "success":
            return {
                "type": "diet_plan_card",
                "data": result.get("plan"),
            }

        return None

    def _sanitize_text(self, text: str) -> str:
        """Strip raw tool calls, code fences, and redundant asterisks from user-facing responses."""
        if not text:
            return ""

        # Remove tool_code markdown blocks (e.g. ```tool_code ... ``` or ```python ... ```)
        cleaned = re.sub(r"```(?:tool_code|python|json)?[\s\S]*?```", "", text, flags=re.IGNORECASE)

        # Remove standalone function calls like get_daily_summary(...) or log_meal(...)
        cleaned = re.sub(
            r"\b(?:get_daily_summary|log_meal|edit_meal|delete_meal|analyze_meal|get_weekly_report|set_calorie_goal|update_profile|generate_diet_plan|set_reminder)\([^)]*\)",
            "",
            cleaned,
        )

        # Remove leading/trailing bullet asterisks like `*   **` or `* ` while preserving clean bullet lists
        # Turn bold markdown **word** into plain text
        cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)

        # Normalize markdown bullet asterisks into clean bullets (e.g., "*   Total" -> "• Total")
        cleaned = re.sub(r"^[ \t]*\*[ \t]+", "• ", cleaned, flags=re.MULTILINE)

        # Strip remaining isolated stray asterisks
        cleaned = cleaned.replace("*", "")

        # Collapse excess blank lines
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
        return cleaned
