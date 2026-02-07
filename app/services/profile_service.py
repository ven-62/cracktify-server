from datetime import datetime, timezone
from app.models.user import User
from app.utils.password import hash_password, verify_password


def update_profile(profile_data: dict, db):
    """Update user profile with provided data"""
    user_id = profile_data.get("id")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}

    for key, value in profile_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    user.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    return {"success": True, "user": user}


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
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}
    
    hashed_password = hash_password(new_password)

    user.password_hash = hashed_password

    db.commit()
    db.refresh(user)

    return {
        "success": False, "message": "Password updated"
    }


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