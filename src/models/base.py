from pydantic import BaseModel, Field


class BaseProjectModel(BaseModel):
    id: str = Field(..., serialization_alias='uuid')

    class Config:
        allow_population_by_field_name = True
