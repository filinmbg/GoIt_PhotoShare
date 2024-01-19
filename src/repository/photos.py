from src.entity.models import User, Image
from sqlalchemy.ext.asyncio import AsyncSession
from src.conf.config import config
from cloudinary.uploader import upload
from src.repository.qrcode_generator import generate_qr_code
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

    # Генерація QR-коду та збереження його в базі даних
    qr_code_content = generate_qr_code(response["secure_url"])
    qr_public_id = f"qrcode_{user.id}_{uuid.uuid4()}"
    qr_response = cloudinary.uploader.upload(
        qr_code_content, public_id=qr_public_id, overwrite=True, folder="qrcodes"
    )

    # Зберігання в базі даних
    image = Image(
        user_id=user.id,
        url=response["secure_url"],
        description=text,
        qr_url=qr_response["secure_url"],
    )

    db.add(image)
    await db.commit()
    await db.refresh(image)

    return image
