import uuid

from pydantic import BaseModel, Field


class BaseProjectModel(BaseModel):
    id: uuid.UUID = Field(..., serialization_alias='uuid')

    class Config:
        allow_population_by_field_name = True
