from typing import Optional, List
from pydantic import BaseModel
import datetime


class PostSingle(BaseModel):
    id: int
    user_id: int
    url: str
    description: Optional[str]

    class ConfigDict:
        orm_mode = True


class GetSingle(BaseModel):
    id: int
    user_id: int
    url: str
    description: str
    qr_url: str

    class ConfigDict:
        orm_mode = True


class PutSingle(BaseModel):
    description: str
    updated_at: datetime.datetime

    class ConfigDict:
        orm_mode = True


class DeleteSingle(BaseModel):
    message: str

