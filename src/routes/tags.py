from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from src.repository import tags as repository_tags
from src.database.db import get_db

from src.schemas.tag_schemas import TagModel, TagResponse, PhotoAddTagsModel, TagResponseNew
from src.routes.photo_routes import allowed_operation_admin
from src.services.validator import validate_tags_count

router = APIRouter(tags=["Tags"])


router = APIRouter(tags=["Tags"])

@router.post('/{photo_id}', response_model=TagResponseNew)
async def add_tag_to_photo(photo_id: int, body: PhotoAddTagsModel, db: AsyncSession = Depends(get_db)):
    """
    The add_tag_to_photo function adds tags to a photo.
        The function takes in the following parameters:
            - photo_id: int, the id of the photo that will be tagged.
            - body: PhotoAddTagsModel, a model containing all of the tags that will be added to this specific photo.

    :param photo_id: int: Identify the photo to which we want to add tags
    :param body: PhotoAddTagsModel: Validate the tags list
    :param db: AsyncSession: Pass the database connection to the function
    :return: A list of tags that were added to the photo
    :doc-author: Trelent
    """

    tags_list = await validate_tags_count(body.tags)
    return await repository_tags.add_tag_to_photo_(tags_list, photo_id, db)


@router.get("/{tag_id}", dependencies=[Depends(allowed_operation_admin)], response_model=TagResponse)
async def get_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    """
    The get_tag function is a GET request that returns the tag with the given ID.
    If no such tag exists, it raises an HTTPException with status code 404 and a detail message.

    :param tag_id: int: Get the tag_id from the url
    :param db: AsyncSession: Pass the database session to the function
    :return: A tag object, which is defined in models
    :doc-author: Trelent
    """
    tag = await repository_tags.get_tag_by_id(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.put("/{tag_id}", dependencies=[Depends(allowed_operation_admin)], response_model=TagResponse)
async def update_tag(tag_id: int, body: TagModel, db: AsyncSession = Depends(get_db)):
    """
    The update_tag function updates a tag in the database.
        Args:
            tag_id (int): The id of the tag to update.
            body (TagModel): The updated data for the specified TagModel object.

    :param tag_id: int: Get the tag_id from the url
    :param body: TagModel: Get the tag_name and description of the tag
    :param db: AsyncSession: Get the database session
    :return: The updated tag
    :doc-author: Trelent
    """
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
    """
    The delete_tag function deletes a tag from the database.

    :param tag_id: int: Specify the tag_id of the tag to be deleted
    :param db: AsyncSession: Get a database session
    :return: The number of rows affected by the delete statement
    :doc-author: Trelent
    """
    tag = await repository_tags.get_tag_by_id(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TAGNAME_NOT_FOUND")

    result = await repository_tags.remove_tag_by_id(tag_id, db)

    return result

