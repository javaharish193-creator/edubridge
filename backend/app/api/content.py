from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, RoleEnum
from app.models.academic import Student
from app.models.content import Subject, Chapter, Material
from app.schemas.content import SubjectTreeResponse, SubjectResponse, ChapterResponse, MaterialResponse
from app.services.storage_service import generate_signed_url
from app.api.deps import get_current_user

router = APIRouter(prefix="/content", tags=["Content"])

@router.get("/subjects", response_model=List[SubjectResponse])
def get_user_subjects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Subject)
    if current_user.role == RoleEnum.STUDENT:
        st = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not st:
            return []
        query = query.filter(Subject.class_id == st.class_id)
    subjects = query.order_by(Subject.name).all()
    res = []
    for s in subjects:
        c_count = db.query(Chapter).filter(Chapter.subject_id == s.id).count()
        res.append(SubjectResponse(
            id=s.id,
            class_id=s.class_id,
            name=s.name,
            code=s.code,
            thumbnail_url=s.thumbnail_url,
            chapter_count=c_count,
            created_at=s.created_at
        ))
    return res

@router.get("/subjects/{subject_id}/materials", response_model=SubjectTreeResponse)
def get_subject_materials(subject_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sub = db.query(Subject).filter(Subject.id == subject_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Subject not found"})

    # Grade locking rule
    if current_user.role == RoleEnum.STUDENT:
        st = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not st or st.class_id != sub.class_id:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Access to materials of this class is not permitted"})

    now = datetime.utcnow()
    chapters = db.query(Chapter).filter(Chapter.subject_id == sub.id).order_by(Chapter.order_index).all()
    chapter_responses = []

    for c in chapters:
        # If student, check release_at schedule
        if current_user.role == RoleEnum.STUDENT and c.release_at and c.release_at > now:
            continue

        materials = db.query(Material).filter(Material.chapter_id == c.id).order_by(Material.created_at).all()
        mat_responses = []
        for m in materials:
            mat_responses.append(MaterialResponse(
                id=m.id,
                chapter_id=m.chapter_id,
                title=m.title,
                material_type=m.material_type,
                file_key=m.file_key,
                file_size_bytes=m.file_size_bytes,
                is_downloadable=m.is_downloadable,
                download_url=generate_signed_url(m.file_key),
                created_at=m.created_at
            ))

        chapter_responses.append(ChapterResponse(
            id=c.id,
            subject_id=c.subject_id,
            title=c.title,
            order_index=c.order_index,
            release_at=c.release_at,
            materials=mat_responses,
            created_at=c.created_at
        ))

    sub_resp = SubjectResponse(
        id=sub.id,
        class_id=sub.class_id,
        name=sub.name,
        code=sub.code,
        thumbnail_url=sub.thumbnail_url,
        chapter_count=len(chapter_responses),
        created_at=sub.created_at
    )

    return SubjectTreeResponse(
        subject=sub_resp,
        chapters=chapter_responses
    )
