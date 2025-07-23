"""
CRUD repositories for User, Student, Class, and Attendance models.
"""

from .models import User, Student, Class, Attendance
from .repository_base import BaseRepository

# PUBLIC_INTERFACE
class UserRepository(BaseRepository):
    """CRUD repository for User entity."""
    def __init__(self):
        super().__init__(User)

# PUBLIC_INTERFACE
class StudentRepository(BaseRepository):
    """CRUD repository for Student entity."""
    def __init__(self):
        super().__init__(Student)

# PUBLIC_INTERFACE
class ClassRepository(BaseRepository):
    """CRUD repository for Class entity."""
    def __init__(self):
        super().__init__(Class)

# PUBLIC_INTERFACE
class AttendanceRepository(BaseRepository):
    """CRUD repository for Attendance entity."""
    def __init__(self):
        super().__init__(Attendance)
