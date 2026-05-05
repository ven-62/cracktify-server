from ast import Dict
import io
import re
from typing import Any
from fastapi import APIRouter, Depends, Body
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.profile_service import (
    assign_engineer_to_user,
    update_profile,
    verify_engineer_assignment,
    verify_user_password,
    get_user,
    update_password,
    delete_account,
    get_all_engineers_username,
)

router = APIRouter()


@router.post("/update")
def api_update_profile(data: dict = Body(...), db: Session = Depends(get_db)):
    profile_data = data.get("profile_data", {})

    return update_profile(profile_data, db)


@router.get("/avatar")
def api_get_profile(data: dict = Body(...), db: Session = Depends(get_db)):
    user_id = data.get("user_id")

    return get_user(user_id, db)


@router.post("/verify_password")
def api_verify_user_password(data: dict = Body(...), db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    old_password = data.get("old_password")

    return verify_user_password(user_id, old_password, db)


@router.post("/update_password")
def api_update_password(data: dict = Body(...), db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    new_password = data.get("new_password")

    return update_password(user_id, new_password, db)


@router.post("/delete_account")
def api_delete_account(data: dict = Body(...), db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    password = data.get("password")

    return delete_account(user_id, password, db)

@router.get("/engineers")
def api_get_all_engineers_username(db: Session = Depends(get_db)):
    return get_all_engineers_username(db)

@router.post("/assign_engineer")
def api_assign_engineer(data: dict = Body(...), db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    engineer_id = data.get("engineer_id")

    return assign_engineer_to_user(user_id, engineer_id, db)

@router.post("/verify_engineer")
def api_verify_engineer_assignment(data: dict = Body(...), db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    license_number = data.get("license_number")
    document_url = data.get("document_url")

    return verify_engineer_assignment(user_id, license_number, document_url, db)
    