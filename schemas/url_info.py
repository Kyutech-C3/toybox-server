from datetime import datetime
import json
from pydantic import BaseModel
from pydantic.class_validators import validator
from db.models import UrlType
from .user import User

class BaseUrlInfo(BaseModel):
    url: str
    url_type: str

    @validator('url_type')
    def value_of(cls, v):
        for e in UrlType:
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

class UrlInfo(BaseUrlInfo):
    id: str
    user: User
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True