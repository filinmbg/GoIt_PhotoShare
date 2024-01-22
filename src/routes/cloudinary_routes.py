from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
from cloudinary.uploader import upload
import cloudinary.api
import cloudinary.utils

from src.database.db import get_db
from src.entity.models import Image
from src.services.cloudinary_service import cloudinary

router = APIRouter(prefix='/transformed_image', tags=["Cloudinary"])


@router.get("/{image_id}")
async def transform_and_update_image(image_id: int, angle: int = 45, db: AsyncSession = Depends(get_db)):
    image = await db.execute(select(Image).filter(Image.id == image_id))
    image = image.scalar()

    if image:
        url = image.url
        public_id = cloudinary.utils.cloudinary_url(url)[0].split("/")[-1]

        folder_path = "transform"
        transformation = {"angle": angle}

        public_id = f"{folder_path}/{public_id}"

        response = upload(url, transformation=transformation, public_id=public_id)

        transformed_image_url = response['secure_url']

        stmt = (
            update(Image)
            .where(Image.id == image_id)
            .values(transformed_url=transformed_image_url)
            .returning(Image)
        )

        await db.execute(stmt)
        await db.commit()

        return {
            "message": f"Image transformed and updated successfully. Rotated by {angle} degrees.",
            "transformed_image_url": transformed_image_url
        }

    raise HTTPException(status_code=404, detail="Image not found.")


