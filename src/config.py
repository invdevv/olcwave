from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_HOST: str
    BASE_PORT: int

    RW_API_URL: str
    RW_API_TOKEN: str

    OLCRTC_MANAGER_URL: str
    OLCRTC_MANAGER_LOGIN: str
    OLCRTC_MANAGER_PASSWORD: str

    OLCRTC_SUB_PATH: str
    OLCRTC_CARRIER: str
    OLCRTC_TRANSPORT: str
    OLCRTC_SERVER_NAME: str
    OLCRTC_DNS: str
    OLCRTC_ROOM_ID: str | None
    OLCRTC_JITSI_URL: str | None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()  # pyright: ignore[reportCallIssue]