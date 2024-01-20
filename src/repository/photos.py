from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User, Image
from src.services.auth_service import get_current_user
from cloudinary.uploader import upload
from cloudinary.api import delete_resources_by_tag, resources
from fastapi import UploadFile, File, Form
import uuid

router = APIRouter()


@router.post("/images", response_model=Image)
async def create_image(db: AsyncSession = Depends(get_db), file: UploadFile = File(), text: str = Form(...), user: User = Depends(get_current_user)):
    img_content = await file.read()
    public_id = f"image_{user.id}_{uuid.uuid4()}"

    # Завантаження на Cloudinary
    response = upload(
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


@router.get("/images/{image_id}", response_model=Image)
async def get_image(image_id: int, db: AsyncSession = Depends(get_db)):
    image = await db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.put("/images/{image_id}", response_model=Image)
async def update_image(image_id: int, text: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    image = await db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    if image.user_id != user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    image.description = text
    await db.commit()
    await db.refresh(image)
    return image


@router.delete("/images/{image_id}", response_model=dict)
async def delete_image(image_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    image = await db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    if image.user_id != user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    delete_resources_by_tag(f"image_{user.id}_{image.id}")

    db.delete(image)
    await db.commit()

    return {"message": "Image deleted successfully"}
