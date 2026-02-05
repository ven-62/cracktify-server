import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    # Database
    DB_HOST = os.getenv("MYSQLHOST")
    DB_USER = os.getenv("MYSQLUSER")
    DB_PASSWORD = os.getenv("MYSQLPASSWORD")
    DB_NAME = os.getenv("MYSQLDATABASE")
    DB_PORT = int(os.getenv("MYSQLPORT", 3306))

    # Email settings
    EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

    # JWT Settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # Cloudinary Settings
    CLOUDINARY_SECRET_KEY = os.getenv("CLOUDINARY_SECRET_KEY")

    DEFAULT_BASE64_AVATAR = os.getenv("DEFAULT_BASE64_AVATAR", "")