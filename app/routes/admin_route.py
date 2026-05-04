from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.admin_service import (
    approve_engineer_verification,
    get_pending_verifications,
)

router = APIRouter()

# GET /admin/pending-verifications
@router.get("/pending-verifications")
def api_get_pending_verifications(db: Session = Depends(get_db)):
    # Search Cloudinary for all docs tagged as pending verification
    return get_pending_verifications(db)


# POST /admin/approve-verification
@router.post("/approve-verification")
def approve_verification(data: dict, db: Session = Depends(get_db)):
    public_id = data.get("public_id")
    engineer_id = data.get("engineer_id")

    return approve_engineer_verification(public_id, engineer_id, db)