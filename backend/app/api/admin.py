import io
import csv
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User, RoleEnum
from app.models.academic import Class, Student
from app.models.content import Subject, Chapter, Material, MaterialTypeEnum
from app.models.assignment import Assignment, Submission, SubmissionStatusEnum
from app.models.live import LiveClass, LiveClassStatusEnum, LiveAttendance
from app.schemas.academic import (
    ClassCreate, ClassResponse, StudentCreate, StudentUpdate, StudentResponse,
    StudentImportResponse, StudentImportRowError, StudentActivityResponse, AdminStatsResponse
)
from app.schemas.content import SubjectCreate, SubjectResponse, ChapterCreate, ChapterResponse, MaterialResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.auth_service import get_password_hash
from app.services.storage_service import save_uploaded_file, generate_signed_url
from app.api.deps import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

# --- CLASSES ---
@router.post("/classes", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(req: ClassCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    existing = db.query(Class).filter(
        Class.grade_level == req.grade_level,
        Class.section == req.section.upper(),
        Class.academic_year == req.academic_year
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CLASS_EXISTS", "message": f"Class {req.grade_level}-{req.section} already exists for {req.academic_year}"}
        )
    new_class = Class(
        grade_level=req.grade_level,
        section=req.section.upper(),
        academic_year=req.academic_year
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return ClassResponse(
        id=new_class.id,
        grade_level=new_class.grade_level,
        section=new_class.section,
        academic_year=new_class.academic_year,
        student_count=0,
        created_at=new_class.created_at
    )

@router.get("/classes", response_model=List[ClassResponse])
def list_classes(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    classes = db.query(Class).order_by(Class.grade_level, Class.section).all()
    res = []
    for c in classes:
        st_count = db.query(Student).filter(Student.class_id == c.id).count()
        res.append(ClassResponse(
            id=c.id,
            grade_level=c.grade_level,
            section=c.section,
            academic_year=c.academic_year,
            student_count=st_count,
            created_at=c.created_at
        ))
    return res

# --- STUDENTS ---
@router.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(req: StudentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    # Check phone
    if db.query(User).filter(User.phone_number == req.phone_number.strip()).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "PHONE_EXISTS", "message": "Phone number is already registered"}
        )
    # Check class
    target_class = db.query(Class).filter(Class.id == req.class_id).first()
    if not target_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Target class not found"}
        )
    # Check roll number in this class
    if db.query(Student).filter(Student.class_id == req.class_id, Student.roll_number == req.roll_number.strip()).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "ROLL_EXISTS", "message": f"Roll number {req.roll_number} already exists in this class"}
        )

    user = User(
        phone_number=req.phone_number.strip(),
        full_name=req.full_name.strip(),
        password_hash=get_password_hash(req.password or "Student@123"),
        role=RoleEnum.STUDENT,
        is_active=True
    )
    db.add(user)
    db.flush()

    student = Student(
        user_id=user.id,
        class_id=req.class_id,
        roll_number=req.roll_number.strip(),
        guardian_name=req.guardian_name,
        guardian_phone=req.guardian_phone
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return StudentResponse(
        id=student.id,
        user_id=user.id,
        class_id=student.class_id,
        grade_level=target_class.grade_level,
        section=target_class.section,
        roll_number=student.roll_number,
        full_name=user.full_name,
        phone_number=user.phone_number,
        guardian_name=student.guardian_name,
        guardian_phone=student.guardian_phone,
        is_active=user.is_active,
        created_at=student.created_at
    )

@router.get("/students", response_model=PaginatedResponse[StudentResponse])
def list_students(
    class_id: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    query = db.query(Student).join(User).join(Class)
    if class_id:
        query = query.filter(Student.class_id == class_id)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter((User.full_name.ilike(search_pattern)) | (Student.roll_number.ilike(search_pattern)) | (User.phone_number.ilike(search_pattern)))

    total = query.count()
    students = query.order_by(Class.grade_level, Student.roll_number).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for s in students:
        items.append(StudentResponse(
            id=s.id,
            user_id=s.user.id,
            class_id=s.class_id,
            grade_level=s.student_class.grade_level,
            section=s.student_class.section,
            roll_number=s.roll_number,
            full_name=s.user.full_name,
            phone_number=s.user.phone_number,
            guardian_name=s.guardian_name,
            guardian_phone=s.guardian_phone,
            is_active=s.user.is_active,
            created_at=s.created_at
        ))

    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

@router.patch("/students/{id}", response_model=StudentResponse)
def update_student(id: str, req: StudentUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Student not found"})

    if req.full_name is not None:
        student.user.full_name = req.full_name.strip()
    if req.roll_number is not None:
        student.roll_number = req.roll_number.strip()
    if req.guardian_name is not None:
        student.guardian_name = req.guardian_name
    if req.guardian_phone is not None:
        student.guardian_phone = req.guardian_phone
    if req.is_active is not None:
        student.user.is_active = req.is_active

    db.commit()
    db.refresh(student)

    return StudentResponse(
        id=student.id,
        user_id=student.user.id,
        class_id=student.class_id,
        grade_level=student.student_class.grade_level,
        section=student.student_class.section,
        roll_number=student.roll_number,
        full_name=student.user.full_name,
        phone_number=student.user.phone_number,
        guardian_name=student.guardian_name,
        guardian_phone=student.guardian_phone,
        is_active=student.user.is_active,
        created_at=student.created_at
    )

@router.post("/students/import", response_model=StudentImportResponse)
def import_students_csv(
    file: UploadFile = File(...),
    class_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    target_class = db.query(Class).filter(Class.id == class_id).first()
    if not target_class:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Class not found"})

    content = file.file.read().decode('utf-8-sig', errors='ignore')
    reader = csv.DictReader(io.StringIO(content))
    
    imported = 0
    skipped = 0
    errors = []

    row_idx = 1
    for row in reader:
        row_idx += 1
        roll = row.get("roll_number") or row.get("Roll Number") or row.get("roll")
        name = row.get("full_name") or row.get("Full Name") or row.get("name")
        phone = row.get("phone_number") or row.get("Phone Number") or row.get("phone")
        guardian = row.get("guardian_name") or row.get("Guardian Name") or ""
        g_phone = row.get("guardian_phone") or row.get("Guardian Phone") or ""

        if not roll or not name or not phone:
            errors.append(StudentImportRowError(row=row_idx, roll_number=roll, error="Missing required fields"))
            skipped += 1
            continue

        roll = roll.strip()
        phone = phone.strip()

        # Check existing phone or roll
        if db.query(User).filter(User.phone_number == phone).first():
            errors.append(StudentImportRowError(row=row_idx, roll_number=roll, error=f"Phone {phone} already exists"))
            skipped += 1
            continue

        if db.query(Student).filter(Student.class_id == class_id, Student.roll_number == roll).first():
            errors.append(StudentImportRowError(row=row_idx, roll_number=roll, error=f"Roll number {roll} already exists in class"))
            skipped += 1
            continue

        try:
            u = User(
                phone_number=phone,
                full_name=name.strip(),
                password_hash=get_password_hash("Student@123"),
                role=RoleEnum.STUDENT,
                is_active=True
            )
            db.add(u)
            db.flush()

            st = Student(
                user_id=u.id,
                class_id=class_id,
                roll_number=roll,
                guardian_name=guardian.strip() or None,
                guardian_phone=g_phone.strip() or None
            )
            db.add(st)
            imported += 1
        except Exception as e:
            errors.append(StudentImportRowError(row=row_idx, roll_number=roll, error=str(e)))
            skipped += 1

    db.commit()
    return StudentImportResponse(
        imported_count=imported,
        skipped_count=skipped,
        errors=errors
    )

@router.get("/students/{id}/activity", response_model=StudentActivityResponse)
def get_student_activity(id: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Student not found"})

    total_assignments = db.query(Assignment).filter(Assignment.class_id == student.class_id).count()
    submissions = db.query(Submission).filter(Submission.student_id == student.id).all()
    submitted_count = len(submissions)
    graded_count = sum(1 for s in submissions if s.status == SubmissionStatusEnum.GRADED)

    graded_scores = [s.marks_awarded for s in submissions if s.marks_awarded is not None]
    avg_score = round(sum(graded_scores) / len(graded_scores), 1) if graded_scores else 0.0

    total_live = db.query(LiveClass).filter(LiveClass.class_id == student.class_id, LiveClass.status == LiveClassStatusEnum.COMPLETED).count()
    attended_live = db.query(LiveAttendance).filter(LiveAttendance.student_id == student.id).count()
    attendance_pct = round((attended_live / total_live * 100), 1) if total_live > 0 else 100.0

    recent_activity = []
    for s in submissions[-5:]:
        recent_activity.append({
            "type": "assignment",
            "title": s.assignment.title,
            "status": s.status.value,
            "marks": f"{s.marks_awarded}/{s.assignment.max_marks}" if s.marks_awarded is not None else "Not graded",
            "date": s.submitted_at.isoformat()
        })

    return StudentActivityResponse(
        student_id=student.id,
        full_name=student.user.full_name,
        roll_number=student.roll_number,
        class_name=f"Class {student.student_class.grade_level}-{student.student_class.section}",
        attendance_percentage=attendance_pct,
        total_assignments=total_assignments,
        submitted_assignments=submitted_count,
        graded_assignments=graded_count,
        average_score=avg_score,
        recent_activity=recent_activity
    )

@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    total_students = db.query(Student).count()
    total_classes = db.query(Class).count()
    total_subjects = db.query(Subject).count()
    total_assignments = db.query(Assignment).count()
    pending_submissions = db.query(Submission).filter(Submission.status.in_([SubmissionStatusEnum.SUBMITTED, SubmissionStatusEnum.LATE])).count()
    live_today = db.query(LiveClass).filter(LiveClass.status.in_([LiveClassStatusEnum.SCHEDULED, LiveClassStatusEnum.IN_PROGRESS])).count()

    recent = db.query(Submission).order_by(Submission.submitted_at.desc()).limit(5).all()
    recent_list = []
    for r in recent:
        recent_list.append({
            "id": r.id,
            "student_name": r.student.user.full_name,
            "roll_number": r.student.roll_number,
            "assignment_title": r.assignment.title,
            "status": r.status.value,
            "submitted_at": r.submitted_at.isoformat()
        })

    return AdminStatsResponse(
        total_students=total_students,
        total_classes=total_classes,
        total_subjects=total_subjects,
        total_assignments=total_assignments,
        pending_submissions=pending_submissions,
        live_classes_today=live_today,
        recent_submissions=recent_list
    )

# --- SUBJECTS, CHAPTERS, MATERIALS ---
@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(req: SubjectCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    target_class = db.query(Class).filter(Class.id == req.class_id).first()
    if not target_class:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Class not found"})

    sub = Subject(
        class_id=req.class_id,
        name=req.name.strip(),
        code=req.code.strip().upper(),
        thumbnail_url=req.thumbnail_url
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return SubjectResponse(
        id=sub.id,
        class_id=sub.class_id,
        name=sub.name,
        code=sub.code,
        thumbnail_url=sub.thumbnail_url,
        chapter_count=0,
        created_at=sub.created_at
    )

@router.get("/subjects", response_model=List[SubjectResponse])
def list_subjects(class_id: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    query = db.query(Subject)
    if class_id:
        query = query.filter(Subject.class_id == class_id)
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

@router.post("/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
def create_chapter(req: ChapterCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    subject = db.query(Subject).filter(Subject.id == req.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Subject not found"})

    chap = Chapter(
        subject_id=req.subject_id,
        title=req.title.strip(),
        order_index=req.order_index,
        release_at=req.release_at
    )
    db.add(chap)
    db.commit()
    db.refresh(chap)
    return ChapterResponse(
        id=chap.id,
        subject_id=chap.subject_id,
        title=chap.title,
        order_index=chap.order_index,
        release_at=chap.release_at,
        materials=[],
        created_at=chap.created_at
    )

@router.post("/materials", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def upload_material(
    chapter_id: str = Form(...),
    title: str = Form(...),
    material_type: MaterialTypeEnum = Form(MaterialTypeEnum.PDF_NOTES),
    is_downloadable: bool = Form(True),
    file: Optional[UploadFile] = File(None),
    external_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Chapter not found"})

    if file:
        content = await file.read()
        file_key, size = save_uploaded_file(content, file.filename or "document.pdf")
    elif external_url:
        file_key = external_url
        size = 0
    else:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": "Either file or external_url must be provided"})

    mat = Material(
        chapter_id=chapter_id,
        title=title.strip(),
        material_type=material_type,
        file_key=file_key,
        file_size_bytes=size,
        is_downloadable=is_downloadable
    )
    db.add(mat)
    db.commit()
    db.refresh(mat)

    return MaterialResponse(
        id=mat.id,
        chapter_id=mat.chapter_id,
        title=mat.title,
        material_type=mat.material_type,
        file_key=mat.file_key,
        file_size_bytes=mat.file_size_bytes,
        is_downloadable=mat.is_downloadable,
        download_url=generate_signed_url(mat.file_key),
        created_at=mat.created_at
    )

@router.delete("/materials/{id}", response_model=MessageResponse)
def delete_material(id: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    mat = db.query(Material).filter(Material.id == id).first()
    if not mat:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Material not found"})
    db.delete(mat)
    db.commit()
    return MessageResponse(message="Material deleted successfully")
