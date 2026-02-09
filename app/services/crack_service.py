from datetime import datetime, timezone
from app.models.user import User
from app.models.crack import Crack

def fetch_cracks_service(user_id: int, db):
    """Fetch cracks for a specific user."""
    try:
        cracks = db.query(Crack).filter(Crack.user_id == user_id).all()

        return {
            "success": True,
            "message": "Cracks fetched successfully",
            "cracks": [crack.to_dict() for crack in cracks]
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error fetching cracks: {str(e)}"
        }

def add_crack_service(user_id: int, file_url: str, probability: float, severity: str, db):
    """Add a crack for a specific user."""

    # Validate user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found"}

    # Create crack record
    new_crack = Crack(
        user_id=user_id,
        file_url=file_url,
        probability=probability,
        severity=severity,
        detected_at=datetime.now(timezone.utc)
    )
    db.add(new_crack)
    db.commit()
    db.refresh(new_crack)

    return {
        "success": True,
        "message": "Crack added successfully",
        "crack_id": new_crack.id
    }