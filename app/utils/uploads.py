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

def upload_image(file_path, public_id=None):
    """Uploads an image to Cloudinary."""
    if public_id:
        result = cloudinary.uploader.upload(file_path, public_id=public_id)
    else:
        result = cloudinary.uploader.upload(file_path)
    return result


if __name__ == "__main__":
    # Upload an image
    upload_result = cloudinary.uploader.upload("C:\\Users\\Admin\\School\\Coding Course\\Software Engineering 2\\midterm\\Cracktify\\server\\app\\utils\\Still 2025-11-23 095316_1.1.1.jpg", public_id="chickens")
    print(upload_result["secure_url"])

    # Optimize delivery by resizing and applying auto-format and auto-quality
    # optimize_url, _ = cloudinary_url("shoes", fetch_format="auto", quality="auto")
    # print(optimize_url)

    # # Transform the image: auto-crop to square aspect_ratio
    # auto_crop_url, _ = cloudinary_url("shoes", width=500, height=500, crop="auto", gravity="auto")
    # print(auto_crop_url)