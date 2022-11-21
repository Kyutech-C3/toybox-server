from pydantic.main import BaseModel


class DeleteStatus(BaseModel):
    status: str
