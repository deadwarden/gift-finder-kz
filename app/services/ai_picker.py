import json
from datetime import datetime, timezone

import anthropic

from app.config import settings
from app.models.schemas import GiftItem, GiftRequest, GiftResponse


def build_prompt(req: GiftRequest) -> str:
    hobbies_str = ", ".join(req.hobbies) if req.hobbies else "не указаны"
    extra_str = f"\nДополнительная информация: {req.extra}" if req.extra else ""
    return f"""Ты — эксперт по подбору подарков для покупателей в Казахстане.

Подбери 6 конкретных подарков по следующему профилю получателя:
- Событие: {req.event}
- Пол получателя: {req.gender}
- Возраст: {req.age}
- Кем приходится дарителю: {req.relation}
- Хобби и интересы: {hobbies_str}
- Бюджет: от {req.price_from:,} до {req.price_to:,} тенге{extra_str}

Требования к подаркам:
1. Товары должны быть доступны на маркетплейсах: Kaspi.kz, Wildberries KZ, OZON KZ или Amazon (с доставкой в Казахстан)
2. Цена каждого подарка должна укладываться в указанный бюджет в тенге
3. Подарки должны быть конкретными (не абстрактные категории, а реальные товары)
4. Для каждого подарка укажи search_query — оптимизированный поисковый запрос на русском языке для поиска на маркетплейсе

Ответь СТРОГО в JSON без markdown-обёртки, по такой структуре:
{{
  "gifts": [
    {{
      "name": "Название товара",
      "price_range": "X 000 – Y 000 ₸",
      "why": "1-2 предложения: почему этот подарок подходит именно этому человеку",
      "tags": ["тег1", "тег2", "тег3"],
      "search_query": "поисковый запрос для маркетплейса"
    }}
  ]
}}"""


async def generate_gifts(req: GiftRequest) -> GiftResponse:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    prompt = build_prompt(req)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text.strip()
    data = json.loads(text)
    gifts = [GiftItem(**g) for g in data["gifts"]]

    return GiftResponse(
        gifts=gifts,
        cached=False,
        generated_at=datetime.now(timezone.utc),
    )
