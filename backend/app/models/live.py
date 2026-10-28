import uuid
from datetime import datetime
import enum
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class LiveClassStatusEnum(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class LiveClass(Base):
    __tablename__ = "live_classes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(String(36), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    meeting_room_id = Column(String(100), unique=True, nullable=False, index=True)
    meeting_passcode = Column(String(50), nullable=True)
    scheduled_start = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=45, nullable=False)
    status = Column(Enum(LiveClassStatusEnum), default=LiveClassStatusEnum.SCHEDULED, nullable=False)
    recording_url = Column(String(500), nullable=True)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    target_class = relationship("Class", back_populates="live_classes")
    subject = relationship("Subject", back_populates="live_classes")
    attendances = relationship("LiveAttendance", back_populates="live_class", cascade="all, delete-orphan")

class LiveAttendance(Base):
    __tablename__ = "live_attendance"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    live_class_id = Column(String(36), ForeignKey("live_classes.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    left_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0, nullable=False)
    reconnects = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint('live_class_id', 'student_id', name='uq_live_student_attendance'),
    )

    live_class = relationship("LiveClass", back_populates="attendances")
    student = relationship("Student", back_populates="attendances")
