"""
REST API for managing and marking student attendance.
Features: mark attendance, CRUD attendance, export attendance as CSV.
Secured with JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import date
import csv
import io

from src.api.auth import get_db, get_current_user
from src.models import Attendance, User
from src.repositories import AttendanceRepository

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

class AttendanceCreate(BaseModel):
    student_id: int = Field(..., description="ID of the student")
    class_id: int = Field(..., description="ID of the class")
    date: date = Field(..., description="Date for attendance")
    status: str = Field(..., description="Attendance status - Present/Absent/Late")

class AttendanceUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Attendance status")

class AttendanceOut(BaseModel):
    id: int
    student_id: int
    class_id: int
    date: date
    status: str

    class Config:
        from_attributes = True

class AttendanceMarkIn(BaseModel):
    attendances: List[AttendanceCreate] = Field(..., description="Bulk attendance marking list")

# PUBLIC_INTERFACE
@router.post("/", response_model=AttendanceOut, summary="Create attendance record")
def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = AttendanceRepository()
    # Prevent duplicate for same student/class/date
    exists = db.query(Attendance).filter_by(student_id=attendance.student_id, class_id=attendance.class_id, date=attendance.date).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attendance already marked for this student on this date")
    return repo.create(db, attendance.dict())

# PUBLIC_INTERFACE
@router.post("/mark", summary="Mark batch attendance", description="Mark attendance for multiple students at once")
def mark_attendance(attendance_in: AttendanceMarkIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = AttendanceRepository()
    created = []
    for att in attendance_in.attendances:
        exists = db.query(Attendance).filter_by(student_id=att.student_id, class_id=att.class_id, date=att.date).first()
        if not exists:
            record = repo.create(db, att.dict())
            created.append(record)
    return {"marked": len(created), "records": created}

# PUBLIC_INTERFACE
@router.get("/", response_model=List[AttendanceOut], summary="List all attendance records")
def list_attendance(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = AttendanceRepository()
    return repo.get_all(db, skip=skip, limit=limit)

# PUBLIC_INTERFACE
@router.get("/{attendance_id}", response_model=AttendanceOut, summary="Get attendance record by ID")
def get_attendance(attendance_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = AttendanceRepository()
    db_att = repo.get(db, attendance_id)
    if not db_att:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
    return db_att

# PUBLIC_INTERFACE
@router.put("/{attendance_id}", response_model=AttendanceOut, summary="Update attendance status")
def update_attendance(attendance_id: int, att_in: AttendanceUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = AttendanceRepository()
    db_att = repo.get(db, attendance_id)
    if not db_att:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
    update_data = att_in.dict(exclude_unset=True)
    return repo.update(db, db_att, update_data)

# PUBLIC_INTERFACE
@router.delete("/{attendance_id}", response_model=AttendanceOut, summary="Delete attendance")
def delete_attendance(attendance_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    repo = AttendanceRepository()
    db_att = repo.get(db, attendance_id)
    if not db_att:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
    return repo.delete(db, db_att)

# PUBLIC_INTERFACE
@router.get("/export/csv", summary="Export attendance as CSV", description="Export filtered attendance records as CSV file")
def export_attendance_csv(class_id: Optional[int] = None, student_id: Optional[int] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Attendance)
    if class_id:
        q = q.filter(Attendance.class_id == class_id)
    if student_id:
        q = q.filter(Attendance.student_id == student_id)
    if start_date:
        q = q.filter(Attendance.date >= start_date)
    if end_date:
        q = q.filter(Attendance.date <= end_date)
    records = q.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Class ID', 'Student ID', 'Date', 'Status'])
    for at in records:
        writer.writerow([at.id, at.class_id, at.student_id, at.date, at.status])
    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=attendance_export.csv"
    return response
