from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.crack import Crack


def fetch_cracks_service(user_id: int, db, limit):
    """Fetch cracks for a specific user."""
    try:
        query = db.query(Crack).filter(Crack.user_id == user_id)

        if (
            limit and limit > 0
        ):  # If limit is provided and greater than 0, apply the limit to the query
            query = query.order_by(Crack.detected_at.desc()).limit(limit)

        cracks = query.order_by(Crack.detected_at.desc()).all()

        total_cracks = len(cracks)
        # TODO: Add more crack types in the future and update this logic accordingly
        total_high_cracks = sum(1 for crack in cracks if crack.severity == "High")
        total_mild_cracks = sum(1 for crack in cracks if crack.severity == "Mild")
        total_low_cracks = sum(1 for crack in cracks if crack.severity == "Low")

        return {
            "success": True,
            "message": "Cracks fetched successfully",
            "cracks": [crack.to_dict() for crack in cracks],
            "stats": {
                "total_cracks": total_cracks,
                "total_high_cracks": total_high_cracks,
                "total_mild_cracks": total_mild_cracks,
                "total_low_cracks": total_low_cracks,
            },
        }
    except Exception as e:
        return {"success": False, "message": f"Error fetching cracks: {str(e)}"}


def detect_crack_service(file_info: dict, confidence_threshold: float):
    """Detect cracks in an image or video based on the provided file information."""
    from app.services.crack_classifier import CrackClassifier
    from app.services.crack_vid_detector import analyze_crack_video
    from pathlib import Path

    file_url = file_info.get("url")
    file_type = file_info.get("type")

    if file_type == "image":
        # If the file is an image, perform image classifier
        classifier_path = (
            Path(__file__).parent.parent / "assets" / "model" / "crackAI.tflite"
        )

        classifier = CrackClassifier(classifier_path)
        result = classifier.analyze_and_save(file_url, confidence_threshold)

        return result

    elif file_type == "video":
        # Else, if file is a video, perform video classifier
        result = analyze_crack_video(file_url)
        return result

    else:
        raise ValueError(f"Unsupported file type for crack detection: {file_type}")


def add_crack_service(user_id: int, crack_data: dict, db):
    """Add a crack for a specific user."""

    # Validate user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found"}

    file_url = crack_data.get("file_url")
    probability = crack_data.get("probability")
    severity = crack_data.get("severity")
    filename = crack_data.get("filename")

    # Create crack record
    new_crack = Crack(
        user_id=user_id,
        file_url=file_url,
        probability=probability,
        severity=severity,
        detected_at=datetime.now(timezone.utc),  # Assuming UTC timezone
        filename=filename,
    )
    db.add(new_crack)
    db.commit()
    db.refresh(new_crack)

    return {
        "success": True,
        "message": "Crack added successfully",
        "crack_id": new_crack.id,
    }


def update_crack_service(crack_id: int, updated_data: dict, db):
    """Update an existing crack by its ID."""
    try:
        crack = db.query(Crack).filter(Crack.id == crack_id).first()
        if not crack:
            return {"success": False, "message": "Crack not found"}

        # Update fields based on provided data
        for key, value in updated_data.items():
            if hasattr(crack, key):
                setattr(crack, key, value)

        db.commit()
        db.refresh(crack)

        return {
            "success": True,
            "message": "Crack updated successfully",
            "crack": crack.to_dict(),
        }
    
    except Exception as e:
        return {"success": False, "message": f"Error updating crack: {str(e)}"}


def delete_crack_service(crack_id: int, db):
    """Delete a crack by its ID."""
    try:
        crack = db.query(Crack).filter(Crack.id == crack_id).first()
        if not crack:
            return {"success": False, "message": "Crack not found"}

        db.delete(crack)
        db.commit()

        return {"success": True, "message": "Crack deleted successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error deleting crack: {str(e)}"}
