from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas.photo_schemas import PostSingle, GetSingle, PutSingle, DeleteSingle
from src.services.auth_service import get_current_user
from src.repository.photos import create_image, get_image, update_image, delete_image
from src.entity.models import User, Role
from src.services.role_service import RoleAccess

router = APIRouter(prefix='/photos', tags=['Photos'])

allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_read = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_delete = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.post("/",
             response_model=PostSingle,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_operation_create)])
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


@router.get("/{photo_id}",
            response_model=GetSingle,
            dependencies=[Depends(allowed_operation_read)])
async def get_images(
        image_id: int,
        session: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    try:
        image = await get_image(image_id, session)
        return image
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{photo_id}",
            response_model=PutSingle,
            dependencies=[Depends(allowed_operation_update)])
async def update_images(
        image_id: int,
        text: str,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    try:
        updated_image = await update_image(image_id, text, db)
        return updated_image
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{photo_id}",
               response_model=DeleteSingle,
               dependencies=[Depends(allowed_operation_delete)])
async def delete_images(
        image_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)
):
    try:
        if user.role in allowed_operation_admin.allowed_roles:
            deleted_image = await delete_image(image_id, db, user)
            return deleted_image
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

