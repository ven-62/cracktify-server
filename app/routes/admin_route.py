from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.admin_service import (
    approve_engineer_verification,
    decline_engineer_verification,
    get_pending_verifications,
)

router = APIRouter()


# GET /admin/pending-verifications
@router.get("/pending-verifications")
def api_get_pending_verifications(db: Session = Depends(get_db)):
    """Return all engineer verification documents currently tagged as pending."""
    return get_pending_verifications(db)


# POST /admin/approve-verification
@router.post("/approve-verification")
async def approve_verification(data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Approve an engineer's verification.
    Body: { public_id, engineer_id }
    Marks the engineer as verified, re-tags the Cloudinary doc, and
    pushes a real-time notification to the engineer via WebSocket.
    """
    public_id   = data.get("public_id")
    engineer_id = data.get("engineer_id")
    return await approve_engineer_verification(public_id, engineer_id, db)


# POST /admin/decline-verification
@router.post("/decline-verification")
async def decline_verification(data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Decline an engineer's verification.
    Body: { public_id, engineer_id, reason }
    Re-tags the Cloudinary doc as declined, and pushes a real-time
    notification to the engineer with the admin's optional reason.
    """
    public_id   = data.get("public_id")
    engineer_id = data.get("engineer_id")
    reason      = data.get("reason", "")
    return await decline_engineer_verification(public_id, engineer_id, reason, db)