import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def evaluate_answer(question, answer_key, student_answer):
    prompt = f"""
You are an experienced university examiner.

Question:
{question}

Correct Answer:
{answer_key}

Student Answer:
{student_answer}

Evaluate the student's answer.

Return ONLY in this format:

Marks: X/10
Feedback:
- Strengths
- Mistakes
- Suggestions
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    return response.text