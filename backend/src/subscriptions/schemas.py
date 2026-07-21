from pydantic import BaseModel

class ServerSchema(BaseModel):
    uri: str
    name: str

class SubscriptionSchema(BaseModel):
    name: str
    update: int
    refresh: int

    servers: list[ServerSchema]