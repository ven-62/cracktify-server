import os, json, base64
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    # Database Configuration
    DB_HOST = os.getenv("SQLHOST")
    DB_USER = os.getenv("SQLUSER")
    DB_PASSWORD = os.getenv("SQLPASSWORD")
    DB_NAME = os.getenv("SQLDATABASE")
    DB_PORT = int(os.getenv("SQLPORT", 5432))  # Default to 5432 for PostgreSQL

    # Gmail API Credentials
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
