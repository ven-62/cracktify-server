from datetime import datetime, timedelta, timezone

from app.models.user import User
from app.websocket_manager import manager
from app.services.notification_service import create_notification

import cloudinary
import cloudinary.uploader


def get_all_engineers_username(db):
    """Retrieve all verified engineers' usernames"""
    engineers = (
        db.query(User).filter(User.is_engineer == True, User.verified == True).all()
    )
    engineer_usernames = [engineer.username for engineer in engineers]
    return {"success": True, "engineers": engineer_usernames}


async def invite_engineer_to_user(user_id: int, engineer_username: str, db):
    """Assign an engineer to a user"""
    user = db.query(User).filter(User.id == user_id).first()
    engineer = (
        db.query(User)
        .filter(User.username == engineer_username, User.is_engineer == True)
        .first()
    )

    if not user:
        return {"success": False, "error": "User not found"}
    if not engineer:
        return {"success": False, "error": "Engineer not found"}

    # Send a notification to the assigned engineer
    notif = create_notification(
        user_id=engineer.id,
        message=f"You are invited by {user.first_name} {user.last_name} ({user.username}) to be their structural engineer. You can accept or ignore the invitation below.",
        inviter_id=user.id,
        db=db,
    )

    await manager.notify_user(
        str(engineer.id),
        {
            "event": "new_assignment",
            "notification_id": notif.id,
            "inviter_id": user.id,
        },
    )


async def accept_engineer_assignment(inviter_id: str, engineer_id: int, db):
    user = db.query(User).filter(User.id == inviter_id).first()
    engineer = (
        db.query(User).filter(User.id == engineer_id, User.is_engineer == True).first()
    )

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

    await manager.notify_user(
        str(engineer_id),
        {
            "event": "accepted_assignment",
            "notification_id": eng_notif.id,
        },
    )

    await manager.notify_user(
        str(inviter_id),
        {
            "event": "accepted_assignment",
            "notification_id": inv_notif.id,
        },
    )

    return {
        "success": True,
        "message": f"Engineer {engineer.username} assigned to user {user.username}",
    }


async def verify_engineer_assignment(
    user_id: int, license_number: str, document_url: str, db
):
    """Verify that the engineer is assigned to the user and submit the verification document to Cloudinary"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"success": False, "error": "User not found"}

    public_id = document_url.split("/")[-1].split(".")[0]

    # Tag as pending + attach user/engineer IDs as context
    cloudinary.uploader.add_tag("verification-pending", [public_id])
    cloudinary.uploader.add_context(
        f"user_id={user_id}|license_number={license_number}", [public_id]
    )

    return {"success": True, "message": "Document submitted for verification"}


def get_associated_users(eng_id: int, db):
    """Get all users associated with a given engineer"""
    users = db.query(User).filter(User.assigned_engineer == eng_id).all()
    user_data = []
    for user in users:
        user_data.append(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email_address": user.email_address,
                "username": user.username,
                "avatar_url": user.avatar_url,
            }
        )
    return {"success": True, "associated_users": user_data}
