from pydantic import BaseModel

class ContainerSchema(BaseModel):
    id: str
    name: str
    user_id: str
    config_tag: str
    status: str
    created: str
    image: str

class ContainerLogsSchema(BaseModel):
    name: str
    logs: str

class ContainerConfigSchema(BaseModel):
    name: str
    config: str

class ContainerStatsSchema(BaseModel):
    name: str
    upload_bytes: int = 0
    download_bytes: int = 0
    total_bytes: int = 0
    upload_rate_bps: int = 0
    download_rate_bps: int = 0
