from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.comments import create_comment, update_comment, delete_comment
from src.schemas.comment_schemas import CommentSchema, CommentsResponse
from src.database.db import get_db
from src.entity.models import User
from src.services.auth_service import get_current_user

router = APIRouter(prefix="/comments", tags=['comments'])


# Роут для створення коментарів
@router.post("/", response_model=CommentsResponse, status_code=status.HTTP_201_CREATED)
async def create_comments(comment_data: CommentSchema, image_id: int,
                          current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    """
    The create_comments function creates a new comment for an image.
        The function takes in the following parameters:
            - comment_data: A CommentSchema object containing the data of the new comment to be created.
            - image_id: An integer representing the id of an existing Image object that will have a
                new Comment associated with it. This is passed as part of the URL path, and not as part
                of JSON request body like other parameters are.

    :param comment_data: CommentSchema: Validate the json data passed in with the request
    :param image_id: int: Get the image id from the url
    :param current_user: User: Get the user who is currently logged in
    :param db: AsyncSession: Get the database session
    :return: A comment object
    :doc-author: Trelent
    """
    try:
        created_comment = await create_comment(db, image_id, comment_data.comment, current_user)
        return created_comment
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Роут для редагування коментарів
@router.put("/{comment_id}/", response_model=CommentsResponse)
async def update_comments(comment_id: int, comment: CommentSchema,
                          current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    The update_comments function updates a comment in the database.
        It takes a comment_id and CommentSchema as input, and returns an updated CommentSchema object.
        If the update is successful, it will return an HTTP 200 status code with the updated CommentSchema object.
        If not, it will return either an HTTP 404 status code if no such comment exists or 403 if permission is denied.

    :param comment_id: int: Specify the comment to update
    :param comment: CommentSchema: Get the comment data from the request body
    :param current_user: User: Get the current user from the request
    :param db: AsyncSession: Get the database session
    :return: A commentschema object
    :doc-author: Trelent
    """
    updated_comment = await update_comment(db, comment_id, comment.comment, current_user)

    if updated_comment:
        return updated_comment
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found or permission denied")


# Роут для видалення коментарів
@router.delete("/{comment_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comments(comment_id: int, current_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    """
    The delete_comments function deletes a comment from the database.
        The function takes in an integer representing the id of the comment to be deleted, and returns a boolean value
        indicating whether or not it was successful.

    :param comment_id: int: Get the comment id from the url
    :param current_user: User: Get the current user from the database
    :param db: AsyncSession: Pass in the database session
    :return: A boolean value
    :doc-author: Trelent
    """
    success = await delete_comment(db, comment_id, current_user)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found or permission denied")
