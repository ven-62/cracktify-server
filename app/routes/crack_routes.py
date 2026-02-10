from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.crack_service import detect_crack_service, fetch_cracks_service, add_crack_service

router = APIRouter()

@router.post("/fetch")
def api_fetch_cracks(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to fetch cracks for a specific user."""
    user_id = data.get("user_id")
    
    return fetch_cracks_service(user_id, db)

@router.post("/detect")
def api_detect_crack(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to detect cracks in an image."""
    image_path = data.get("image_path")
    confidence_threshold = data.get("confidence_threshold", 0.4)  # Default threshold if not provided
    
    return detect_crack_service(image_path, confidence_threshold, db)

@router.post("/add")
def api_add_crack(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to add a new crack."""
    user_id = data.get("user_id")
    crack_data = data.get("crack_data")
    
    file_url = crack_data.get("file_url")
    probability = crack_data.get("probability")
    severity = crack_data.get("severity")
    
    return add_crack_service(user_id, file_url, probability, severity, db)

