import os, json, base64
from dotenv import load_dotenv

import cloudinary

# Load .env file
load_dotenv()

class Config:
    # Database
    DB_HOST = os.getenv("MYSQLHOST")
    DB_USER = os.getenv("MYSQLUSER")
    DB_PASSWORD = os.getenv("MYSQLPASSWORD")
    DB_NAME = os.getenv("MYSQLDATABASE")
    DB_PORT = int(os.getenv("MYSQLPORT", 3306))

    CREDS_INFO = json.loads(
        base64.b64decode(os.getenv("GMAIL_CREDENTIALS")).decode("utf-8")
    )

    TOKEN_INFO = json.loads(
        base64.b64decode(os.getenv("GMAIL_TOKEN")).decode("utf-8")
    )

    # JWT Settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_SECRET_KEY = os.getenv("CLOUDINARY_SECRET_KEY")

    DEFAULT_BASE64_AVATAR = os.getenv("DEFAULT_BASE64_AVATAR", "")

