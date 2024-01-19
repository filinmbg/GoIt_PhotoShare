from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.schemas.photo_schemas import PostSingle
from src.services.auth_service import get_current_user
from src.repository.photos import create_image
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
