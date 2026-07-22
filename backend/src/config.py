from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    NAME: str
    
    RW_API_URL: str
    RW_API_TOKEN: str

    DB_HOST: str
    DB_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"

    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    JWT_SECRET_KEY: str
    JWT_EXPIRE_MINUTES: int = 1440

    # Default traffic limit applied to new users, in bytes. Set 0 for unlimited.
    DEFAULT_TRAFFIC_LIMIT: int

    # Interval (seconds) for the background traffic collection loop.
    TRAFFIC_COLLECT_INTERVAL: int

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env")  # pyright: ignore[reportUnannotatedClassAttribute]

settings = Settings()  # pyright: ignore[reportCallIssue]