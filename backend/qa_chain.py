import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_question(context, question):
    prompt = f"""
You are a helpful assistant. Use the context to answer the question.

Context:
{context}

Question:
{question}
"""
    response = model.generate_content(prompt)
    return response.text.strip()
