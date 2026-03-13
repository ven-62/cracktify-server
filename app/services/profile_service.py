from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.utils.password import hash_password, verify_password

def validate_email_uniqueness(email_address: str, db):
    """Check if the email address is already in use by another user."""
    existing_user = db.query(User).filter(User.email_address == email_address).first()
    return existing_user is None

def update_profile(profile_data: dict, db):
    """Update user profile with provided data"""
    user_id = profile_data.get("id")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}
    
    if "email_address" in profile_data:
        existing_user = db.query(User).filter(User.email_address == profile_data["email_address"], User.id != user_id).first()
        if existing_user:
            return {"success": False, "error": "Email address already in use"}

    for key, value in profile_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    user.updated_at = datetime.now(timezone.utc)  # Assuming UTC timezone

    db.commit()
    db.refresh(user)

    user_data  = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email_address": user.email_address,
        "avatar_url": user.avatar_url
    }

    return {"success": True, "user": user_data}

def get_user(user_id: int, db):
    """Retrieve user profile by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}

    user_data  = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email_address": user.email_address,
        "avatar_url": user.avatar_url
    }
    return {"success": True, "user": user_data}

def verify_user_password(user_id: int, old_password: str, db):
    """Verify if the provided password matches the user's password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}

    if verify_password(old_password, user.password_hash):
        return {"success": True, "message": "Password verified"}
    else:
        return {"success": False, "error": "Incorrect password"}

def update_password(user_id: int, new_password: str, db):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "error": "User not found"}
        
        hashed_password = hash_password(new_password)

        user.password_hash = hashed_password
        user.updated_at = datetime.now(timezone.utc)  # Assuming UTC timezone

        db.commit()
        db.refresh(user)

        return {
            "success": True, "message": "Password updated"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_account(user_id: int, password: str, db):
    """Delete user account after verifying the password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}

    if not verify_password(password, user.password_hash):
        return {"success": False, "error": "Incorrect password"}

    # Delete the user account directly (no group logic)
    db.delete(user)
    db.commit()

    return {"success": True, "message": "Account deleted successfully"}