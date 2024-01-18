from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from fastapi import UploadFile, File


class TagBase(BaseModel):
    tag_name: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int


class ImageBase(BaseModel):
    description: str
    tags: List[TagCreate] = []
    public_id: str
    user_id: int = 1


class ImageUpload(ImageBase):
    image_file: Optional[UploadFile]


class ImageUpdate(ImageBase):
    pass


class ImageResponse(ImageBase):
    id: int
    tags: List[TagResponse] = []

    class Config:
        orm_mode = True
