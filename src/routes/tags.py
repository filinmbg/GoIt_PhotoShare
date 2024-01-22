from typing import List, Type
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.repository import tags as repository_tags
from src.database.db import get_db
from src.entity.models import User, Tag
from src.services.auth_service import auth_service
from src.repository import tags as repo_tags
from src.schemas.tag_schemas import TagModel, TagResponse, PhotoAddTagsModel, TagResponseNew
from src.conf import messages
from src.routes.photo_routes import allowed_operation_admin
from src.services.validator import validate_tags_count


router = APIRouter(tags=["Tags"])


@router.post('/{photo_id}', response_model=TagResponseNew)
async def add_tag_to_photo(photo_id: int, body: PhotoAddTagsModel, db: AsyncSession = Depends(get_db)):
    tags_list = await validate_tags_count(body.tags)
    return await repository_tags.add_tag_to_photo_(tags_list, photo_id, db)


@router.get("/{tag_id}", dependencies=[Depends(allowed_operation_admin)], response_model=TagResponse)
async def get_tag(tag_id: int, db: AsyncSession = Depends(get_db)):

    tag = await repository_tags.get_tag_by_id(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.put("/{tag_id}", dependencies=[Depends(allowed_operation_admin)], response_model=TagResponse)
async def update_tag(tag_id: int, body: TagModel, db: AsyncSession = Depends(get_db)):

    tag = await repository_tags.get_tag_by_id(tag_id, db)
    exist_tag = await repository_tags.get_tag_by_name(str(body.tag_name), db)
    if tag:
        if exist_tag:
            updated_tag = await repository_tags.update_tag(tag_id, body, db)
            return updated_tag
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="TAGNAME_ALREADY_EXIST")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TAGNAME_NOT_FOUND")


@router.delete("/{tag_id}", dependencies=[Depends(allowed_operation_admin)], status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):

    tag = await repository_tags.get_tag_by_id(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TAGNAME_NOT_FOUND")

    result = await repository_tags.remove_tag_by_id(tag_id, db)
    return result