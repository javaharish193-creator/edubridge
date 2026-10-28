from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, RoleEnum
from app.models.academic import Student, Class
from app.models.content import Subject
from app.models.assignment import Assignment, Submission, SubmissionStatusEnum
from app.schemas.assignment import (
    AssignmentResponse, SubmissionResponse, SubmissionFileItem,
    GradeSubmissionRequest, PublishAnswerKeyRequest
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.storage_service import save_uploaded_file, generate_signed_url
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="", tags=["Assignments"])

@router.post("/assignments/create", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    class_id: str = Form(...),
    subject_id: str = Form(...),
    title: str = Form(...),
    instructions: Optional[str] = Form(None),
    due_date: str = Form(...),
    max_marks: int = Form(100),
    allow_late_submission: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    try:
        parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
    except Exception:
        raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": "Invalid ISO 8601 due_date format"})

    if parsed_due_date <= datetime.utcnow():
        raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": "due_date must be in the future"})

    # Check subject belongs to class
    sub = db.query(Subject).filter(Subject.id == subject_id, Subject.class_id == class_id).first()
    if not sub:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": "Subject does not belong to the selected class"})

    attachment_key = None
    if file:
        content = await file.read()
        attachment_key, _ = save_uploaded_file(content, file.filename or "question_paper.pdf")

    assignment = Assignment(
        class_id=class_id,
        subject_id=subject_id,
        title=title.strip(),
        instructions=instructions,
        due_date=parsed_due_date,
        max_marks=max_marks,
        allow_late_submission=allow_late_submission,
        attachment_key=attachment_key,
        created_by=current_user.id
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    student_count = db.query(Student).filter(Student.class_id == class_id).count()

    return AssignmentResponse(
        id=assignment.id,
        class_id=assignment.class_id,
        subject_id=assignment.subject_id,
        subject_name=sub.name,
        title=assignment.title,
        instructions=assignment.instructions,
        due_date=assignment.due_date,
        max_marks=assignment.max_marks,
        allow_late_submission=assignment.allow_late_submission,
        attachment_url=generate_signed_url(assignment.attachment_key),
        answer_key_url=generate_signed_url(assignment.answer_key_key) if assignment.answer_key_published else None,
        status="PENDING",
        submitted_count=0,
        graded_count=0,
        total_students=student_count,
        created_at=assignment.created_at
    )

@router.get("/assignments/list", response_model=PaginatedResponse[AssignmentResponse])
def list_assignments(
    class_id: Optional[str] = None,
    subject_id: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Assignment).join(Subject)

    student_profile = None
    if current_user.role == RoleEnum.STUDENT:
        student_profile = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student_profile:
            return PaginatedResponse(items=[], page=page, page_size=page_size, total=0)
        # Grade locking rule: student always sees their own class
        query = query.filter(Assignment.class_id == student_profile.class_id)
    else:
        if class_id:
            query = query.filter(Assignment.class_id == class_id)

    if subject_id:
        query = query.filter(Assignment.subject_id == subject_id)

    total = query.count()
    assignments = query.order_by(Assignment.due_date.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    now = datetime.utcnow()

    for a in assignments:
        sub_count = db.query(Submission).filter(Submission.assignment_id == a.id).count()
        graded_count = db.query(Submission).filter(Submission.assignment_id == a.id, Submission.status == SubmissionStatusEnum.GRADED).count()
        total_st = db.query(Student).filter(Student.class_id == a.class_id).count()

        # Determine student specific status
        user_status = "PENDING"
        if student_profile:
            user_sub = db.query(Submission).filter(Submission.assignment_id == a.id, Submission.student_id == student_profile.id).first()
            if user_sub:
                user_status = user_sub.status.value
            elif now > a.due_date:
                user_status = "OVERDUE"

        if status_filter and user_status != status_filter.upper():
            continue

        items.append(AssignmentResponse(
            id=a.id,
            class_id=a.class_id,
            subject_id=a.subject_id,
            subject_name=a.subject.name,
            title=a.title,
            instructions=a.instructions,
            due_date=a.due_date,
            max_marks=a.max_marks,
            allow_late_submission=a.allow_late_submission,
            attachment_url=generate_signed_url(a.attachment_key),
            answer_key_url=generate_signed_url(a.answer_key_key) if a.answer_key_published else None,
            status=user_status,
            submitted_count=sub_count,
            graded_count=graded_count,
            total_students=total_st,
            created_at=a.created_at
        ))

    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

@router.get("/assignments/{id}", response_model=AssignmentResponse)
def get_assignment_detail(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    a = db.query(Assignment).filter(Assignment.id == id).first()
    if not a:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Assignment not found"})

    user_status = "PENDING"
    student_profile = None
    if current_user.role == RoleEnum.STUDENT:
        student_profile = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student_profile or student_profile.class_id != a.class_id:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Not permitted to view assignment of another class"})
        
        user_sub = db.query(Submission).filter(Submission.assignment_id == a.id, Submission.student_id == student_profile.id).first()
        if user_sub:
            user_status = user_sub.status.value
        elif datetime.utcnow() > a.due_date:
            user_status = "OVERDUE"

    sub_count = db.query(Submission).filter(Submission.assignment_id == a.id).count()
    graded_count = db.query(Submission).filter(Submission.assignment_id == a.id, Submission.status == SubmissionStatusEnum.GRADED).count()
    total_st = db.query(Student).filter(Student.class_id == a.class_id).count()

    return AssignmentResponse(
        id=a.id,
        class_id=a.class_id,
        subject_id=a.subject_id,
        subject_name=a.subject.name,
        title=a.title,
        instructions=a.instructions,
        due_date=a.due_date,
        max_marks=a.max_marks,
        allow_late_submission=a.allow_late_submission,
        attachment_url=generate_signed_url(a.attachment_key),
        answer_key_url=generate_signed_url(a.answer_key_key) if a.answer_key_published else None,
        status=user_status,
        submitted_count=sub_count,
        graded_count=graded_count,
        total_students=total_st,
        created_at=a.created_at
    )

@router.post("/assignments/{id}/submit", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_assignment(
    id: str,
    notes: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.STUDENT:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only students can submit assignments"})

    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Student profile not found"})

    assignment = db.query(Assignment).filter(Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Assignment not found"})

    if assignment.class_id != student.class_id:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Assignment does not belong to your class"})

    now = datetime.utcnow()
    is_late = now > assignment.due_date
    if is_late and not assignment.allow_late_submission:
        raise HTTPException(status_code=400, detail={"code": "LATE_NOT_ALLOWED", "message": "Late submissions are not accepted for this assignment"})

    if len(files) > 10:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": "Maximum 10 files allowed per submission"})

    stored_files = []
    for f in files:
        data = await f.read()
        if len(data) > 25 * 1024 * 1024:
            raise HTTPException(status_code=413, detail={"code": "FILE_TOO_LARGE", "message": f"File {f.filename} exceeds 25 MB limit"})
        key, _ = save_uploaded_file(data, f.filename or "page.pdf")
        stored_files.append({"name": f.filename or "page.pdf", "key": key})

    existing_sub = db.query(Submission).filter(Submission.assignment_id == id, Submission.student_id == student.id).first()
    status_val = SubmissionStatusEnum.LATE if is_late else SubmissionStatusEnum.SUBMITTED

    if existing_sub:
        existing_sub.file_keys = stored_files
        existing_sub.student_notes = notes
        existing_sub.status = status_val
        existing_sub.submitted_at = now
        sub_obj = existing_sub
    else:
        sub_obj = Submission(
            assignment_id=id,
            student_id=student.id,
            file_keys=stored_files,
            student_notes=notes,
            status=status_val,
            submitted_at=now
        )
        db.add(sub_obj)

    db.commit()
    db.refresh(sub_obj)

    file_items = [SubmissionFileItem(name=item["name"], url=generate_signed_url(item["key"])) for item in sub_obj.file_keys]
    return SubmissionResponse(
        id=sub_obj.id,
        assignment_id=sub_obj.assignment_id,
        student_id=sub_obj.student_id,
        student_name=current_user.full_name,
        roll_number=student.roll_number,
        status=sub_obj.status.value,
        submitted_at=sub_obj.submitted_at,
        marks_awarded=sub_obj.marks_awarded,
        max_marks=assignment.max_marks,
        feedback_remarks=sub_obj.feedback_remarks,
        student_notes=sub_obj.student_notes,
        files=file_items,
        answer_key_url=generate_signed_url(assignment.answer_key_key) if assignment.answer_key_published else None
    )

@router.get("/assignments/{id}/my-submission", response_model=SubmissionResponse)
def get_my_submission(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Student profile not found"})

    assignment = db.query(Assignment).filter(Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Assignment not found"})

    sub = db.query(Submission).filter(Submission.assignment_id == id, Submission.student_id == student.id).first()
    if not sub:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "No submission found for this assignment"})

    file_items = [SubmissionFileItem(name=item["name"], url=generate_signed_url(item["key"])) for item in sub.file_keys]
    return SubmissionResponse(
        id=sub.id,
        assignment_id=sub.assignment_id,
        student_id=sub.student_id,
        student_name=current_user.full_name,
        roll_number=student.roll_number,
        status=sub.status.value,
        submitted_at=sub.submitted_at,
        marks_awarded=sub.marks_awarded,
        max_marks=assignment.max_marks,
        feedback_remarks=sub.feedback_remarks,
        student_notes=sub.student_notes,
        files=file_items,
        answer_key_url=generate_signed_url(assignment.answer_key_key) if assignment.answer_key_published else None,
        graded_at=sub.graded_at
    )

# --- ADMIN: REVIEW QUEUE, GRADING & ANSWER KEYS ---
@router.get("/admin/assignments/{id}/submissions")
def get_assignment_submissions_queue(
    id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    assignment = db.query(Assignment).filter(Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Assignment not found"})

    students_query = db.query(Student).join(User).filter(Student.class_id == assignment.class_id)
    if search:
        s_pat = f"%{search.strip()}%"
        students_query = students_query.filter((User.full_name.ilike(s_pat)) | (Student.roll_number.ilike(s_pat)))

    students = students_query.order_by(Student.roll_number).all()
    now = datetime.utcnow()

    items = []
    for st in students:
        sub = db.query(Submission).filter(Submission.assignment_id == assignment.id, Submission.student_id == st.id).first()
        st_status = "PENDING"
        if sub:
            st_status = sub.status.value
        elif now > assignment.due_date:
            st_status = "OVERDUE"

        if status_filter and st_status != status_filter.upper():
            continue

        files_list = []
        if sub:
            files_list = [{"name": f["name"], "url": generate_signed_url(f["key"])} for f in sub.file_keys]

        items.append({
            "submission_id": sub.id if sub else None,
            "student_id": st.id,
            "student_name": st.user.full_name,
            "roll_number": st.roll_number,
            "status": st_status,
            "submitted_at": sub.submitted_at.isoformat() if sub and sub.submitted_at else None,
            "marks_awarded": sub.marks_awarded if sub else None,
            "feedback_remarks": sub.feedback_remarks if sub else None,
            "student_notes": sub.student_notes if sub else None,
            "files": files_list
        })

    total = len(items)
    paginated = items[(page - 1) * page_size : page * page_size]

    return {
        "assignment": {
            "id": assignment.id,
            "title": assignment.title,
            "max_marks": assignment.max_marks,
            "due_date": assignment.due_date.isoformat(),
            "answer_key_published": assignment.answer_key_published
        },
        "items": paginated,
        "page": page,
        "page_size": page_size,
        "total": total
    }

@router.patch("/admin/submissions/{id}/grade", response_model=SubmissionResponse)
def grade_submission(
    id: str,
    req: GradeSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    sub = db.query(Submission).filter(Submission.id == id).first()
    if not sub:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Submission not found"})

    assignment = sub.assignment
    if req.marks_awarded is not None and req.marks_awarded > assignment.max_marks:
        raise HTTPException(
            status_code=422,
            detail={"code": "VALIDATION_ERROR", "message": f"marks must be between 0 and {assignment.max_marks}"}
        )

    if req.request_resubmission:
        sub.status = SubmissionStatusEnum.RESUBMISSION_REQUESTED
        sub.feedback_remarks = req.feedback_remarks
    else:
        sub.status = SubmissionStatusEnum.GRADED
        sub.marks_awarded = req.marks_awarded
        sub.feedback_remarks = req.feedback_remarks
        sub.graded_at = datetime.utcnow()
        sub.graded_by = current_user.id

    db.commit()
    db.refresh(sub)

    file_items = [SubmissionFileItem(name=item["name"], url=generate_signed_url(item["key"])) for item in sub.file_keys]
    return SubmissionResponse(
        id=sub.id,
        assignment_id=sub.assignment_id,
        student_id=sub.student_id,
        student_name=sub.student.user.full_name,
        roll_number=sub.student.roll_number,
        status=sub.status.value,
        submitted_at=sub.submitted_at,
        marks_awarded=sub.marks_awarded,
        max_marks=assignment.max_marks,
        feedback_remarks=sub.feedback_remarks,
        student_notes=sub.student_notes,
        files=file_items,
        answer_key_url=generate_signed_url(assignment.answer_key_key) if assignment.answer_key_published else None,
        graded_at=sub.graded_at
    )

@router.post("/admin/assignments/{id}/answer-key")
async def upload_answer_key(
    id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    assignment = db.query(Assignment).filter(Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Assignment not found"})

    content = await file.read()
    key, _ = save_uploaded_file(content, file.filename or "answer_key.pdf")
    assignment.answer_key_key = key
    assignment.answer_key_published = False
    db.commit()

    return {"message": "Answer key uploaded", "published": False}

@router.post("/admin/assignments/{id}/publish-answer-key")
def publish_answer_key(
    id: str,
    req: PublishAnswerKeyRequest = PublishAnswerKeyRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    assignment = db.query(Assignment).filter(Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Assignment not found"})

    if not assignment.answer_key_key:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": "No answer key has been uploaded for this assignment"})

    if datetime.utcnow() < assignment.due_date and not req.force:
        raise HTTPException(
            status_code=400,
            detail={"code": "DUE_DATE_NOT_PASSED", "message": "Due date has not passed yet. Use force=true to publish early."}
        )

    assignment.answer_key_published = True
    db.commit()

    student_count = db.query(Student).filter(Student.class_id == assignment.class_id).count()
    return {
        "message": "Answer key published",
        "published": True,
        "notified_students": student_count
    }
