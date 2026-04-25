from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.auth_service import (
    register_user_service,
    login_user_service,
    check_email_unique_service,
    forgot_password_service,
    check_username_unique_service,
)

router = APIRouter()


@router.post("/check-uniqueness")
def api_check_email_unique(data: dict = Body(...), db: Session = Depends(get_db)):
    field = data.get("field")
    check_type = data.get("check_type")

    if check_type == "email":
        return check_email_unique_service(field, db)
    elif check_type == "username":
        return check_username_unique_service(field, db)
    else:
        return {"success": False, "message": "Invalid check type"}

@router.post("/register")
def api_register_user(data: dict = Body(...), db: Session = Depends(get_db)):
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    username = data.get("username")
    email_address = data.get("email_address")
    password = data.get("password")

    return register_user_service(first_name, last_name, username, email_address, password, db)


@router.post("/login")
def api_login_user(data: dict = Body(...), db: Session = Depends(get_db)):
    user = data.get("user")
    password = data.get("password")

    return login_user_service(user, password, db)


@router.post("/forgot-password")
def api_forgot_password(data: dict = Body(...), db: Session = Depends(get_db)):
    email_address = data.get("email_address")
    new_password = data.get("new_password")

    return forgot_password_service(email_address, new_password, db)
