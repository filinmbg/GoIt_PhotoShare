from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.repository.comments import create_comment, update_comment, delete_comment
from src.schemas.comment_schemas import CommentSchema, CommentsResponse, UserResponse
from src.database.db import get_db
from src.services.auth_service import get_current_user

router = APIRouter(prefix="/comments", tags=['comments'])


# Роут для створення коментарів
@router.post("/", response_model=CommentsResponse)
async def create_comment(photo_id: int, comment: CommentSchema, current_user: UserResponse = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    return create_comment(db, photo_id, comment.text, current_user)


# Роут для редагування коментарів
@router.put("/{comment_id}/", response_model=CommentsResponse)
async def update_comment(comment_id: int, comment: CommentSchema,
                         current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_comment = update_comment(db, comment_id, comment.text, current_user)

    if updated_comment:
        return updated_comment
    else:
        raise HTTPException(status_code=404, detail="Comment not found or permission denied")


# Роут для видалення коментарів
@router.delete("/{comment_id}/")
async def delete_comment(comment_id: int, current_user: UserResponse = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    success = delete_comment(db, comment_id, current_user)

    if success:
        return {"success": True}
    else:
        raise HTTPException(status_code=404, detail="Comment not found or permission denied")
