from pydantic import BaseModel
from typing import Optional, List
from pydantic_settings import SettingsConfigDict
from datetime import datetime, date


class TagModel(BaseModel):
    tag_name: str


class TagResponse(TagModel):
    model_config = SettingsConfigDict(from_attributes=True)
    id: int
    tag_name: str


class AddTag(BaseModel):
    detail: str = "Image tags has been updated"


class TagDetail(BaseModel):
    id: int
    name: str


class PhotoSchema(BaseModel):
    id: int
    url: str
    qr_url: Optional[str]
    description: Optional[str]
    created_at: datetime
    user_id: int


class PhotoResponse(BaseModel):
    photo: PhotoSchema
    tags: Optional[List[TagDetail]]

    class Config:
        orm_mode = True


class PhotoAddTagsModel(BaseModel):
    tags: Optional[List[str]]


class TagResponseNew(BaseModel):
    detail: str = "Tags has been added to the photo"