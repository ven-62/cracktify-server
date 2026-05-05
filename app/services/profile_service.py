from datetime import datetime, timedelta, timezone
from app.database import db
from app.models.user import User
from app.utils.password import hash_password, verify_password

from app.websocket_manager import manager
from app.services.notification_service import create_notification

import cloudinary
import cloudinary.uploader
import cloudinary.search

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
        existing_user = (
            db.query(User)
            .filter(
                User.email_address == profile_data["email_address"], User.id != user_id
            )
            .first()
        )
        if existing_user:
            return {"success": False, "error": "Email address already in use"}

    for key, value in profile_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    user.updated_at = datetime.now(timezone.utc)  # Assuming UTC timezone

    db.commit()
    db.refresh(user)

    user_data = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email_address": user.email_address,
        "avatar_url": user.avatar_url,
    }

    return {"success": True, "user": user_data}


def get_user(user_id: int, db):
    """Retrieve user profile by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}

    user_data = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email_address": user.email_address,
        "avatar_url": user.avatar_url,
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

        return {"success": True, "message": "Password updated"}
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

def get_all_engineers_username(db):
    """Retrieve all verified engineers' usernames"""
    engineers = (
        db.query(User)
        .filter(User.is_engineer == True, User.verified == True)
        .all()
    )
    engineer_usernames = [engineer.username for engineer in engineers]
    return {"success": True, "engineers": engineer_usernames}

async def invite_engineer_to_user(user_id: int, engineer_id: int, db):
    """Assign an engineer to a user"""
    user = db.query(User).filter(User.id == user_id).first()
    engineer = db.query(User).filter(User.id == engineer_id, User.is_engineer == True).first()

    if not user:
        return {"success": False, "error": "User not found"}
    if not engineer:
        return {"success": False, "error": "Engineer not found"}

    # Send a notification to the assigned engineer
    notif = create_notification(
        user_id=engineer_id,
        message=f"You are invited by {user.first_name} {user.last_name} ({user.username}) to be their structural engineer. You can accept or ignore the invitation below.",
        db=db,
    )

    await manager.notify_user(str(engineer_id), {
        "event": "new_assignment",
        "notification_id": notif.id,
        "inviter_id": user.id,
    })

async def accept_engineer_assignment(inviter_id: str, engineer_id: int, db):
    user = db.query(User).filter(User.id == inviter_id).first()
    engineer = db.query(User).filter(User.id == engineer_id, User.is_engineer == True).first()

    if not user:
        return {"success": False, "error": "User not found"}
    if not engineer:
        return {"success": False, "error": "Engineer not found"}

    user.assigned_engineer = engineer_id
    user.updated_at = datetime.now(timezone.utc)  # Assuming UTC timezone

    db.commit()
    db.refresh(user)

    # Send a notification to the assigned engineer
    eng_notif = create_notification(
        user_id=engineer_id,
        message=f"You have accepted the assignment to be {user.first_name} {user.last_name}'s structural engineer.",
        db=db,
    )
    inv_notif = create_notification(
        user_id=inviter_id,
        message=f"{engineer.first_name} {engineer.last_name} ({engineer.username}) has accepted your invitation to be their structural engineer.",
        db=db,
    )

    await manager.notify_user(str(engineer_id), {
        "event": "accepted_assignment",
        "notification_id": eng_notif.id,
    })

    await manager.notify_user(str(inviter_id), {
        "event": "accepted_assignment",
        "notification_id": inv_notif.id,
    })

    return {"success": True, "message": f"Engineer {engineer.username} assigned to user {user.username}"}


async def verify_engineer_assignment(user_id: int, license_number: str, document_url: str, db):
    """Verify that the engineer is assigned to the user and submit the verification document to Cloudinary"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"success": False, "error": "User not found"}

    public_id = document_url.split("/")[-1].split(".")[0]

    # Tag as pending + attach user/engineer IDs as context
    cloudinary.uploader.add_tag("verification:pending", [public_id])
    cloudinary.uploader.add_context(
        f"user_id={user_id}|license_number={license_number}",
        [public_id]
    )

    return {"success": True, "message": "Document submitted for verification"}


def get_verification_doc(user_id: int):
    """Search Cloudinary for the user's verification document"""

    result = cloudinary.search.Search()\
        .expression(f"tags:verification:user_{user_id}")\
        .execute()
    return result["resources"]  # returns the document with its URL

