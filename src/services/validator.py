from typing import List
from fastapi import HTTPException, status
from src.conf.config import config


async def validate_tags_count(tags: List[str]):
    tags_list = []

    if tags:
        tags_list.extend(tags)
    if len(tags_list) > 0:
        tags_list = list(set(tags_list))
    if len(tags_list) > config.MAX_TAGS_COUNT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Too many tags. Allowed: {config.MAX_TAGS_COUNT}")

    return tags_list
