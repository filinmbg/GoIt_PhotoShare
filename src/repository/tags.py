from fastapi import HTTPException
from typing import List
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.services.validator import validate_tags_count
from src.routes.photo_routes import get_image
from src.entity.models import Tag, image_m2m_tag
from src.schemas.tag_schemas import TagModel


async def add_tags_to_photo(tags: List[str], photo_id: int, session: AsyncSession):
    result = []
    for tag in tags:
        query = select(Tag).where(Tag.tag_name == tag)
        tag_result = await session.execute(query)
        tag_obj = tag_result.scalar_one_or_none()
        if not tag_obj:
            query_ = insert(Tag).values(tag_name=tag).returning(Tag)
            tag_insert_result = await session.execute(query_)
            tag_obj = tag_insert_result.scalar_one()

        try:
            query = insert(image_m2m_tag).values(tag_id=tag_obj.id, image_id=photo_id).returning(image_m2m_tag)
            image_m2m_tag_insert_result = await session.execute(query)  # Виправлене ім'я змінної
            image_m2m_tag_obj = image_m2m_tag_insert_result.scalar_one()

        except Exception as err:
            if str(err).find("duplicate key") < 0:
                raise

        result.append(tag_obj)

    await session.commit()
    return result


async def get_tags_photo(photo_id: int, db: AsyncSession):
    tquery = select(Tag).join(image_m2m_tag).where(Tag.id == image_m2m_tag.c.tag_id).where(
        image_m2m_tag.c.image_id == photo_id)
    result = await db.execute(tquery)
    tags = result.scalars().all()
    if tags:
        return tags
    else:
        return False


async def add_tag_to_photo_(tags: List[str], photo_id: int, db: AsyncSession):
    tags_photo = await get_tags_photo(photo_id, db)
    if not tags_photo:
        await validate_tags_count(tags=tags)
        await add_tags_to_photo(tags, photo_id, db)
        photo = await get_image(photo_id, db)
        await db.commit()
        return photo


async def get_tags(db: AsyncSession):
    tags = db.query(Tag).all()
    return tags


async def get_tag_by_id(tag_id: int, db: AsyncSession) -> Tag | None:
    tag = await db.execute(select(Tag).filter(Tag.id == tag_id))
    tag = tag.scalar()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


async def get_tag_by_name(tag_name: str, db: AsyncSession) -> Tag | None:
    tag = await db.execute(select(Tag).filter(Tag.tag_name == tag_name))
    tag = tag.scalar()
    if not tag:
        return True
    else:
        return False


async def update_tag(tag_id: int, body: TagModel, db: AsyncSession) -> Tag | None:
    tag = await get_tag_by_id(tag_id, db)
    if not tag:
        return None
    tag.tag_name = body.tag_name.lower()
    await db.commit()
    await db.refresh(tag)
    return tag


async def remove_tag_by_id(tag_id: int, db: AsyncSession) -> Tag | None:
    tag = await get_tag_by_id(tag_id, db)
    if tag:
        await db.delete(tag)
        await db.commit()
    return {"message": "tag deleted successfully"}


async def remove_tag_by_name(tag_name: str, db: AsyncSession) -> Tag | None:
    tag = await get_tag_by_name(tag_name, db)
    if tag:
        await db.delete(tag)
        await db.commit()
    return {"message": "tag deleted successfully"}
