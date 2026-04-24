import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from app.config import Config

# Configuration
cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_SECRET_KEY,  # Click 'View API Keys' above to copy your API secret
    secure=True,
)


def upload_file(file_path, resource_type="auto"):
    """Uploads a file to Cloudinary."""
    try:
        resp = cloudinary.uploader.upload(
            file_path, use_filename=True, resource_type=resource_type
        )
        return resp

    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_file(url):
    """Delete the file asset from the cloud using url"""
    try:
        public_id = url.split("/")[-1].split(".")[0]  # Extract public_id from URL
        _ = cloudinary.uploader.destroy(public_id)

    except Exception as e:
        return {"success": False, "error": str(e)}