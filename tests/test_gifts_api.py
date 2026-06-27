import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import GiftItem, GiftResponse

SAMPLE_RESPONSE = GiftResponse(
    gifts=[
        GiftItem(
            name="Беспроводные наушники Sony WH-1000XM5",
            price_range="25 000–30 000 ₸",
            why="Отличный выбор для любителя музыки.",
            tags=["электроника", "музыка"],
            search_query="Sony WH-1000XM5 наушники",
        )
    ],
    cached=False,
    generated_at=datetime.now(timezone.utc),
)

VALID_BODY = {
    "event": "день рождения",
    "gender": "мужчина",
    "age": "26–35 лет",
    "relation": "коллега",
    "hobbies": ["музыка", "гаджеты"],
    "price_from": 10000,
    "price_to": 30000,
    "extra": "",
}


@pytest.fixture
def client():
    return TestClient(app)


def test_gifts_success(client):
    with (
        patch("app.api.gifts.get_cached", new=AsyncMock(return_value=None)),
        patch("app.api.gifts.generate_gifts", new=AsyncMock(return_value=SAMPLE_RESPONSE)),
        patch("app.api.gifts.set_cached", new=AsyncMock()),
    ):
        resp = client.post("/api/gifts", json=VALID_BODY)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["gifts"]) == 1
    assert data["gifts"][0]["name"] == "Беспроводные наушники Sony WH-1000XM5"


def test_gifts_cache_hit(client):
    cached = SAMPLE_RESPONSE.model_copy(update={"cached": True})
    with patch("app.api.gifts.get_cached", new=AsyncMock(return_value=cached)):
        resp = client.post("/api/gifts", json=VALID_BODY)
    assert resp.status_code == 200
    assert resp.json()["cached"] is True


def test_gifts_validation_error(client):
    resp = client.post("/api/gifts", json={"event": "день рождения"})
    assert resp.status_code == 422


def test_gifts_ai_error(client):
    with (
        patch("app.api.gifts.get_cached", new=AsyncMock(return_value=None)),
        patch("app.api.gifts.generate_gifts", new=AsyncMock(side_effect=Exception("AI down"))),
        patch("app.api.gifts.set_cached", new=AsyncMock()),
    ):
        resp = client.post("/api/gifts", json=VALID_BODY)
    assert resp.status_code == 502


def test_index_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Gift Finder" in resp.text
