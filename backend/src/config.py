from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    NAME: str
    
    RW_API_URL: str
    RW_API_TOKEN: str

    DB_URL: str

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "strong_password_here"

    JWT_SECRET_KEY: str = "change_me"
    JWT_EXPIRE_MINUTES: int = 1440

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env")  # pyright: ignore[reportUnannotatedClassAttribute]

settings = Settings()  # pyright: ignore[reportCallIssue]