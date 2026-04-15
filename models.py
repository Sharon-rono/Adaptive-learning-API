from pydantic import BaseModel
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    email: str

class AnswerSubmit(BaseModel):
    student_id: int
    topic: str
    question: str
    answer_given: str
    correct_answer: str
    time_taken_ms: int

class QuestionRequest(BaseModel):
    topic: str
    difficulty: str  # "easy", "medium", "hard"