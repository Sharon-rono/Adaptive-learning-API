import asyncpg
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from database import create_tables, get_connection
from models import StudentCreate, AnswerSubmit, QuestionRequest
from ai import get_feedback, generate_question
from analytics import get_struggling_students, get_hardest_topic, get_student_report

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()  # runs on startup
    yield

app = FastAPI(title="Adaptive Learning System", lifespan=lifespan)


# --- Student routes ---

@app.post("/students")
async def create_student(student: StudentCreate):
    conn = await get_connection()
    try:
        row = await conn.fetchrow("""
            INSERT INTO students (name, email)
            VALUES ($1, $2)
            RETURNING student_id, name, email, joined_at;
        """, student.name, student.email)
        return dict(row)
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Email already registered.")
    finally:
        await conn.close()


@app.get("/students/{student_id}")
async def get_student(student_id: int):
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            "SELECT * FROM students WHERE student_id = $1;", student_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Student not found.")
        return dict(row)
    finally:
        await conn.close()


# --- Core answer submission ---

@app.post("/submit-answer")
async def submit_answer(payload: AnswerSubmit):
    # Step 1: check correctness
    is_correct = payload.answer_given.strip().lower() == payload.correct_answer.strip().lower()

    # Step 2: get AI feedback
    try:
        feedback = get_feedback(
            topic=payload.topic,
            question=payload.question,
            answer_given=payload.answer_given,
            correct_answer=payload.correct_answer,
            is_correct=is_correct
        )
    except Exception as e:
        feedback = f"AI feedback unavailable: {str(e)}"

    # Step 3: save to quiz_results
    conn = await get_connection()
    try:
        await conn.execute("""
            INSERT INTO quiz_results 
                (student_id, topic, answer_given, is_correct, time_taken_ms, ai_feedback)
            VALUES ($1, $2, $3, $4, $5, $6);
        """, payload.student_id, payload.topic, payload.answer_given,
            is_correct, payload.time_taken_ms, feedback)

        # Step 4: update performance_history (upsert)
        await conn.execute("""
            INSERT INTO performance_history (student_id, topic, total_questions, correct_count, avg_accuracy, avg_time_ms)
            VALUES ($1, $2, 1, $3, $4, $5)
            ON CONFLICT (student_id, topic) DO UPDATE SET
                total_questions = performance_history.total_questions + 1,
                correct_count   = performance_history.correct_count + EXCLUDED.correct_count,
                avg_accuracy    = ROUND(
                                    (performance_history.correct_count + EXCLUDED.correct_count)::NUMERIC /
                                    (performance_history.total_questions + 1) * 100, 2),
                avg_time_ms     = ROUND(
                                    (performance_history.avg_time_ms * performance_history.total_questions + $5) /
                                    (performance_history.total_questions + 1), 2),
                last_updated    = CURRENT_TIMESTAMP;
        """, payload.student_id, payload.topic,
            1 if is_correct else 0,
            100.0 if is_correct else 0.0,
            payload.time_taken_ms)

    finally:
        await conn.close()

    # Step 5: return result to student
    return {
        "is_correct": is_correct,
        "correct_answer": payload.correct_answer,
        "ai_feedback": feedback
    }


# --- Question generation ---

@app.post("/generate-question")
async def generate_quiz_question(payload: QuestionRequest):
    try:
        question = generate_question(payload.topic, payload.difficulty)
        return {"question": question}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")


# --- Progress & analytics routes ---

@app.get("/students/{student_id}/progress")
async def student_progress(student_id: int):
    report = await get_student_report(student_id)
    if not report:
        raise HTTPException(status_code=404, detail="No data found for this student.")
    return report


@app.get("/analytics/struggling-students")
async def struggling_students(threshold: float = 50.0):
    return await get_struggling_students(threshold)


@app.get("/analytics/hardest-topics")
async def hardest_topics():
    return await get_hardest_topic()
