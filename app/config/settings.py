from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Clinic Management System"
    app_env: str = "development"
    debug: bool = True

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    templates_dir: str = "app/templates"
    static_dir: str = "app/static"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        #tem bien mtr kh phan biet in hoa hay thuong APP__NAME HAY app__name deu duoc
        case_sensitive=False,
        #bo qua bien mtr khong khai bao trong class
        extra="ignore",
    )

settings = Settings()
