from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.repository.comments import create_comment, update_comment, delete_comment
from src.schemas.comment_schemas import CommentSchema, CommentsResponse
from src.database.db import get_db
from src.entity.models import User
from src.services.auth_service import get_current_user

router = APIRouter(prefix="/comments", tags=['comments'])


# Роут для створення коментарів
@router.post("/", response_model=CommentsResponse)
async def create_comments(photo_id: int, comment_data: CommentSchema,
                          current_user: User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    created_comment = await create_comment(db, photo_id, comment_data.comment, current_user)
    return created_comment


# Роут для редагування коментарів
@router.put("/{comment_id}/", response_model=CommentsResponse)
async def update_comments(comment_id: int, comment: CommentSchema,
                          current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_comment = await update_comment(db, comment_id, comment.comment, current_user)

    if updated_comment:
        return updated_comment
    else:
        raise HTTPException(status_code=404, detail="Comment not found or permission denied")


# Роут для видалення коментарів
@router.delete("/{comment_id}/", response_model=bool)
async def delete_comments(comment_id: int, current_user: User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    success = await delete_comment(db, comment_id, current_user)

    if success:
        return {"success": True}
    else:
        raise HTTPException(status_code=404, detail="Comment not found or permission denied")
