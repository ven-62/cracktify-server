import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from config import Config

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
