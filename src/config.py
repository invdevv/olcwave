from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    RW_API_URL: str
    RW_API_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()  # pyright: ignore[reportCallIssue]