from fastapi import HTTPException
from typing import List
from photos import app, photos_db

@app.post("/photos/{photo_id}/add-tags/")
async def add_tags_to_photo(photo_id: int, tags: List[str]):
    if photo_id < 0 or photo_id >= len(photos_db):
        raise HTTPException(status_code=404, detail="Photo not found")
    if len(photos_db[photo_id].tags) + len(tags) > 5:
        raise HTTPException(status_code=400, detail="Cannot add more than 5 tags")
    photos_db[photo_id].tags.extend(tags)
    return {"message": "Tags added successfully"}