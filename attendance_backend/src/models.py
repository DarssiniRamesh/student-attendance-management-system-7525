"""
SQLAlchemy models for User, Student, Class, and Attendance.

Defines the schema and relationships for core entities in the Student Attendance Tracker app.
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    teacher = 'teacher'
    admin = 'admin'

# PUBLIC_INTERFACE
class User(Base):
    """User model representing teachers and admins."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.teacher)

    # Relationship: a teacher can own multiple classes
    classes = relationship("Class", back_populates="teacher")

# PUBLIC_INTERFACE
class Student(Base):
    """Student model representing enrolled students."""
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    roll_number = Column(String(50), unique=True, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)

    # Relationship: reference to Class
    class_ = relationship("Class", back_populates="students")
    attendances = relationship("Attendance", back_populates="student")

# PUBLIC_INTERFACE
class Class(Base):
    """Class model representing a batch or classroom."""
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    section = Column(String(20), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationship: list of students and reference to teacher
    students = relationship("Student", back_populates="class_")
    teacher = relationship("User", back_populates="classes")
    attendances = relationship("Attendance", back_populates="class_")

# PUBLIC_INTERFACE
class Attendance(Base):
    """Attendance model representing student attendance records."""
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    status = Column(String(20), nullable=False)  # e.g., Present, Absent, Late

    student = relationship("Student", back_populates="attendances")
    class_ = relationship("Class", back_populates="attendances")
