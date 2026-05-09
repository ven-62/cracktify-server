from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.profile_service import (
    update_profile,
    verify_user_password,
    get_user,
    update_password,
    delete_account,
)

router = APIRouter()


@router.get("/")
def api_get_profile(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to fetch the profile information of a user."""
    user_id = data.get("user_id")

    return get_user(user_id, db)


@router.post("/update")
def api_update_profile(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to update the profile information of a user."""
    profile_data = data.get("profile_data", {})

    return update_profile(profile_data, db)


@router.post("/verify_password")
def api_verify_user_password(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to verify the user's current password before allowing sensitive operations."""
    user_id = data.get("user_id")
    old_password = data.get("old_password")

    return verify_user_password(user_id, old_password, db)


@router.post("/update_password")
def api_update_password(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to update the user's password after verifying the current password."""
    user_id = data.get("user_id")
    new_password = data.get("new_password")

    return update_password(user_id, new_password, db)


@router.post("/delete_account")
def api_delete_account(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to delete the user's account after verifying the password."""
    user_id = data.get("user_id")
    password = data.get("password")

    return delete_account(user_id, password, db)
