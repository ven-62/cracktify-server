import tempfile
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import engine, Base
from app.routes import otp_routes, auth_routes, profile_routes, activity_routes, crack_routes, upload_routes

import app.models 

app = FastAPI(title="Cracktify API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(otp_routes.router, prefix="/otp", tags=["OTP"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(profile_routes.router, prefix="/profile", tags=["Profile"])
app.include_router(crack_routes.router, prefix="/cracks", tags=["Cracks"])
app.include_router(upload_routes.router, prefix="/upload", tags=["Uploads"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Cracktify API!"}
