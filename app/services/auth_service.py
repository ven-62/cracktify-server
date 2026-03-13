from datetime import datetime, timezone, timedelta
from app.models.user import User
from app.utils.password import hash_password, verify_password
from app.utils.token_generator import generate_jwt
from config import Config

DEFAULT_AVATAR = "https://www.gravatar.com/avatar/?d=mp&s=200"


def check_email_unique_service(email_address: str, db):
    """Check if the email is already registered."""
    # Query the database to find a user with the given email
    user = db.query(User).filter(User.email_address == email_address).first()

    if user:
        return {
            "success": False,
            "message": "Email is already registered",
        }  # If email found, return not unique

    return {"success": True, "message": "Email is unique"}


def register_user_service(
    first_name: str, last_name: str, email_address: str, password: str, db
):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email_address == email_address).first()
    if existing_user:
        return {"success": False, "message": "User already exists"}

    # Hash the password
    hashed_password = hash_password(password)

    # Create new user
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email_address=email_address,
        password_hash=hashed_password,
        avatar_url=DEFAULT_AVATAR,
        created_at=datetime.now(timezone.utc),  # Assuming UTC timezone
        updated_at=datetime.now(timezone.utc),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ERROR PROBABLY HAPPEN HERE,
    token = generate_jwt(new_user.id, new_user.email_address)

    return {
        "success": True,
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": new_user.id,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email_address": new_user.email_address,
            "avatar_url": new_user.avatar_url,
        },
    }


def login_user_service(email_address: str, password: str, db):
    """Authenticate a user by email and password."""
    # Find user by email
    user = db.query(User).filter(User.email_address == email_address).first()
    if not user:
        return {"success": False, "message": "Invalid email or password"}

    # Verify password
    if not verify_password(password, user.password_hash):
        return {"success": False, "message": "Invalid email or password"}

    token = generate_jwt(user.id, user.email_address)

    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email_address": user.email_address,
            "avatar_url": user.avatar_url,
        },
    }


def forgot_password_service(email_address: str, new_password: str, db):
    """Reset user's password."""
    # Find user by email
    user = db.query(User).filter(User.email_address == email_address).first()
    if not user:
        return {"success": False, "message": "Email not found"}

    # Hash the new password
    hashed_password = hash_password(new_password)

    # Update user's password
    user.password_hash = hashed_password
    user.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {"success": True, "message": "Password reset successfully"}
