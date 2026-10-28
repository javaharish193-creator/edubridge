import uuid
from datetime import datetime
import enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class MaterialTypeEnum(str, enum.Enum):
    PDF_NOTES = "PDF_NOTES"
    VIDEO_STREAM = "VIDEO_STREAM"
    DOC = "DOC"
    EXTERNAL_LINK = "EXTERNAL_LINK"

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(String(36), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    target_class = relationship("Class", back_populates="subjects")
    chapters = relationship("Chapter", back_populates="subject", cascade="all, delete-orphan", order_by="Chapter.order_index")
    assignments = relationship("Assignment", back_populates="subject", cascade="all, delete-orphan")
    live_classes = relationship("LiveClass", back_populates="subject", cascade="all, delete-orphan")

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    order_index = Column(Integer, default=1, nullable=False)
    release_at = Column(DateTime, nullable=True)  # Nullable or scheduled release
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    subject = relationship("Subject", back_populates="chapters")
    materials = relationship("Material", back_populates="chapter", cascade="all, delete-orphan")

class Material(Base):
    __tablename__ = "materials"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chapter_id = Column(String(36), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    material_type = Column(Enum(MaterialTypeEnum), default=MaterialTypeEnum.PDF_NOTES, nullable=False)
    file_key = Column(String(500), nullable=False)  # Storage key or external URL
    file_size_bytes = Column(Integer, default=0, nullable=False)
    is_downloadable = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    chapter = relationship("Chapter", back_populates="materials")
