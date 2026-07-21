from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    NAME: str
    
    RW_API_URL: str
    RW_API_TOKEN: str

    DB_URL: str

    model_config = SettingsConfigDict(env_file=".env")  # pyright: ignore[reportUnannotatedClassAttribute]

settings = Settings()  # pyright: ignore[reportCallIssue]