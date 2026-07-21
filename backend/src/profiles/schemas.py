from pydantic import BaseModel, Field, ConfigDict

class ProfileSchema(BaseModel):
    name: str = Field(max_length=255)
    tag: str = Field(max_length=255)
    profile: str

    model_config = ConfigDict(from_attributes=True)  # pyright: ignore[reportUnannotatedClassAttribute]