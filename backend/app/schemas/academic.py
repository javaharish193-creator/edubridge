from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ClassCreate(BaseModel):
    grade_level: int = Field(ge=3, le=12)
    section: str = Field(min_length=1, max_length=10)
    academic_year: str = Field(default="2026-2027")

class ClassResponse(BaseModel):
    id: str
    grade_level: int
    section: str
    academic_year: str
    student_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class StudentCreate(BaseModel):
    class_id: str
    phone_number: str
    full_name: str
    roll_number: str
    password: Optional[str] = "Student@123"
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    roll_number: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    is_active: Optional[bool] = None

class StudentResponse(BaseModel):
    id: str
    user_id: str
    class_id: str
    grade_level: int
    section: str
    roll_number: str
    full_name: str
    phone_number: str
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class StudentImportRowError(BaseModel):
    row: int
    roll_number: Optional[str] = None
    error: str

class StudentImportResponse(BaseModel):
    imported_count: int
    skipped_count: int
    errors: List[StudentImportRowError]

class StudentActivityResponse(BaseModel):
    student_id: str
    full_name: str
    roll_number: str
    class_name: str
    attendance_percentage: float
    total_assignments: int
    submitted_assignments: int
    graded_assignments: int
    average_score: float
    recent_activity: List[dict]

class AdminStatsResponse(BaseModel):
    total_students: int
    total_classes: int
    total_subjects: int
    total_assignments: int
    pending_submissions: int
    live_classes_today: int
    recent_submissions: List[dict]
