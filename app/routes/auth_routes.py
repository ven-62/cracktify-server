from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.auth_service import (
    register_user_service,
    login_user_service,
    check_email_unique_service,
    forgot_password_service,
)

router = APIRouter()


@router.post("/check-email")
def api_check_email_unique(data: dict = Body(...), db: Session = Depends(get_db)):
    email_address = data.get("email_address")

    return check_email_unique_service(email_address, db)


@router.post("/register")
def api_register_user(data: dict = Body(...), db: Session = Depends(get_db)):
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email_address = data.get("email_address")
    password = data.get("password")

    return register_user_service(first_name, last_name, email_address, password, db)


@router.post("/login")
def api_login_user(data: dict = Body(...), db: Session = Depends(get_db)):
    email_address = data.get("email_address")
    password = data.get("password")

    return login_user_service(email_address, password, db)


@router.post("/forgot-password")
def api_forgot_password(data: dict = Body(...), db: Session = Depends(get_db)):
    email_address = data.get("email_address")
    new_password = data.get("new_password")

    return forgot_password_service(email_address, new_password, db)
