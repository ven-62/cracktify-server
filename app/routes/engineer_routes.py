from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.engineer_service import (
    get_all_engineers_username,
    invite_engineer_to_user,
    accept_engineer_assignment,
    verify_engineer_assignment,
    get_associated_users,
)

router = APIRouter()


@router.get("/usernames")
def api_get_all_engineers_username(db: Session = Depends(get_db)):
    """Endpoint to retrieve all verified engineers' usernames."""
    return get_all_engineers_username(db)


@router.post("/invite")
async def api_invite_engineer(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to invite an engineer to be assigned to a user."""
    user_id = data.get("user_id")
    engineer_username = data.get("engineer_username")

    return await invite_engineer_to_user(user_id, engineer_username, db)


@router.post("/accept")
async def api_accept_engineer_assignment(
    data: dict = Body(...), db: Session = Depends(get_db)
):
    """Endpoint for an engineer to accept an assignment invitation from a user."""
    inviter_id = data.get("inviter_id")
    engineer_id = data.get("engineer_id")

    return await accept_engineer_assignment(inviter_id, engineer_id, db)


@router.post("/verify")
async def api_verify_engineer_assignment(
    data: dict = Body(...), db: Session = Depends(get_db)
):
    """Endpoint for an engineer to verify their credentials when accepting an assignment."""
    user_id = data.get("user_id")
    license_number = data.get("license_number")
    document_url = data.get("document_url")

    return await verify_engineer_assignment(user_id, license_number, document_url, db)


@router.get("/get_associated_users/{user_id}")
def api_get_associated_users(user_id: str, db: Session = Depends(get_db)):
    """Endpoint to retrieve all users associated with a specific engineer."""
    return get_associated_users(int(user_id), db)
