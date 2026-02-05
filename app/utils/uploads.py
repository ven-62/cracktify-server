import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from config import Config

# Configuration       
cloudinary.config( 
    cloud_name = "ddting2vc", 
    api_key = "762886399562366", 
    api_secret = Config.CLOUDINARY_SECRET_KEY, # Click 'View API Keys' above to copy your API secret
    secure=True
)

def upload_image(file_path):
    """Uploads an image to Cloudinary."""
    result = cloudinary.uploader.upload(file_path)
    return result


if __name__ == "__main__":
    # Upload an image
    upload_result = cloudinary.uploader.upload("https://res.cloudinary.com/demo/image/upload/getting-started/shoes.jpg",
                                            public_id="shoes")
    print(upload_result["secure_url"])

    # Optimize delivery by resizing and applying auto-format and auto-quality
    optimize_url, _ = cloudinary_url("shoes", fetch_format="auto", quality="auto")
    print(optimize_url)

    # Transform the image: auto-crop to square aspect_ratio
    auto_crop_url, _ = cloudinary_url("shoes", width=500, height=500, crop="auto", gravity="auto")
    print(auto_crop_url)