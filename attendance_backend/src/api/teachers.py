"""
REST API for managing teachers (Users with role='teacher').
Secured with JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from src.api.auth import get_db, get_current_user, get_password_hash
from src.models import User, UserRole
from src.repositories import UserRepository

router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)

class TeacherCreate(BaseModel):
    username: str = Field(..., description="Username for teacher")
    full_name: str = Field(..., description="Teacher's full name")
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.teacher

class TeacherUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]

class TeacherOut(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
@router.post("/", response_model=TeacherOut, summary="Create a teacher account", status_code=status.HTTP_201_CREATED)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = UserRepository()
    if db.query(User).filter((User.username == teacher.username) | (User.email == teacher.email)).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
    teacher_dict = teacher.dict()
    teacher_dict['hashed_password'] = get_password_hash(teacher_dict.pop('password'))
    db_teacher = repo.create(db, teacher_dict)
    return db_teacher

# PUBLIC_INTERFACE
@router.get("/", response_model=List[TeacherOut], summary="List all teachers")
def list_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    teachers = db.query(User).filter(User.role == UserRole.teacher).offset(skip).limit(limit).all()
    return teachers

# PUBLIC_INTERFACE
@router.get("/{teacher_id}", response_model=TeacherOut, summary="Get teacher by ID")
def get_teacher(teacher_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_teacher = db.query(User).filter(User.id == teacher_id, User.role == UserRole.teacher).first()
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    return db_teacher

# PUBLIC_INTERFACE
@router.put("/{teacher_id}", response_model=TeacherOut, summary="Update teacher profile")
def update_teacher(teacher_id: int, update: TeacherUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = UserRepository()
    db_teacher = db.query(User).filter(User.id == teacher_id, User.role == UserRole.teacher).first()
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    update_data = update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
    return repo.update(db, db_teacher, update_data)

# PUBLIC_INTERFACE
@router.delete("/{teacher_id}", response_model=TeacherOut, summary="Delete teacher")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = UserRepository()
    db_teacher = db.query(User).filter(User.id == teacher_id, User.role == UserRole.teacher).first()
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    return repo.delete(db, db_teacher)
