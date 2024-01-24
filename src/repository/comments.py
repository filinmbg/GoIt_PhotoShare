from sqlalchemy.future import select
from src.entity.models import Comment, User
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


async def create_comment(db: AsyncSession, image_id: int, comment_text: str, user: User):
    """
    The create_comment function creates a new comment in the database.


    :param db: AsyncSession: Pass the database session to the function
    :param image_id: int: Identify the image to which the comment is added
    :param comment_text: str: Pass the text of the comment to be created
    :param user: User: Get the user_id of the comment author
    :return: A comment object
    :doc-author: Trelent
    """
    comment = Comment(comment=comment_text, image_id=image_id, user_id=user.id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)  # Оновлення об'єкта коментаря після збереження
    return comment


async def update_comment(db: AsyncSession, comment_id: int, text: str, user: User):
    """
    The update_comment function updates a comment in the database.

    :param db: AsyncSession: Pass the database session to the function
    :param comment_id: int: Find the comment in the database
    :param text: str: Update the comment text
    :param user: User: Check if the user is an admin or not
    :return: The updated comment if the operation was successful, otherwise it returns none
    :doc-author: Trelent
    """
    comment = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = comment.scalar()

    if not comment:
        return None

    if user.role.name == "user" and comment.user_id != user.id:
        return None

    comment.comment = text
    comment.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(comment)

    return comment


async def delete_comment(db: AsyncSession, comment_id: int, user: User):
    """
    The delete_comment function deletes a comment from the database.
        Args:
            db (AsyncSession): The database session to use for querying.
            comment_id (int): The id of the comment to delete.
            user (User): The user who is deleting the comment, used for authorization purposes.

    :param db: AsyncSession: Pass a database session to the function
    :param comment_id: int: Select the comment to be deleted from the database
    :param user: User: Check if the user is an admin or moderator
    :return: True if the comment was deleted, and false otherwise
    :doc-author: Trelent
    """
    comment = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment_ = comment.scalar()

    if not comment_:
        return False

    if user.role.name == "user" and comment_.user_id == user.id:
        return False

    if user.role.name == "admin" or user.role.name == "moderator":
        await db.delete(comment_)
        await db.commit()
        return True
