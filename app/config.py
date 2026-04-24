import os, json, base64
from app.utils.secrets import get_secret

secrets = get_secret() # Fetch secrets from AWS Secrets Manager

class Config:
    # Database Configuration
    DB_HOST = secrets.get("SQLHOST")
    DB_USER = secrets.get("SQLUSER")
    DB_PASSWORD = secrets.get("SQLPASSWORD")
    DB_NAME = secrets.get("SQLDATABASE")
    DB_PORT = int(secrets.get("SQLPORT", 5432))  # Default to 5432 for PostgreSQL

    # Gmail API Credentials
    CREDS_INFO = json.loads(
        base64.b64decode(secrets.get("GMAIL_CREDENTIALS")).decode("utf-8")
    )

    TOKEN_INFO = json.loads(base64.b64decode(secrets.get("GMAIL_TOKEN")).decode("utf-8"))

    # JWT Settings
    JWT_SECRET_KEY = secrets.get("JWT_SECRET_KEY")

    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME = secrets.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = secrets.get("CLOUDINARY_API_KEY")
    CLOUDINARY_SECRET_KEY = secrets.get("CLOUDINARY_SECRET_KEY")
