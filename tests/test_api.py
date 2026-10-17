"""Unit tests for FastAPI endpoints in app/main.py."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "tiers" in data


def test_submit_ticket_mock():
    payload = {
        "ticket_text": "Where is my order ORD-1001?",
        "order_id": "ORD-1001",
        "mock": True,
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] in ["nano", "super", "ultra"]
    assert "answer" in data
    assert data["cost"] >= 0


def test_get_stats():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "savings_percentage" in data


def test_benchmark_replay_mock():
    response = client.post("/benchmark/replay?mock=true")
    assert response.status_code == 200
    data = response.json()
    assert data["replayed"] == 3
    assert len(data["results"]) == 3
