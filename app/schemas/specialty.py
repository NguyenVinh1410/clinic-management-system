from pydantic import BaseModel, ConfigDict, Field

class SpecialtyCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

class SpecialtyUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

class SpecialtyResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    specialty_id: int
    name: str
    description: str | None