from pydantic import BaseModel
class PostSingle(BaseModel):
    url: str
    description: str
    qr_url: str

class GetSingle(BaseModel):
    id: int
    user_id: int
    url: str
    description: str
    qr_url: str


class PutSingle(BaseModel):
    description: str


class DeleteSingle(BaseModel):
    message: str

