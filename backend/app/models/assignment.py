import uuid
from datetime import datetime
import enum
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class SubmissionStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    LATE = "LATE"
    GRADED = "GRADED"
    RESUBMISSION_REQUESTED = "RESUBMISSION_REQUESTED"

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(String(36), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    instructions = Column(Text, nullable=True)
    attachment_key = Column(String(500), nullable=True)  # Question paper
    answer_key_key = Column(String(500), nullable=True)  # Solution / Answer key
    answer_key_published = Column(Boolean, default=False, nullable=False)
    max_marks = Column(Integer, default=100, nullable=False)
    due_date = Column(DateTime, nullable=False, index=True)
    allow_late_submission = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    target_class = relationship("Class", back_populates="assignments")
    subject = relationship("Subject", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = Column(String(36), ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    file_keys = Column(JSON, default=list, nullable=False)  # list of {name: str, key: str}
    student_notes = Column(Text, nullable=True)
    marks_awarded = Column(Float, nullable=True)
    feedback_remarks = Column(Text, nullable=True)
    status = Column(Enum(SubmissionStatusEnum), default=SubmissionStatusEnum.SUBMITTED, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    graded_at = Column(DateTime, nullable=True)
    graded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        UniqueConstraint('assignment_id', 'student_id', name='uq_assignment_student'),
    )

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("Student", back_populates="submissions")
