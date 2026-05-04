# app/services/notification_service.py
from app.models.notification import Notification

def get_user_notifications(user_id: int, db):
    notifs = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).all()
    return {"notifications": [n.to_dict() for n in notifs]}

def mark_notification_read(notification_id: int, is_read: bool, db):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        return {"success": False, "error": "Not found"}
    notif.is_read = is_read  # ← toggle instead of always True
    db.commit()
    return {"success": True}

def delete_notification(notification_id: int, db):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        return {"success": False, "error": "Not found"}
    db.delete(notif)
    db.commit()
    return {"success": True}

def create_notification(user_id: int, message: str, crack_id: int = None, db=None):
    notif = Notification(user_id=user_id, message=message, crack_id=crack_id)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif