from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BASE_HOST: str
    BASE_PORT: int

    RW_API_URL: str
    RW_API_TOKEN: str

    OLCRTC_CARRIER: str
    OLCRTC_TRANSPORT: str
    
    OLCRTC_SERVER_NAME: str

    model_config = SettingsConfigDict(env_file="backend/.env")

settings = Settings()  # pyright: ignore[reportCallIssue]