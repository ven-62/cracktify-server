# app/routes/notification_route.py
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.notification_service import (
    get_user_notifications,
    mark_notification_read,
    delete_notification,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/{user_id}")
def fetch_notifications(user_id: int, db=Depends(get_db)):
    return get_user_notifications(user_id, db)

@router.post("/mark-read")
def mark_read(data: dict = Body(...), db: Session = Depends(get_db)):
    notification_id = data.get("notification_id")
    is_read = data.get("is_read", True)  # Default to marking as read
    return mark_notification_read(notification_id, is_read, db)

@router.post("/delete")
def remove_notification(data: dict = Body(...), db: Session = Depends(get_db)):
    notification_id = data.get("notification_id")
    return delete_notification(notification_id, db)