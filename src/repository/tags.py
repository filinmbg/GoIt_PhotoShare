from fastapi import HTTPException
from typing import List, Type
# from photos import app, photos_db


from sqlalchemy.orm import Session

from src.entity.models import Tag
from src.schemas.tag_schemas import TagModel

# @app.post("/photos/{photo_id}/add-tags/")
# async def add_tags_to_photo(photo_id: int, tags: List[str]):
#     if photo_id < 0 or photo_id >= len(photos_db):
#         raise HTTPException(status_code=404, detail="Photo not found")
#     if len(photos_db[photo_id].tags) + len(tags) > 5:
#         raise HTTPException(status_code=400, detail="Cannot add more than 5 tags")
#     photos_db[photo_id].tags.extend(tags)
#     return {"message": "Tags added successfully"}




async def create_tag(body: TagModel, db: Session) -> Tag:

    tag = Tag(tag_name=body.tag_name.lower())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def get_tag_by_id(tag_id: int, db: Session) -> Tag | None:

    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    return tag


async def get_tag_by_name(tag_name: str, db: Session) -> Tag | None:

    tag = db.query(Tag).filter(Tag.tag_name == tag_name).first()
    return tag


async def get_tags(db: Session) -> List[Type[Tag]]:

    tags = db.query(Tag).all()
    return tags


async def update_tag(tag_id: int, body: TagModel, db: Session) -> Tag | None:

    tag = await get_tag_by_id(tag_id, db)
    if not tag:
        return None
    tag.tag_name = body.tag_name.lower()
    db.commit()
    return tag


async def remove_tag_by_id(tag_id: int, db: Session) -> Tag | None:

    tag = await get_tag_by_id(tag_id, db)
    if tag:
        db.delete(tag)
        db.commit()
    return tag


async def remove_tag_by_name(tag_name: str, db: Session) -> Tag | None:

    tag = await get_tag_by_name(tag_name, db)
    if tag:
        db.delete(tag)
        db.commit()
    return tag
