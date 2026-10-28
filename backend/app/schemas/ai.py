from typing import Optional, List
from pydantic import BaseModel, Field

class DoubtQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    subject_id: Optional[str] = None
    chapter_id: Optional[str] = None

class DoubtQueryResponse(BaseModel):
    id: str
    question: str
    answer: str
    grade_tier: str  # Primary (3-5), Middle (6-8), High (9-12)
    step_by_step: List[str]
    key_takeaways: List[str]
    practice_question: Optional[str] = None

class HomeworkHintRequest(BaseModel):
    assignment_id: str
    question_text: str
    student_attempt: Optional[str] = None

class HomeworkHintResponse(BaseModel):
    guiding_hint: str
    clarifying_concept: str
    socratic_question: str

class AutoGradeAssistRequest(BaseModel):
    assignment_title: str
    question_instructions: str
    student_notes: Optional[str] = None
    max_marks: int
    submitted_files: List[str] = []

class AutoGradeAssistResponse(BaseModel):
    suggested_marks: float
    max_marks: int
    strengths: List[str]
    areas_for_improvement: List[str]
    feedback_remarks: str

class QuizQuestionItem(BaseModel):
    question: str
    options: List[str]
    correct_option_index: int
    explanation: str

class QuizGenerateRequest(BaseModel):
    chapter_id: str
    num_questions: int = Field(default=5, ge=1, le=10)
    difficulty: str = "medium"

class QuizGenerateResponse(BaseModel):
    title: str
    chapter_title: str
    questions: List[QuizQuestionItem]
