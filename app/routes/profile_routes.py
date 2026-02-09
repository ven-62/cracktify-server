from ast import Dict
import io
import re
from typing import Any
from fastapi import APIRouter, Depends, Body
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.profile_service import update_profile, verify_user_password, get_user, update_password, delete_account

router = APIRouter()

@router.post("/update/{user_id}")
def api_update_profile(data: dict = Body(...), db: Session = Depends(get_db)):
    profile_data = data.get("profile_data", {})

    return update_profile(profile_data, db)

@router.get("/{user_id}")
def api_get_profile(user_id: int, db: Session = Depends(get_db)):
    return get_user(user_id, db)

@router.post("/verify_password/{user_id}")
def api_verify_user_password(data: dict = Body(...), db: Session = Depends(get_db)):
    user_id = data.get("id")
    old_password = data.get("old_password")

    return verify_user_password(user_id, old_password, db)

@router.post("/update_password/{user_id}")
def api_update_password(data: dict = Body(...), db: Session = Depends(get_db)):
    user_id = data.get("id")
    new_password = data.get("new_password")

    return update_password(user_id, new_password, db)

@router.post("/delete_account/{user_id}")
def api_delete_account(data: dict = Body(...), db: Session = Depends(get_db)):
    user_id = data.get("id")
    password = data.get("password")

    return delete_account(user_id, password, db)