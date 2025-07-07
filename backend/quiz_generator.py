# qa_chain.py

import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or "AIza" not in GEMINI_API_KEY:
    raise ValueError(
        "❌ GEMINI_API_KEY is missing or invalid. Make sure it's in your .env file."
    )
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_mcq_quiz(context, difficulty="basic", num_questions=5):
    """
    Generates MCQs from given context using Gemini.
    """
    prompt = f"""
You are a quiz master. Generate a {difficulty}-level MCQ quiz based on the following content.

Context:
{context}

Create {num_questions} multiple-choice questions. Each question should have 4 options (A, B, C, D), indicate the correct answer, and include a one-line explanation.

Output format:
Q1. Question text
A. Option A
B. Option B
C. Option C
D. Option D
Answer: A/B/C/D
Explanation: One-line explanation
"""
    response = model.generate_content(prompt)
    return response.text.strip()

def parse_mcq_output(quiz_text):
    """
    Parses Gemini-generated quiz text into structured question dictionaries.
    Returns a list of questions with text, options, answer, and explanation.
    """
    questions = []

    # Split on lines starting with Q + number + dot (e.g. Q1.)
    blocks = re.split(r"\nQ\d+\.", "\n" + quiz_text.strip())
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.splitlines()
        if len(lines) < 5:
            # Not enough lines to parse a question
            continue

        q_line = lines[0].strip()

        # Parse options safely
        options = {}
        for line in lines[1:5]:
            match = re.match(r"([A-D])\.\s*(.*)", line.strip())
            if match:
                options[match.group(1)] = match.group(2).strip()

        # Find answer and explanation
        answer_match = re.search(r"Answer:\s*([A-D])", block)
        explanation_match = re.search(r"Explanation:\s*(.*)", block)

        if answer_match and explanation_match and options:
            question_data = {
                "question": q_line,
                "options": options,
                "answer": answer_match.group(1).strip(),
                "explanation": explanation_match.group(1).strip()
            }
            questions.append(question_data)

    return questions
