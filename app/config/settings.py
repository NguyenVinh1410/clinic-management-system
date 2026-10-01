from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Clinic Management System"
    app_env: str = "development"
    debug: bool = True

    database_url: str = Field(alias="DATABASE_URL")

    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    templates_dir: str = Field(default="app/templates", alias="TEMPLATES_DIR")
    static_dir: str = Field(default="app/static", alias="STATIC_DIR")

    ollama_base_url: str = Field(
        default="http://localhost:11434/v1",
        alias="OLLAMA_BASE_URL",
    )

    ollama_model: str = Field(
        default="qwen3:8b",
        alias="OLLAMA_MODEL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
