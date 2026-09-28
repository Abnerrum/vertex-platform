from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Vertex Platform API"
    database_url: str = "sqlite:///./vertex.db"
    secret_key: str = "dev-only-change-me-please-use-at-least-32-bytes"
    access_token_expire_minutes: int = 480
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
