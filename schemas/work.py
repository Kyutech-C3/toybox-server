from pydantic import BaseModel

class Work(BaseModel):
    id: str
    name: str
    latest_stage: str
    host_user: User

    class Config:
        orm_mode = True