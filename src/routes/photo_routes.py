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
    """
    The create_images function creates a new image in the database.

    :param db: AsyncSession: Get the database session
    :param file: UploadFile: Get the file from the request
    :param text: str: Get the text from the form
    :param user: User: Get the current user
    :return: A dictionary with the following keys:
    :doc-author: Trelent
    """
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
    """
    The get_images function is a GET request that returns the image with the given ID.
        The function takes in an image_id, which is used to query for the desired image.
        If no such image exists, then a 404 error will be returned.

    :param image_id: int: Specify the image id of the image to be retrieved
    :param session: AsyncSession: Get the database session
    :param user: User: Get the current user from the database
    :return: A list of images
    :doc-author: Trelent
    """
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
    """
    The update_images function is used to update the text of an image.
        The function takes in three parameters:
            - image_id: int, the id of the image that will be updated.
            - text: str, a string containing new text for the specified image.
            - db: Session = Depends(get_db), a database session object that allows us to interact with our database.

    :param image_id: int: Identify the image that will be updated
    :param text: str: Update the text of an image
    :param db: Session: Pass the database session to the function
    :param user: User: Get the user object from the token
    :return: A list of images
    :doc-author: Trelent
    """
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
    """
    The delete_images function deletes an image from the database.
        Args:
            image_id (int): The id of the image to be deleted.
            db (AsyncSession, optional): An async session object for interacting with a PostgreSQL database. Defaults to Depends(get_db).
            user (User, optional): A User object containing information about the current user's session and permissions level. Defaults to Depends(get_current_user).

    :param image_id: int: Specify the image id of the image that is to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Check if the user is allowed to delete images
    :return: A list of images that have been deleted
    :doc-author: Trelent
    """
    try:
        if user.role in allowed_operation_admin.allowed_roles:
            deleted_image = await delete_image(image_id, db, user)
            return deleted_image
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
