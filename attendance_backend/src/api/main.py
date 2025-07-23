from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import router as auth_router

openapi_tags = [
    {
        "name": "Authentication",
        "description": "User registration, login/logout, and current user info endpoints."
    }
]

app = FastAPI(
    title="Student Attendance Tracker API",
    description="API for managing students, attendance, and authentication.",
    version="0.1.0",
    openapi_tags=openapi_tags
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/", tags=["Misc"])
def health_check():
    """Health check endpoint for service monitoring."""
    return {"message": "Healthy"}
