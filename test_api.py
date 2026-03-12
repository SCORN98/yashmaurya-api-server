from fastapi.testclient import TestClient

from app.main import app
from app.storage import load_model

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_estimate() -> None:
    model = load_model().model_dump()
    resp = client.post("/analyze/estimate", json=model)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_weight_kg"] > 0
    assert body["estimated_cost_usd"] > 0


def test_propose_and_apply() -> None:
    model = load_model().model_dump()

    prop = client.post("/changes/propose", json=model)
    assert prop.status_code == 200
    suggestions = prop.json()["suggested_changes"]

    if suggestions:
        selected = [suggestions[0]["change_id"]]
    else:
        selected = []

    apply_payload = {
        "model": model,
        "selected_change_ids": selected,
        "approval_token": "APPROVED",
    }

    result = client.post("/changes/apply", json=apply_payload)
    assert result.status_code == 200
    assert "event_id" in result.json()


def test_apply_rejects_without_approval() -> None:
    model = load_model().model_dump()
    apply_payload = {
        "model": model,
        "selected_change_ids": [],
        "approval_token": "NOPE",
    }
    result = client.post("/changes/apply", json=apply_payload)
    assert result.status_code == 400
