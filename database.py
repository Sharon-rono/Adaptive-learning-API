import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASES_URL")

async def get_connection():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise

async def create_tables():
    conn = await get_connection()
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id  SERIAL PRIMARY KEY,
                name        VARCHAR(100) NOT NULL,
                email       VARCHAR(255) NOT NULL UNIQUE,
                joined_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                result_id     SERIAL PRIMARY KEY,
                student_id    INT NOT NULL,
                topic         VARCHAR(100) NOT NULL,
                answer_given  TEXT NOT NULL,
                is_correct    BOOLEAN NOT NULL,
                time_taken_ms INT NOT NULL,
                ai_feedback   TEXT,
                answered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS performance_history (
                history_id      SERIAL PRIMARY KEY,
                student_id      INT NOT NULL,
                topic           VARCHAR(100) NOT NULL,
                total_questions INT NOT NULL DEFAULT 0,
                correct_count   INT NOT NULL DEFAULT 0,
                avg_accuracy    NUMERIC(5,2) NOT NULL DEFAULT 0.0,
                avg_time_ms     NUMERIC(10,2) NOT NULL DEFAULT 0.0,
                last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (student_id, topic),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );
        """)
        print("Tables created successfully.")
    finally:
        await conn.close()