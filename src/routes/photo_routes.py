from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class Photo(BaseModel):
    url: str
    description: str
    tags: Optional[List[str]] = []

photos_db = []

@router.post("/photos/")
async def create_photo(photo: Photo):
    photos_db.append(photo)
    return {"message": "Photo uploaded successfully"}

@router.delete("/photos/{photo_id}")
async def delete_photo(photo_id: int):
    if photo_id < 0 or photo_id >= len(photos_db):
        raise HTTPException(status_code=404, detail="Photo not found")
    del photos_db[photo_id]
    return {"message": "Photo deleted successfully"}

@router.put("/photos/{photo_id}")
async def update_photo(photo_id: int, updated_photo: Photo):
    if photo_id < 0 or photo_id >= len(photos_db):
        raise HTTPException(status_code=404, detail="Photo not found")
    photos_db[photo_id] = updated_photo
    return {"message": "Photo updated successfully"}

@router.get("/photos/{photo_id}")
async def get_photo(photo_id: int):
    if photo_id < 0 or photo_id >= len(photos_db):
        raise HTTPException(status_code=404, detail="Photo not found")
    return photos_db[photo_id]
