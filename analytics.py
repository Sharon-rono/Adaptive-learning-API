from database import get_connection

# Find students whose average score falls below a given threshold
async def get_struggling_students(threshold: float):
    conn = await get_connection()
    try:
        rows = await conn.fetch("""
            SELECT s.student_id, s.name, s.email,
                   ROUND(AVG(CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END) * 100, 2) AS avg_score
            FROM students s
            JOIN quiz_results qr ON s.student_id = qr.student_id
            GROUP BY s.student_id, s.name, s.email
            HAVING AVG(CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END) * 100 < $1
            ORDER BY avg_score ASC;
        """, threshold)
        return [dict(r) for r in rows]
    finally:
        await conn.close()

# Find the topic with the lowest average score across all students
async def get_hardest_topic():
    conn = await get_connection()
    try:
        rows = await conn.fetch("""
            SELECT topic,
                   ROUND(AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) * 100, 2) AS avg_score,
                   COUNT(*) AS total_attempts
            FROM quiz_results
            GROUP BY topic
            ORDER BY avg_score ASC
            LIMIT 5;
        """)
        return [dict(r) for r in rows]
    finally:
        await conn.close()

# Individual student report broken down by topic
async def get_student_report(student_id: int):
    conn = await get_connection()
    try:
        rows = await conn.fetch("""
            SELECT topic,
                   COUNT(*) AS total_questions,
                   SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) AS correct_count,
                   ROUND(AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) * 100, 2) AS avg_accuracy,
                   ROUND(AVG(time_taken_ms), 2) AS avg_time_ms
            FROM quiz_results
            WHERE student_id = $1
            GROUP BY topic
            ORDER BY avg_accuracy ASC;
        """, student_id)
        return [dict(r) for r in rows]
    finally:
        await conn.close()