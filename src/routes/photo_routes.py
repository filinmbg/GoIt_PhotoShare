from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from GoIt_PhotoShare.src.database.db import get_db
from GoIt_PhotoShare.src.entity.models import Image

from GoIt_PhotoShare.src.schemas.photo_schemas import ImageResponse, ImageUpload
import os

router = APIRouter(prefix='/images', tags=['images'])


@router.post("/", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
        image_data: ImageUpload,
        file: UploadFile = File(),
        db: AsyncSession = Depends(get_db),
        uploads_dir: str = "uploads",
        max_file_size: int = 1_000_000
) -> ImageResponse:
    file_path = await handle_uploaded_file(file, uploads_dir, max_file_size)

    image = Image(**image_data.dict(exclude={"tags"}))
    image.file_path = file_path

    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image


async def handle_uploaded_file(file: UploadFile, uploads_dir: str, max_file_size: int) -> str:
    file_path = f"{uploads_dir}/{file.filename}"
    file_size = 0

    try:
        async with file.file as f:
            while True:
                chunk = await f.read(1024)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > max_file_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File size is over the limit: {max_file_size}"
                    )
                with open(file_path, "ab") as file_buffer:
                    file_buffer.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
    return file_path
