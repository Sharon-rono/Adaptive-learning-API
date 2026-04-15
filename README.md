# Adaptive Learning API

An AI-powered backend system that adapts to each student's learning needs. 
When a student answers a question, the system checks their answer, generates 
personalised AI feedback using Groq, saves everything to a cloud PostgreSQL 
database, and tracks their performance over time.

## Tech Stack

| Layer | Tool |
|-------|------|
| Backend | FastAPI |
| AI | Groq (LLaMA3) |
| Database | Aiven PostgreSQL |
| Driver | asyncpg |
| Server | Uvicorn |

## Features

- Register students and track when they joined
- Submit quiz answers and receive instant AI-generated feedback
- Different feedback for correct vs incorrect answers
- Generate quiz questions on any topic at any difficulty level
- Track student performance history per topic
- Analytics endpoints for teachers to identify struggling students
- Find the hardest topics across all students

## Project Structure  
adaptive-learning/
├── main.py          # FastAPI app, all endpoints  
├── database.py      # PostgreSQL connection and table creation  
├── models.py        # Pydantic request models  
├── ai.py            # Groq AI feedback and question generation  
├── analytics.py     # SQL analytics queries  
└── requirements.txt # Project dependencies

