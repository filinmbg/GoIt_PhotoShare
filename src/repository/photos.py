from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.entity.models import User, Image, Tag
from sqlalchemy.ext.asyncio import AsyncSession
from src.conf.config import config
from src.conf import messages
from src.schemas.tag_schemas import TagModel
from cloudinary.uploader import upload
from src.repository.qrcode_generator import generate_qr_code
#from src.repository.tags import create_tag
from src.services.auth_service import get_current_user
import cloudinary.uploader
from cloudinary.uploader import destroy
import cloudinary.api
from fastapi import UploadFile, File, Form, HTTPException
import uuid


class Cloudinary:
    cloudinary.config(
        cloud_name=config.CLOUDINARY_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET,
        secure=True,
    )


# створення світлини
async def create_image(db: AsyncSession, file: UploadFile = File(), text: str = Form(...), user: User = None):
    img_content = await file.read()
    public_id = f"image_{user.id}_{uuid.uuid4()}"

    # Завантаження на Cloudinary
    response = cloudinary.uploader.upload(
        img_content, public_id=public_id, overwrite=True, folder="publication"
    )

    # Генерація QR-коду та збереження його в базі даних
    qr_code_content = generate_qr_code(response["secure_url"])
    qr_response = cloudinary.uploader.upload(
        qr_code_content, overwrite=True, folder="qrcodes"
    )

    # Зберігання в базі даних
    image = Image(
        user_id=user.id,
        url=response["secure_url"],
        public_id=public_id,
        description=text,
        qr_url=qr_response["secure_url"],
    )

    db.add(image)
    await db.commit()
    await db.refresh(image)

    return image


# отримувати світлину за унікальним посиланням в БД
async def get_image(image_id: int, session: AsyncSession):
    image = await session.execute(select(Image).filter(Image.id == image_id))
    image = image.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


async def update_image(image_id: int, new_description: str, db: Session):
    image = await db.execute(select(Image).filter(Image.id == image_id))
    image = image.scalar()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    image.description = new_description
    await db.commit()
    await db.refresh(image)

    return image


async def delete_image(image_id: int, db: AsyncSession, user: User = None):
    image = await db.execute(select(Image).filter(Image.id == image_id))
    image = image.scalar()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    if image.user_id != user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    try:
        destroy_result = destroy(public_id=image.public_id, resource_type="image")
        print("Cloudinary Destroy Result:", destroy_result)
    except Exception as e:
        print("Error during Cloudinary destroy:", str(e))

    await db.delete(image)
    await db.commit()

    return {"message": "Image deleted successfully"}


# async def add_tag(db: Session, user: User, image_id: int, tag_name: str):
#
#     image = db.query(Image).filter(Image.id == image_id).first()
#     if image is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND
#         )
#     if image.user_id != user.id:
#         raise HTTPException(status_code=403, detail=messages.NOT_ALLOWED)
#     if len(image.tags) >= 5:
#         raise HTTPException(
#             status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=messages.ONLY_FIVE_TAGS
#         )
#     tag = db.query(Tag).filter(Tag.tag_name == tag_name.lower()).first()
#
#     if tag is None:
#         tag_model = TagModel(tag_name=tag_name)
#         tag = await create_tag(tag_model, db)
#
#     image.tags.append(tag)
#
#     db.commit()
#     db.refresh(image)
#
#     return {"message": "Tag successfully added", "tag": tag.tag_name}

