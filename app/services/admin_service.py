from app.models.user import User
from app.websocket_manager import manager

import cloudinary
import cloudinary.uploader
import cloudinary.search


def get_pending_verifications(db):
    """Search Cloudinary for all pending engineer verification documents and return their details."""
    result = (
        cloudinary.search.Search()
        .expression('tags:"verification:pending"')
        .with_field("tags")
        .with_field("context")
        .execute()
    )

    verifications = []
    for resource in result.get("resources", []):
        context = resource.get("context", {}).get("custom", {})

        user = db.query(User).filter(User.id == int(context.get("user_id"))).first()
        if not user:
            continue

        verifications.append({
            "user":           user.username,
            "first_name":     user.first_name,
            "last_name":      user.last_name,
            "email":          user.email_address,
            "image_url":      user.image_url,
            "public_id":      resource["public_id"],
            "document_url":   resource["secure_url"],
            "user_id":        context.get("user_id"),
            "license_number": context.get("license_number"),
            "uploaded_at":    resource["created_at"],
        })

    return {"success": True, "verifications": verifications}


async def approve_engineer_verification(public_id: str, engineer_id: int, db):
    """
    Approve an engineer:
      1. Set user.verified = True in the DB.
      2. Swap Cloudinary tags from 'pending' → 'approved'.
      3. Create a DB notification record.
      4. Push a real-time WebSocket event to the engineer.
    """
    engineer = db.query(User).filter(User.id == engineer_id).first()
    if not engineer:
        return {"success": False, "error": "Engineer not found"}

    engineer.verified = True
    db.commit()

    cloudinary.uploader.remove_tag("verification:pending", [public_id])
    cloudinary.uploader.add_tag("verification:approved", [public_id])

    from app.services.notification_service import create_notification

    notif = create_notification(
        user_id=engineer_id,
        message="Your engineer account has been verified. You can now accept jobs.",
        db=db,
    )

    await manager.notify_user(str(engineer_id), {
        "event": "approved_verification",
        "notification_id": notif.id,
    })

    return {"success": True}


async def decline_engineer_verification(
    public_id: str, engineer_id: int, reason: str, db
):
    """
    Decline an engineer's verification:
      1. Swap Cloudinary tags from 'pending' → 'declined'.
      2. Create a DB notification record with the admin's reason.
      3. Push a real-time WebSocket event to the engineer.

    Note: we intentionally do NOT set user.verified = False here because
    the user may already be unverified by default. The engineer can re-submit
    documents after addressing the admin's feedback.
    """
    engineer = db.query(User).filter(User.id == engineer_id).first()
    if not engineer:
        return {"success": False, "error": "Engineer not found"}

    cloudinary.uploader.remove_tag("verification:pending", [public_id])
    cloudinary.uploader.add_tag("verification:declined", [public_id])

    base_message = "Your engineer verification was declined."
    message = (
        f"{base_message} Reason: {reason}"
        if reason and reason.strip()
        else f"{base_message} Please review your documents and re-submit."
    )

    from app.services.notification_service import create_notification

    notif = create_notification(
        user_id=engineer_id,
        message=message,
        db=db,
    )

    await manager.notify_user(str(engineer_id), {
        "event": "declined_verification",
        "notification_id": notif.id,
    })

    return {"success": True}