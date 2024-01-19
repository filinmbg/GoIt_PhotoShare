from src.entity.models import User, Image
from sqlalchemy.ext.asyncio import AsyncSession
from src.conf.config import config
from cloudinary.uploader import upload
from src.services.auth_service import get_current_user
import cloudinary.uploader
import cloudinary.api
from fastapi import UploadFile, File, Form
import uuid


class Cloudinary:
    cloudinary.config(
        cloud_name=config.CLOUDINARY_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET,
        secure=True,
    )


async def create_image(db: AsyncSession, file: UploadFile = File(), text: str = Form(...), user: User = None):
    img_content = await file.read()
    public_id = f"image_{user.id}_{uuid.uuid4()}"

    # Завантаження на Cloudinary
    response = cloudinary.uploader.upload(
        img_content, public_id=public_id, overwrite=True, folder="publication"
    )

    # Зберігання в базі даних
    image = Image(
        user_id=user.id,
        url=response["secure_url"],
        description=text,
        qr_url="",
    )

    db.add(image)
    await db.commit()
    await db.refresh(image)

    return image
