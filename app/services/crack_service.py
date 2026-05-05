from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.crack import Crack


def fetch_cracks_service(user_id: int, db, limit):
    """Fetch cracks for a specific user."""
    try:
        if user_id == -1:  # If user_id is -1, fetch all cracks without filtering by user
            query = db.query(Crack)
        else:
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

def get_one_crack_service(crack_id: int, db):
    """Fetch a single crack by its ID."""
    try:
        crack = db.query(Crack).filter(Crack.id == crack_id).first()
        if not crack:
            return {"success": False, "message": "Crack not found"}

        return {
            "success": True,
            "message": "Crack fetched successfully",
            "crack": crack.to_dict(),
        }
    except Exception as e:
        return {"success": False, "message": f"Error fetching crack: {str(e)}"}
    
def detect_crack_service(file_info: dict, confidence_threshold: float):
    """Detect cracks in an image or video based on the provided file information."""
    from app.services.crack_classifier import CrackClassifier
    from app.services.crack_vid_detector import analyze_crack_video
    from pathlib import Path

    file_url = file_info.get("url")
    file_type = file_info.get("type")
    try:

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
        
    except Exception as e:
        return {"success": False, "message": f"Error during crack detection: {str(e)}"}
    
    finally:        # Cleanup the file from cloud storage after processing
        from app.utils.uploads import delete_file
        delete_file(file_url)


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
    
def has_edit_access(user_id: int, crack_id: int, db):
    """Check if a user is the engineer assigned to the crack"""
    try:
        crack = db.query(Crack).filter(Crack.id == crack_id).first()
        crack_owner = db.query(User).filter(User.id == crack.user_id).first()

        if crack_owner.assigned_engineer == user_id: # If the user is the assigned engineer for the crack, they have edit access
            return {"success": True, "can_edit": True}
        else:
            return {"success": True, "can_edit": False}
         
    except Exception as e:
        return {"success": False, "message": f"Error checking edit access: {str(e)}"}
    

def delete_crack_service(crack_id: int, db):
    """Delete a crack by its ID."""
    from app.utils.uploads import delete_file

    try:
        crack = db.query(Crack).filter(Crack.id == crack_id).first()
        if not crack:
            return {"success": False, "message": "Crack not found"}

        db.delete(crack)
        db.commit()

        delete_file(crack.file_url)

        return {"success": True, "message": "Crack deleted successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error deleting crack: {str(e)}"}
