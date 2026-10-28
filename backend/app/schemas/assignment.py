from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.assignment import SubmissionStatusEnum

class AssignmentResponse(BaseModel):
    id: str
    class_id: str
    subject_id: str
    subject_name: Optional[str] = None
    title: str
    instructions: Optional[str] = None
    due_date: datetime
    max_marks: int = 100
    allow_late_submission: bool = False
    attachment_url: Optional[str] = None
    answer_key_url: Optional[str] = None
    status: Optional[str] = "PENDING"
    submitted_count: Optional[int] = 0
    graded_count: Optional[int] = 0
    total_students: Optional[int] = 0
    created_at: datetime

    class Config:
        from_attributes = True

class SubmissionFileItem(BaseModel):
    name: str
    url: str

class SubmissionResponse(BaseModel):
    id: Optional[str] = None
    assignment_id: str
    student_id: str
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    status: str
    submitted_at: Optional[datetime] = None
    marks_awarded: Optional[float] = None
    max_marks: Optional[int] = None
    feedback_remarks: Optional[str] = None
    student_notes: Optional[str] = None
    files: List[SubmissionFileItem] = []
    answer_key_url: Optional[str] = None
    graded_at: Optional[datetime] = None

class GradeSubmissionRequest(BaseModel):
    marks_awarded: Optional[float] = Field(None, ge=0)
    feedback_remarks: Optional[str] = None
    request_resubmission: bool = False

class PublishAnswerKeyRequest(BaseModel):
    force: bool = False
