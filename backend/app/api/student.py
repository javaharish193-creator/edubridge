from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, RoleEnum
from app.models.academic import Student
from app.models.content import Subject, Chapter, Material
from app.models.assignment import Assignment, Submission, SubmissionStatusEnum
from app.models.live import LiveClass, LiveClassStatusEnum
from app.services.storage_service import generate_signed_url
from app.api.deps import require_student

router = APIRouter(prefix="/student", tags=["Student"])

@router.get("/dashboard")
def get_student_dashboard(
    deps: tuple[User, Student] = Depends(require_student),
    db: Session = Depends(get_db)
):
    user, student = deps
    target_class = student.student_class
    now = datetime.utcnow()

    # Subjects
    subjects = db.query(Subject).filter(Subject.class_id == target_class.id).all()
    subject_list = []
    for s in subjects:
        mats_count = db.query(Material).join(Chapter).filter(Chapter.subject_id == s.id).count()
        subject_list.append({
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "thumbnail_url": s.thumbnail_url,
            "materials_count": mats_count
        })

    # Assignments
    assignments = db.query(Assignment).filter(Assignment.class_id == target_class.id).order_by(Assignment.due_date.asc()).all()
    pending_assignments = []
    submitted_assignments = []

    for a in assignments:
        sub = db.query(Submission).filter(Submission.assignment_id == a.id, Submission.student_id == student.id).first()
        st_status = "PENDING"
        if sub:
            st_status = sub.status.value
        elif now > a.due_date:
            st_status = "OVERDUE"

        item = {
            "id": a.id,
            "title": a.title,
            "subject_name": a.subject.name,
            "due_date": a.due_date.isoformat(),
            "max_marks": a.max_marks,
            "status": st_status,
            "marks_awarded": sub.marks_awarded if sub else None,
            "attachment_url": generate_signed_url(a.attachment_key)
        }

        if st_status in ["PENDING", "OVERDUE", "RESUBMISSION_REQUESTED"]:
            pending_assignments.append(item)
        else:
            submitted_assignments.append(item)

    # Live Classes
    upcoming_live = db.query(LiveClass).filter(
        LiveClass.class_id == target_class.id,
        LiveClass.status.in_([LiveClassStatusEnum.IN_PROGRESS, LiveClassStatusEnum.SCHEDULED])
    ).order_by(LiveClass.scheduled_start.asc()).all()

    live_list = []
    for l in upcoming_live:
        live_list.append({
            "id": l.id,
            "title": l.title,
            "subject_name": l.subject.name,
            "scheduled_start": l.scheduled_start.isoformat(),
            "duration_minutes": l.duration_minutes,
            "status": l.status.value,
            "can_join": l.status == LiveClassStatusEnum.IN_PROGRESS
        })

    # Recent materials
    recent_mats = db.query(Material).join(Chapter).join(Subject).filter(
        Subject.class_id == target_class.id
    ).order_by(Material.created_at.desc()).limit(6).all()

    recent_materials_list = []
    for m in recent_mats:
        recent_materials_list.append({
            "id": m.id,
            "title": m.title,
            "chapter_title": m.chapter.title,
            "subject_name": m.chapter.subject.name,
            "material_type": m.material_type.value,
            "file_size_bytes": m.file_size_bytes,
            "is_downloadable": m.is_downloadable,
            "download_url": generate_signed_url(m.file_key)
        })

    return {
        "student": {
            "id": student.id,
            "full_name": user.full_name,
            "roll_number": student.roll_number,
            "grade_level": target_class.grade_level,
            "section": target_class.section,
            "academic_year": target_class.academic_year
        },
        "stats": {
            "total_subjects": len(subjects),
            "pending_homework": len(pending_assignments),
            "completed_homework": len(submitted_assignments),
            "upcoming_live_count": len(live_list)
        },
        "subjects": subject_list,
        "pending_assignments": pending_assignments,
        "submitted_assignments": submitted_assignments,
        "upcoming_live_classes": live_list,
        "recent_materials": recent_materials_list
    }
