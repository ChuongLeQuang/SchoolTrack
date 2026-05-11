from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class AcademicYear:
    """
    EN: Academic Year Model (Quản lý Niên Khóa).
    VI: Model Niên Khóa để gom nhóm các lớp học.
    """
    year_code: str
    name: str
    start_date: date
    end_date: date
    status: str = "Active"  # Active, Ended


@dataclass
class Student:
    """
    EN: Student Model (Quản lý Sinh viên).
    VI: Model Sinh Viên chứa thông tin cá nhân cơ bản.
    """
    student_id: str
    full_name: str
    date_of_birth: date
    email: str
    phone_number: str
    study_status: str = "Studying"  # Studying, On Leave, Dropped, Graduated, Other
    tuition_balance: int = 0  # Số dư học phí hiện tại (VND)


@dataclass
class ClassInfo:
    """
    EN: Class Information Model (Quản lý Lớp học).
    VI: Model Lớp Học chứa thông tin chi tiết từng lớp.
    """
    class_code: str
    year_code: str  # Foreign Key to AcademicYear
    class_name: str
    location: str
    room: str
    session: str  # Morning, Afternoon, Evening
    schedule: str # Days of week
    time_slot: str # Specific time
    start_month_year: str  # e.g., '09/2026'
    end_date: date
    min_students: int
    max_students: int
    current_students: int = 0
    class_status: str = "Opening"  # Opening, Full, Not Opened, Closed


@dataclass
class Registration:
    """
    EN: Registration Model (Đăng ký Lớp học).
    VI: Model Đăng ký - cầu nối giữa Sinh viên và Lớp học.
    """
    student_id: str  # Foreign Key to Student
    class_code: str  # Foreign Key to ClassInfo
    registration_date: date
    registration_status: str = "Registered"  # Registered, Valid, Paid, Allocated
    notes: Optional[str] = None