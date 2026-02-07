import shutil
import tempfile

from fastapi import APIRouter, File, UploadFile
from app.utils.uploads import upload_image

router = APIRouter()

@router.post("/file")
async def handle_upload_file(file: UploadFile = File(...)):
    """Endpoint to upload an image to Cloudinary."""

    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    # Upload the image to Cloudinary
    result = upload_image(temp_file_path)

    return {"message": True, "url": result["secure_url"], "type": result["resource_type"]}