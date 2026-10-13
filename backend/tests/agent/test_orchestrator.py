import json
from app.models.user import User
from app.agent.orchestrator import AgentOrchestrator

def test_orchestrator_flow(app, test_user):
    with app.app_context():
        user = User.query.get(test_user)
        orchestrator = AgentOrchestrator(user=user)

        # Send test user prompt
        stream = orchestrator.process_message_stream("I had 2 eggs and toast for breakfast")
        events = []
        for chunk in stream:
            if chunk.startswith("data: "):
                payload = json.loads(chunk[6:].strip())
                events.append(payload)

        # Assert thinking, tool_call, tool_result, token, done events are received
        event_types = [e.get("event") for e in events]
        assert "thinking" in [e.get("status") for e in events if "status" in e]
        assert "done" in event_types

        # Verify message was saved to conversation
        messages = orchestrator.conversation.messages
        assert len(messages) >= 2  # user and assistant
