import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_feedback(topic: str, question: str, answer_given: str, correct_answer: str, is_correct: bool) -> str:
    if is_correct:
        prompt = f"""
        A student correctly answered a question on the topic: {topic}.
        Question: {question}
        Their answer: {answer_given}

        Give them a short, encouraging response (2-3 sentences). 
        Acknowledge what they got right, and add one interesting fact 
        or a slightly harder follow-up thought to keep them challenged.
        """
    else:
        prompt = f"""
        A student got a question wrong. Your job is to help them understand, not just tell them they failed.

        Topic: {topic}
        Question: {question}
        Student's answer: {answer_given}
        Correct answer: {correct_answer}

        Do three things:
        1. Gently explain why their answer was incorrect.
        2. Clearly explain the correct answer with a simple example.
        3. End with one short tip to remember this concept next time.

        Keep the tone warm and encouraging. Max 5 sentences.
        """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def generate_question(topic: str, difficulty: str) -> str:
    prompt = f"""
    Generate a quiz question about: {topic}
    Difficulty level: {difficulty}

    Respond in this exact format:
    Question: <your question here>
    A) <option>
    B) <option>
    C) <option>
    D) <option>
    Correct Answer: <letter>

    Do not add anything else before or after.
    """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content