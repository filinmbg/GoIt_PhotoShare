from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.schemas.photo_schemas import PostSingle, GetSingle, PutSingle, DeleteSingle
from src.services.auth_service import get_current_user
from src.repository.photos import create_image, get_image, update_image, delete_image
from src.entity.models import User

router = APIRouter(prefix='/photos', tags=['photos'])


@router.post("/",
             response_model=PostSingle,
             status_code=status.HTTP_201_CREATED)
async def create_images(
        db: AsyncSession = Depends(get_db),
        file: UploadFile = File(),
        text: str = Form(...),
        user: User = Depends(get_current_user)
):
    try:
        created_image = await create_image(db, file, text, user)
        return created_image
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{image_id}", response_model=GetSingle)
async def get_images(
        image_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    try:
        image = await get_image(db, image_id)
        return image
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{image_id}", response_model=PutSingle)
async def update_images(
        image_id: int,
        text: str,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    try:
        updated_image = await update_image(db, image_id, text, user)
        return updated_image
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{image_id}", response_model=DeleteSingle)
async def delete_images(
        image_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    try:
        deleted_image = await delete_image(db, image_id, user)
        return deleted_image
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
