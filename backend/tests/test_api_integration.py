import json
import pytest

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_auth_and_chat_flow(client):
    # 1. Register
    reg_res = client.post(
        "/api/auth/register",
        json={"email": "newuser@example.com", "password": "password123", "name": "Sam"},
    )
    assert reg_res.status_code == 201
    token = reg_res.get_json()["token"]

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 2. Get me
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.get_json()["user"]["email"] == "newuser@example.com"

    # 3. Send chat message
    chat_res = client.post(
        "/api/chat",
        headers=headers,
        json={"message": "I had 2 eggs and a banana for breakfast"},
    )
    assert chat_res.status_code == 200
    assert "text/event-stream" in chat_res.content_type
