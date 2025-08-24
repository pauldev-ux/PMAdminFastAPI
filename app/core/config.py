from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Entorno
    APP_ENV: str = "local"  # "local" | "prod"

    # Seguridad / Auth
    SECRET_KEY: str = "superpm"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    #DB
    DATABASE_URL: str = "postgresql+psycopg://postgres:123456@localhost:5432/perfumes_db"

    # CORS / hosts
    ALLOWED_ORIGINS: str = "http://127.0.0.1:5173,http://localhost:5173"
    TRUSTED_HOSTS: str = "*"  # coma-separado

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_prod(self) -> bool:
        return self.APP_ENV.lower() == "prod"

settings = Settings()
