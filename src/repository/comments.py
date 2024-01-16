from sqlalchemy.orm import Session
from datetime import datetime
from src.schemas.comment_schemas import CommentSchema
from src.entity.models import Comment, User


def create_comment(db: Session, photo_id: int, text: str, user: User):
    comment = Comment(text=text, photo_id=photo_id, user=user)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def update_comment(db: Session, comment_id: int, text: str, user: User):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        return None

    if user.role == "user" and comment.user_id != user.id:
        return None

    comment.text = text
    comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(comment)

    return comment


def delete_comment(db: Session, comment_id: int, user: User):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        return False

    if user.role == "user" and comment.user_id != user.id:
        return False

    db.delete(comment)
    db.commit()

    return True