from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Vertex Platform API"
    database_url: str = "sqlite:///./vertex.db"
    secret_key: str = "dev-only-change-me"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
