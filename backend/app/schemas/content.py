from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.content import MaterialTypeEnum

class SubjectCreate(BaseModel):
    class_id: str
    name: str
    code: str
    thumbnail_url: Optional[str] = None

class MaterialResponse(BaseModel):
    id: str
    chapter_id: str
    title: str
    material_type: MaterialTypeEnum
    file_key: str
    file_size_bytes: int
    is_downloadable: bool
    download_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChapterCreate(BaseModel):
    subject_id: str
    title: str
    order_index: int = 1
    release_at: Optional[datetime] = None

class ChapterResponse(BaseModel):
    id: str
    subject_id: str
    title: str
    order_index: int
    release_at: Optional[datetime] = None
    materials: List[MaterialResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

class SubjectResponse(BaseModel):
    id: str
    class_id: str
    name: str
    code: str
    thumbnail_url: Optional[str] = None
    chapter_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class SubjectTreeResponse(BaseModel):
    subject: SubjectResponse
    chapters: List[ChapterResponse]
