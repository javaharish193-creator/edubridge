import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Class(Base):
    __tablename__ = "classes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grade_level = Column(Integer, nullable=False)  # 3 to 12
    section = Column(String(10), nullable=False)   # A, B, C, etc.
    academic_year = Column(String(20), nullable=False)  # e.g., "2026-2027"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('grade_level', 'section', 'academic_year', name='uq_grade_section_year'),
    )

    # Relationships
    students = relationship("Student", back_populates="student_class", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="target_class", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="target_class", cascade="all, delete-orphan")
    live_classes = relationship("LiveClass", back_populates="target_class", cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    class_id = Column(String(36), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    roll_number = Column(String(50), nullable=False)
    guardian_name = Column(String(255), nullable=True)
    guardian_phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('class_id', 'roll_number', name='uq_class_roll'),
    )

    # Relationships
    user = relationship("User", back_populates="student_profile")
    student_class = relationship("Class", back_populates="students")
    submissions = relationship("Submission", back_populates="student", cascade="all, delete-orphan")
    attendances = relationship("LiveAttendance", back_populates="student", cascade="all, delete-orphan")
