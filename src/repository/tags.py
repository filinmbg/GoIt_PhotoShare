from fastapi import HTTPException
from typing import List
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.validator import validate_tags_count
from src.routes.photo_routes import get_image
from src.entity.models import Tag, image_m2m_tag
from src.schemas.tag_schemas import TagModel


async def add_tags_to_photo(tags: List[str], photo_id: int, session: AsyncSession):
    """
    The add_tags_to_photo function adds tags to a photo.

    :param tags: List[str]: Pass a list of tags to the function
    :param photo_id: int: Specify the photo to which tags are added
    :param session: AsyncSession: Pass the database session to the function
    :return: A list of tag objects
    :doc-author: Trelent
    """
    result = []
    for tag in tags:
        query = select(Tag).where(Tag.tag_name == tag)
        tag_result = await session.execute(query)
        tag_obj = tag_result.scalar_one_or_none()
        if not tag_obj:
            query_ = insert(Tag).values(tag_name=tag).returning(Tag)
            tag_insert_result = await session.execute(query_)
            tag_obj = tag_insert_result.scalar_one()

        try:
            query = insert(image_m2m_tag).values(tag_id=tag_obj.id, image_id=photo_id).returning(image_m2m_tag)
            image_m2m_tag_insert_result = await session.execute(query)  # Виправлене ім'я змінної
            image_m2m_tag_obj = image_m2m_tag_insert_result.scalar_one()

        except Exception as err:
            if str(err).find("duplicate key") < 0:
                raise

        result.append(tag_obj)

    await session.commit()
    return result


async def get_tags_photo(photo_id: int, db: AsyncSession):
    """
    The get_tags_photo function takes a photo_id and an async database session as arguments.
    It then creates a query that selects all tags associated with the given photo_id,
    and executes it on the database. The result is returned as an array of tag names.

    :param photo_id: int: Specify the photo id of the image to be tagged
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of tags or false if there are no tags for the photo
    :doc-author: Trelent
    """
    tquery = select(Tag).join(image_m2m_tag).where(Tag.id == image_m2m_tag.c.tag_id).where(
        image_m2m_tag.c.image_id == photo_id)
    result = await db.execute(tquery)
    tags = result.scalars().all()
    if tags:
        return tags
    else:
        return False


async def add_tag_to_photo_(tags: List[str], photo_id: int, db: AsyncSession):
    """
    The add_tag_to_photo_ function adds tags to a photo.
        Args:
            tags (List[str]): A list of strings representing the tag(s) to be added.
            photo_id (int): The id of the photo that will have its tags updated.

    :param tags: List[str]: Pass in a list of tags to be added to the photo
    :param photo_id: int: Identify the photo to be tagged
    :param db: AsyncSession: Pass the database session to the function
    :return: The photo object
    :doc-author: Trelent
    """
    tags_photo = await get_tags_photo(photo_id, db)
    if not tags_photo:
        await validate_tags_count(tags=tags)
        await add_tags_to_photo(tags, photo_id, db)
        photo = await get_image(photo_id, db)
        await db.commit()
        return photo


async def get_tags(db: AsyncSession):
    """
    The get_tags function searches for tags in the database
    :param db: AsyncSession: Pass the database session to the function
    :return: A tag
    """
    tags = db.query(Tag).all()
    return tags


async def get_tag_by_id(tag_id: int, db: AsyncSession) -> Tag | None:
    """
    The get_tag_by_id function returns a tag by its id.

    :param tag_id: int: Specify the id of the tag we want to get
    :param db: AsyncSession: Pass the database session to the function
    :return: A tag or none
    :doc-author: Trelent
    """
    tag = await db.execute(select(Tag).filter(Tag.id == tag_id))
    tag = tag.scalar()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


async def get_tag_by_name(tag_name: str, db: AsyncSession) -> Tag | None:
    """
    The get_tag_by_name function takes in a tag_name and an AsyncSession object.
    It then queries the database for a Tag with that name, returning it if found, or None if not.

    :param tag_name: str: Specify the name of the tag you want to get
    :param db: AsyncSession: Pass in the database session
    :return: A tag object if it exists, or none if it does not
    :doc-author: Trelent
    """
    tag = await db.execute(select(Tag).filter(Tag.tag_name == tag_name))
    tag = tag.scalar()
    if not tag:
        return True
    else:
        return False


async def update_tag(tag_id: int, body: TagModel, db: AsyncSession) -> Tag | None:
    """
    The update_tag function updates a tag in the database.
        Args:
            tag_id (int): The id of the tag to update.
            body (TagModel): A TagModel object containing the new values for this tag.

    :param tag_id: int: Identify the tag that is to be deleted
    :param body: TagModel: Create a new tag object
    :param db: AsyncSession: Pass in the database session
    :return: A tag object if the update was successful, none otherwise
    :doc-author: Trelent
    """
    tag = await get_tag_by_id(tag_id, db)
    if not tag:
        return None
    tag.tag_name = body.tag_name.lower()
    await db.commit()
    await db.refresh(tag)
    return tag


async def remove_tag_by_id(tag_id: int, db: AsyncSession) -> Tag | None:
    """
    The remove_tag_by_id function removes a tag from the database by its id.
        Args:
            tag_id (int): The id of the tag to be removed.
            db (AsyncSession): An async session object for interacting with the database.

    :param tag_id: int: Specify the id of the tag to be deleted
    :param db: AsyncSession: Pass in the database session
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    tag = await get_tag_by_id(tag_id, db)
    if tag:
        await db.delete(tag)
        await db.commit()
    return {"message": "tag deleted successfully"}


async def remove_tag_by_name(tag_name: str, db: AsyncSession) -> Tag | None:
    """
    remove_tag_by_name function removes a tag from the database by name.
    Args:
    tag_name (str): The name of the tag to be removed.
    db (AsyncSession): An async session object for interacting with the database.

    :param tag_name: str: Specify name of the tag to be deleted
    :param db: AsyncSession: Pass in the database session
    :return: A dictionary with a message
    """
    tag = await get_tag_by_name(tag_name, db)
    if tag:
        await db.delete(tag)
        await db.commit()
    return {"message": "tag deleted successfully"}
