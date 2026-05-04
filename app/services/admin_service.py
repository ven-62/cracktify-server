from app.database import db
from app.models.user import User

import cloudinary
import cloudinary.uploader
import cloudinary.search

def get_pending_verifications(db):
    """Search Cloudinary for all pending engineer verification documents and return their details"""

    result = cloudinary.search.Search()\
        .expression("tags:verification:pending")\
        .with_field("tags")\
        .with_field("context")\
        .execute()

    verifications = []
    for resource in result.get("resources", []):
        context = resource.get("context", {}).get("custom", {})
        verifications.append({
            "public_id": resource["public_id"],
            "document_url": resource["secure_url"],
            "user_id": context.get("user_id"),
            "engineer_id": context.get("engineer_id"),
            "uploaded_at": resource["created_at"],
        })

    return {"success": True, "verifications": verifications}

def approve_engineer_verification(public_id: str, engineer_id: int, db):
    """Approve an engineer's verification by updating their status in the DB and retagging the Cloudinary asset"""
    engineer = db.query(User).filter(User.id == engineer_id).first()
    if not engineer:
        return {"success": False, "error": "Engineer not found"}

    # Mark engineer as verified in DB
    engineer.verified = True
    db.commit()

    # Remove the pending tag from Cloudinary so it doesn't show up again
    cloudinary.uploader.remove_tag("verification:pending", [public_id])
    cloudinary.uploader.add_tag("verification:approved", [public_id])

    return {"success": True, "message": f"Engineer {engineer_id} verified"}