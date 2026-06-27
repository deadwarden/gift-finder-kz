from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    redis_url: str = "redis://localhost:6379"
    allowed_origins: list[str] = ["*"]
    rate_limit: str = "20/minute"

    model_config = {"env_file": ".env"}


settings = Settings()
