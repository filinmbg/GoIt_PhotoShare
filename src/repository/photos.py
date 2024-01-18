from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from src.entity.models import Image
from datetime import datetime
from typing import List


async def create_image(db: AsyncSession, image_data: dict) -> Image:
    try:
        image = Image(**image_data)
        db.add(image)
        await db.commit()
        await db.refresh(image)
        return image
    except Exception as e:
        raise ValueError(f"Error creating image: {str(e)}")


async def get_image(image_id: int, db: AsyncSession) -> Image:
    stmt = select(Image).where(Image.id == image_id).options(selectinload(Image.tags))
    result = await db.execute(stmt)
    image = result.scalar()

    if image is None:
        raise ValueError("Image not found")
    return image


async def update_image(image_id: int, image_data: dict, db: AsyncSession) -> Image:
    stmt = select(Image).where(Image.id == image_id)
    result = await db.execute(stmt)
    image = result.scalar()

    if image is None:
        raise ValueError("Image not found")

    if image_data:
        for field, value in image_data.items():
            setattr(image, field, value)

        await db.commit()
        await db.refresh(image)

    return image


async def delete_image(image_id: int, db: AsyncSession) -> Image:
    stmt = select(Image).where(Image.id == image_id)
    result = await db.execute(stmt)
    image = result.scalar()

    if image is None:
        raise ValueError("Image not found")

    try:
        db.delete(image)
        await db.commit()
        return image
    except Exception as e:
        raise ValueError(f"Error deleting image: {str(e)}")


async def list_images(skip: int = 0, limit: int = 10, db: AsyncSession = None) -> List[Image]:
    stmt = select(Image).offset(skip).limit(limit)
    result = await db.execute(stmt)
    images = result.scalars().all()
    return images
