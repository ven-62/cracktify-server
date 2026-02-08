import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from config import Config

# Configuration       
cloudinary.config( 
    cloud_name = Config.CLOUDINARY_CLOUD_NAME, 
    api_key = Config.CLOUDINARY_API_KEY, 
    api_secret = Config.CLOUDINARY_SECRET_KEY, # Click 'View API Keys' above to copy your API secret
    secure=True
)

def upload_file(file_path, public_id=None):
    """Uploads a file to Cloudinary."""
    if public_id:
        result = cloudinary.uploader.upload(file_path, public_id=public_id, resource_type="auto")
    else:
        result = cloudinary.uploader.upload(file_path, resource_type="auto")
    return result
