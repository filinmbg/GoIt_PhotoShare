from typing import Optional
from pydantic import BaseModel
from src.entity.models import Role


# class User(BaseModel):
#     id: int
#     username: str
#     email: str
#     role: Role = Role.user
#     avatar: str
#
#     class ConfigDict:
#         orm_mode = True


class PostSingle(BaseModel):
    id: int
    user_id: int
    url: str
    description: Optional[str]

    class ConfigDict:
        orm_mode = True


