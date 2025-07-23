from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import router as auth_router
from src.api.students import router as students_router
from src.api.classes import router as classes_router
from src.api.teachers import router as teachers_router
from src.api.attendance import router as attendance_router

openapi_tags = [
    {
        "name": "Authentication",
        "description": "User registration, login/logout, and current user info endpoints."
    },
    {
        "name": "Students",
        "description": "CRUD endpoints for students management."
    },
    {
        "name": "Classes",
        "description": "CRUD endpoints for classes management."
    },
    {
        "name": "Teachers",
        "description": "CRUD endpoints for teachers management."
    },
    {
        "name": "Attendance",
        "description": "Mark, update, view, and export attendance records."
    },
    {
        "name": "Misc",
        "description": "Miscellaneous endpoints (e.g., health check)."
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
app.include_router(students_router)
app.include_router(classes_router)
app.include_router(teachers_router)
app.include_router(attendance_router)

@app.get("/", tags=["Misc"])
def health_check():
    """Health check endpoint for service monitoring."""
    return {"message": "Healthy"}
