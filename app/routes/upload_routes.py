import os
import shutil
import tempfile

from fastapi import APIRouter, File, UploadFile, HTTPException
from app.utils.uploads import upload_image

router = APIRouter()

@router.post("/file")
async def handle_upload_file(file: UploadFile = File(...)):
    temp_file_path = None

    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        # Upload to Cloudinary
        result = upload_image(temp_file_path)

        return {
            "success": True,
            "url": result["secure_url"],
            "type": result["resource_type"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # ALWAYS cleanup
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
