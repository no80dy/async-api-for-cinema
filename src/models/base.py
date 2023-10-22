from pydantic import BaseModel, Field


class BaseModelOrjson(BaseModel):
    id: str = Field(..., serialization_alias='uuid')

    class Config:
        allow_population_by_field_name = True
