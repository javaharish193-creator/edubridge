from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, RoleEnum
from app.models.academic import Student
from app.models.content import Subject, Chapter
from app.models.assignment import Assignment, Submission
from app.models.audit import AIDoubt
from app.schemas.ai import (
    DoubtQueryRequest, DoubtQueryResponse,
    HomeworkHintRequest, HomeworkHintResponse,
    AutoGradeAssistRequest, AutoGradeAssistResponse,
    QuizGenerateRequest, QuizGenerateResponse
)
from app.services.ai_service import AIService
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/ai", tags=["AI Engine"])

@router.post("/doubt/ask", response_model=DoubtQueryResponse)
def ask_doubt(
    req: DoubtQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    grade_level = 8
    student = None
    if current_user.role == RoleEnum.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student and student.student_class:
            grade_level = student.student_class.grade_level

    subject_name = "General Science & Maths"
    if req.subject_id:
        sub = db.query(Subject).filter(Subject.id == req.subject_id).first()
        if sub:
            subject_name = sub.name

    chapter_title = None
    if req.chapter_id:
        chap = db.query(Chapter).filter(Chapter.id == req.chapter_id).first()
        if chap:
            chapter_title = chap.title

    result = AIService.solve_doubt(
        question=req.question,
        grade_level=grade_level,
        subject_name=subject_name,
        chapter_title=chapter_title
    )

    doubt_record_id = "ai-query"
    if student:
        doubt_rec = AIDoubt(
            student_id=student.id,
            subject_id=req.subject_id,
            chapter_id=req.chapter_id,
            question=req.question,
            answer=result["answer"],
            context_sources=[subject_name, chapter_title or "General"]
        )
        db.add(doubt_rec)
        db.commit()
        db.refresh(doubt_rec)
        doubt_record_id = doubt_rec.id

    return DoubtQueryResponse(
        id=doubt_record_id,
        question=req.question,
        answer=result["answer"],
        grade_tier=result["grade_tier"],
        step_by_step=result["step_by_step"],
        key_takeaways=result["key_takeaways"],
        practice_question=result.get("practice_question")
    )

@router.post("/homework/hint", response_model=HomeworkHintResponse)
def get_homework_hint(
    req: HomeworkHintRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assignment = db.query(Assignment).filter(Assignment.id == req.assignment_id).first()
    title = assignment.title if assignment else "Homework Assignment"

    res = AIService.get_homework_hint(
        assignment_title=title,
        question_text=req.question_text,
        student_attempt=req.student_attempt
    )
    return HomeworkHintResponse(**res)

@router.post("/grading/assist", response_model=AutoGradeAssistResponse)
def auto_grade_assist(
    req: AutoGradeAssistRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    res = AIService.auto_grade_assist(
        assignment_title=req.assignment_title,
        question_instructions=req.question_instructions,
        student_notes=req.student_notes,
        max_marks=req.max_marks,
        file_count=len(req.submitted_files)
    )
    return AutoGradeAssistResponse(**res)

@router.post("/quiz/generate", response_model=QuizGenerateResponse)
def generate_chapter_quiz(
    req: QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chap = db.query(Chapter).filter(Chapter.id == req.chapter_id).first()
    if not chap:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Chapter not found"})

    subject_name = chap.subject.name
    grade_level = chap.subject.target_class.grade_level

    res = AIService.generate_quiz(
        chapter_title=chap.title,
        subject_name=subject_name,
        grade_level=grade_level,
        num_questions=req.num_questions
    )
    return QuizGenerateResponse(**res)

@router.get("/doubts/history")
def get_doubt_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.STUDENT:
        return []
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return []
    doubts = db.query(AIDoubt).filter(AIDoubt.student_id == student.id).order_by(AIDoubt.created_at.desc()).limit(20).all()
    return [
        {
            "id": d.id,
            "question": d.question,
            "answer": d.answer,
            "sources": d.context_sources,
            "created_at": d.created_at.isoformat()
        }
        for d in doubts
    ]
