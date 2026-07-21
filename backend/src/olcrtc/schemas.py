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
