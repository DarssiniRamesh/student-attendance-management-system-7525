"""
REST API for managing students. Supports CRUD operations.
Secured with JWT and OpenAPI docs.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.api.auth import get_db, get_current_user
from src.models import Student, User
from src.repositories import StudentRepository

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

class StudentCreate(BaseModel):
    name: str = Field(..., description="Full name of student")
    roll_number: str = Field(..., description="Unique roll number assigned to student")
    class_id: Optional[int] = Field(None, description="Class ID the student belongs to")

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Full name of student")
    roll_number: Optional[str] = Field(None, description="Unique roll number")
    class_id: Optional[int] = Field(None, description="Class ID")

class StudentOut(BaseModel):
    id: int
    name: str
    roll_number: str
    class_id: Optional[int]

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
@router.post("/", response_model=StudentOut, summary="Create a student", description="Add a new student to the system.", status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = StudentRepository()
    if db.query(Student).filter(Student.roll_number == student.roll_number).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student with this roll number already exists")
    db_student = repo.create(db, student.dict())
    return db_student

# PUBLIC_INTERFACE
@router.get("/", response_model=List[StudentOut], summary="List all students", description="Retrieve all students in the system.")
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = StudentRepository()
    return repo.get_all(db, skip=skip, limit=limit)

# PUBLIC_INTERFACE
@router.get("/{student_id}", response_model=StudentOut, summary="Get student by ID", description="Get details of a specific student.")
def get_student(student_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = StudentRepository()
    student = repo.get(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student

# PUBLIC_INTERFACE
@router.put("/{student_id}", response_model=StudentOut, summary="Update a student", description="Update student details.")
def update_student(student_id: int, student: StudentUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = StudentRepository()
    db_student = repo.get(db, student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    old_roll = db_student.roll_number
    if student.roll_number and student.roll_number != old_roll:
        # Check for unique roll number
        if db.query(Student).filter(Student.roll_number == student.roll_number).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Roll number already exists")

    update_data = student.dict(exclude_unset=True)
    return repo.update(db, db_student, update_data)

# PUBLIC_INTERFACE
@router.delete("/{student_id}", response_model=StudentOut, summary="Delete a student", description="Delete a student from the system.")
def delete_student(student_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = StudentRepository()
    db_student = repo.get(db, student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return repo.delete(db, db_student)
