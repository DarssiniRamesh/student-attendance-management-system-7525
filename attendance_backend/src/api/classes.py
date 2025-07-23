"""
REST API for managing classes. Supports CRUD operations.
Secured with JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.api.auth import get_db, get_current_user
from src.models import User
from src.repositories import ClassRepository

router = APIRouter(
    prefix="/classes",
    tags=["Classes"]
)

class ClassCreate(BaseModel):
    name: str = Field(..., description="Class name")
    section: Optional[str] = Field(None, description="Section name")
    teacher_id: Optional[int] = Field(None, description="Teacher user ID")

class ClassUpdate(BaseModel):
    name: Optional[str]
    section: Optional[str]
    teacher_id: Optional[int]

class ClassOut(BaseModel):
    id: int
    name: str
    section: Optional[str]
    teacher_id: Optional[int]

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
@router.post("/", response_model=ClassOut, summary="Create a class", status_code=status.HTTP_201_CREATED)
def create_class(class_in: ClassCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = ClassRepository()
    db_class = repo.create(db, class_in.dict())
    return db_class

# PUBLIC_INTERFACE
@router.get("/", response_model=List[ClassOut], summary="List all classes")
def list_classes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = ClassRepository()
    return repo.get_all(db, skip=skip, limit=limit)

# PUBLIC_INTERFACE
@router.get("/{class_id}", response_model=ClassOut, summary="Get class by ID")
def get_class(class_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = ClassRepository()
    db_class = repo.get(db, class_id)
    if not db_class:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
    return db_class

# PUBLIC_INTERFACE
@router.put("/{class_id}", response_model=ClassOut, summary="Update a class")
def update_class(class_id: int, class_in: ClassUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = ClassRepository()
    db_class = repo.get(db, class_id)
    if not db_class:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
    update_data = class_in.dict(exclude_unset=True)
    return repo.update(db, db_class, update_data)

# PUBLIC_INTERFACE
@router.delete("/{class_id}", response_model=ClassOut, summary="Delete a class")
def delete_class(class_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = ClassRepository()
    db_class = repo.get(db, class_id)
    if not db_class:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")
    return repo.delete(db, db_class)
