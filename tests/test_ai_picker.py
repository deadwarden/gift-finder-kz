import json
from unittest.mock import MagicMock, patch

import pytest

from app.models.schemas import GiftRequest
from app.services.ai_picker import build_prompt, generate_gifts


SAMPLE_REQ = GiftRequest(
    event="день рождения",
    gender="женщина",
    age="26–35 лет",
    relation="подруга",
    hobbies=["кулинария", "путешествия"],
    price_from=5000,
    price_to=20000,
    extra="не любит сладкое",
)

SAMPLE_JSON = json.dumps({
    "gifts": [
        {
            "name": "Набор специй",
            "price_range": "5 000–8 000 ₸",
            "why": "Для любителя кулинарии.",
            "tags": ["кулинария"],
            "search_query": "набор специй кулинарный",
        }
    ]
})


def test_build_prompt_contains_key_fields():
    prompt = build_prompt(SAMPLE_REQ)
    assert "день рождения" in prompt
    assert "женщина" in prompt
    assert "5 000" in prompt or "5000" in prompt
    assert "не любит сладкое" in prompt
    assert "JSON" in prompt


def test_build_prompt_no_extra():
    req = SAMPLE_REQ.model_copy(update={"extra": ""})
    prompt = build_prompt(req)
    assert "Дополнительная информация" not in prompt


@pytest.mark.asyncio
async def test_generate_gifts_parses_response():
    mock_content = MagicMock()
    mock_content.text = SAMPLE_JSON

    mock_message = MagicMock()
    mock_message.content = [mock_content]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    with patch("app.services.ai_picker.anthropic.Anthropic", return_value=mock_client):
        result = await generate_gifts(SAMPLE_REQ)

    assert len(result.gifts) == 1
    assert result.gifts[0].name == "Набор специй"
    assert result.cached is False
