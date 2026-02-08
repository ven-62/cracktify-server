from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.crack_service import fetch_cracks_service, add_crack_service

router = APIRouter()

@router.post("/fetch")
def api_fetch_cracks(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to fetch cracks for a specific user."""
    user_id = data.get("user_id")
    
    return fetch_cracks_service(user_id, db)

@router.post("/add")
def api_add_crack(data: dict = Body(...), db: Session = Depends(get_db)):
    """Endpoint to add a new crack."""
    user_id = data.get("user_id")
    file_url = data.get("file_url")
    probability = data.get("probability")
    severity = data.get("severity")
    
    return add_crack_service(user_id, file_url, probability, severity, db)

