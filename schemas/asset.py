from datetime import datetime
import json
from .user import User
from pydantic import BaseModel, validator
from db.models import AssetType, Work

class BaseAsset(BaseModel):
    asset_type: str

    @validator('asset_type')
    def value_of(cls, v):
        for e in AssetType:
            if e.value == v:
                return e
        raise ValueError('{} is invalid asset type.'.format(v))

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class Asset(BaseAsset):
    id: str
    user: User
    extension: str
    url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True