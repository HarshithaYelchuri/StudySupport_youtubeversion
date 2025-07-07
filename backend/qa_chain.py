import google.generativeai as genai
import os
from dotenv import load_dotenv
import whisper

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Load Whisper model once
whisper_model = whisper.load_model("base")

def transcribe_audio(audio_file_path: str) -> str:
    """Convert audio file to text using Whisper."""
    result = whisper_model.transcribe(audio_file_path)
    return result["text"].strip()

def ask_question(context, question_or_audio):
    """
    Accepts either:
      - question_or_audio as text string (typed question)
      - or path to audio file (wav, mp3)
    If audio file, transcribes to text first.
    """
    if isinstance(question_or_audio, str) and question_or_audio.endswith((".wav", ".mp3", ".m4a")):
        question = transcribe_audio(question_or_audio)
    else:
        question = question_or_audio  # text input

    prompt = f"""
You are a helpful assistant. Use the context to answer the question.

Context:
{context}

Question:
{question}
"""
    response = model.generate_content(prompt)
    return response.text.strip()
