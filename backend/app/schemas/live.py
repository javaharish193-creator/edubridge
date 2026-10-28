from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.live import LiveClassStatusEnum

class LiveClassStartRequest(BaseModel):
    class_id: str
    subject_id: str
    title: str
    scheduled_start: Optional[datetime] = None
    duration_minutes: int = 45

class LiveClassResponse(BaseModel):
    id: str
    class_id: str
    subject_id: str
    subject_name: Optional[str] = None
    title: str
    meeting_room_id: str
    scheduled_start: datetime
    duration_minutes: int
    status: LiveClassStatusEnum
    can_join: bool = False
    notified_students: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class LiveJoinResponse(BaseModel):
    provider: str = "jitsi"
    domain: str = "meet.jit.si"
    room: str
    jwt: str
    display_name: str
    start_muted: bool = True
    is_moderator: bool = False
    expires_in: int = 3600

class LiveLeaveResponse(BaseModel):
    message: str = "left"
    duration_seconds: int

class LiveEndResponse(BaseModel):
    status: str
    attendees: int

class AttendanceSummary(BaseModel):
    enrolled: int
    attended: int
    absent: int
    average_minutes: float

class AttendanceItem(BaseModel):
    student_id: str
    roll_number: str
    student_name: str
    present: bool
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    duration_minutes: float = 0.0
    reconnects: int = 0

class LiveAttendanceReport(BaseModel):
    live_class: dict
    summary: AttendanceSummary
    items: List[AttendanceItem]
