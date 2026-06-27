from datetime import datetime
from pydantic import BaseModel, Field


class GiftRequest(BaseModel):
    event: str
    gender: str
    age: str
    relation: str
    hobbies: list[str] = []
    price_from: int = Field(ge=0)
    price_to: int = Field(ge=0)
    extra: str = ""


class GiftItem(BaseModel):
    name: str
    price_range: str
    why: str
    tags: list[str]
    search_query: str


class GiftResponse(BaseModel):
    gifts: list[GiftItem]
    cached: bool = False
    generated_at: datetime
