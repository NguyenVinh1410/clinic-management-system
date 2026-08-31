from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        #tem bien mtr kh phan biet in hoa hay thuong APP__NAME HAY app__name deu duoc
        case_sensitive=False,
        #bo qua bien mtr khong khai bao trong class
        extra="ignore",
    )

settings = Settings()
