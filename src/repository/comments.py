from sqlalchemy.orm import Session
from datetime import datetime
from src.entity.models import Comment, User


async def create_comment(db: Session, photo_id: int, text: str, user: User):
    comment_entity = Comment(comment=text, photo_id=photo_id, user=user)

    db.add(comment_entity)
    db.commit()
    db.refresh(comment_entity)

    return comment_entity


async def update_comment(db: Session, comment_id: int, text: str, user: User):
    comment_entity = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment_entity:
        return None

    if user.role == "user" and comment_entity.user_id != user.id:
        return None

    comment_entity.comment = text
    comment_entity.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(comment_entity)

    return comment_entity


async def delete_comment(db: Session, comment_id: int, user: User):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        return False

    if user.role == "user" and comment.user_id != user.id:
        return False

    db.delete(comment)
    db.commit()

    return True
