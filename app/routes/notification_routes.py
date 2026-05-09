from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.notification_service import (
    get_notification,
    get_user_notifications,
    mark_notification_read,
    delete_notification,
)

router = APIRouter()


@router.get("/user/{user_id}")
def fetch_notifications(user_id: str, db=Depends(get_db)):
    """Endpoint to fetch all notifications for a specific user."""
    return get_user_notifications(int(user_id), db)


@router.get("/{notification_id}")
def fetch_notification(notification_id: str, db=Depends(get_db)):
    """Endpoint to fetch a specific notification by ID."""
    return get_notification(int(notification_id), db)


@router.post("/mark-read")
def mark_read(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to mark a notification as read or unread."""
    notification_id = data.get("notification_id")
    is_read = data.get("is_read", True)  # Default to marking as read
    return mark_notification_read(int(notification_id), is_read, db)


@router.post("/delete")
def remove_notification(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to delete a notification."""
    notification_id = data.get("notification_id")
    return delete_notification(int(notification_id), db)
