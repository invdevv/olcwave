from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    RW_ENABLED: bool
    RW_API_URL: str = ""
    RW_API_TOKEN: str = ""
    RW_CADDY_TOKEN: str = ""

    DB_HOST: str
    DB_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @property
    def DB_DSN(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"

    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    JWT_SECRET_KEY: str
    JWT_EXPIRE_MINUTES: int = 1440

    RW_SQUAD_NAME: str = ""

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # pyright: ignore[reportUnannotatedClassAttribute]
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
