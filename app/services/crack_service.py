from datetime import datetime, timezone
from app.models.user import User
from app.models.crack import Crack

def fetch_cracks_service(user_id: int, db):
    """Fetch cracks for a specific user."""
    try:
        cracks = db.query(Crack).filter(Crack.user_id == user_id).order_by(Crack.detected_at.desc()).all()

        total_cracks = len(cracks)
        # TODO: Add more crack types in the future and update this logic accordingly
        total_severe_cracks = sum(1 for crack in cracks if crack.severity == "Severe")
        total_mild_cracks = sum(1 for crack in cracks if crack.severity == "Mild")
        total_none_cracks = sum(1 for crack in cracks if crack.severity == "Low")

        return {
            "success": True,
            "message": "Cracks fetched successfully",
            "cracks": [crack.to_dict() for crack in cracks],
            "stats": {
                "total_cracks": total_cracks,
                "total_severe_cracks": total_severe_cracks,
                "total_mild_cracks": total_mild_cracks,
                "total_none_cracks": total_none_cracks,
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error fetching cracks: {str(e)}"
        }
def detect_crack_service(file_url: str, confidence_threshold: float, db):
    # This function is now handled by the CrackClassifier's analyze_and_save method, which returns the confidence and saves the image with the appropriate filename. The service layer can then call that method and extract the confidence from the filename if needed for further processing or database storage.
    from app.services.crack_classifier import CrackClassifier
    from pathlib import Path

    classifier_path = Path(__file__).parent.parent / "assets" / "model" / "crackAI.tflite"
    
    classifier = CrackClassifier(classifier_path)

    result = classifier.analyze_and_save(file_url, confidence_threshold)
    return result

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