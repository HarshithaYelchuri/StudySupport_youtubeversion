import streamlit as st
import os
import json
import time
import re
import pandas as pd

from google.oauth2 import service_account
from googleapiclient.discovery import build
import google.generativeai as genai
from dotenv import load_dotenv

# ============================= CONFIG =============================
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-1.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = [
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/forms.responses.readonly',
    'https://www.googleapis.com/auth/drive.file'
]

# ============================= GOOGLE AUTH =============================
def authenticate_google():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('forms', 'v1', credentials=creds)
    return service

# ============================= SAFE PARSE =============================
def safe_parse_gemini_json(response_text):
    try:
        return json.loads(response_text)
    except:
        json_text = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_text:
            return json.loads(json_text.group())
        st.error("⚠ Gemini returned invalid JSON.")
        return None

# ============================= GENERATE QUESTIONS =============================
def generate_questions(text, num_questions, q_type):
    prompt = f"""
Generate {num_questions} {q_type} questions from the following text. Output only valid JSON.

{{
  "questions": [
    {{"question": "...", "options": ["A", "B", "C", "D"], "answer": "Correct option"}}
  ]
}}

Text: {text}
"""
    response = model.generate_content(prompt)
    return safe_parse_gemini_json(response.text)

# ============================= CREATE FORM =============================
def create_form(service, form_title, questions, q_type):
    form = service.forms().create(body={"info": {"title": form_title}}).execute()
    form_id = form['formId']

    requests = [
        {
            "createItem": {
                "item": {"title": "Full Name", "questionItem": {"question": {"textQuestion": {}}}},
                "location": {"index": 0}
            }
        },
        {
            "createItem": {
                "item": {"title": "Email", "questionItem": {"question": {"textQuestion": {}}}},
                "location": {"index": 1}
            }
        }
    ]

    service.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()

    question_requests = []
    for idx, q in enumerate(questions['questions']):
        item = {
            "title": f"{idx+1}. {q['question']}",
            "questionItem": {
                "question": {
                    "choiceQuestion": {"options": [{"value": opt} for opt in q["options"]], "type": "RADIO"}
                } if q_type == "MCQ" else {"textQuestion": {}}
            }
        }
        question_requests.append({
            "createItem": {"item": item, "location": {"index": idx + 2}}
        })

    service.forms().batchUpdate(formId=form_id, body={"requests": question_requests}).execute()
    return form_id, f"https://docs.google.com/forms/d/{form_id}/viewform"
def download_responses(service, form_id, questions, q_type):
    responses = service.forms().responses().list(formId=form_id).execute()
    rows = []
    correct_answers = [q['answer'].strip().lower() for q in questions['questions']]

    for response in responses.get("responses", []):
        row = {}
        score = 0
        answers = response.get("answers", {})

        # Temporary dict to map question titles to responses
        answer_map = {}
        for qid, data in answers.items():
            val = data.get("textAnswers", {}).get("answers", [{}])[0].get("value", "").strip()
            answer_map[qid] = val

        # Get form structure to map questionId → title
        form_structure = service.forms().get(formId=form_id).execute()
        question_titles = {}
        for item in form_structure.get("items", []):
            qid = item.get("questionItem", {}).get("question", {}).get("questionId")
            title = item.get("title", "")
            if qid:
                question_titles[qid] = title

        name, email = "", ""
        q_counter = 0
        for qid, answer in answer_map.items():
            title = question_titles.get(qid, "")
            if "name" in title.lower():
                name = answer
            elif "email" in title.lower():
                email = answer
            else:
                row[f"Q{q_counter+1}"] = answer
                # Match to correct answer
                if q_counter < len(correct_answers):
                    if answer.strip().lower() == correct_answers[q_counter]:
                        score += 1
                q_counter += 1

        row["Name"] = name
        row["Email"] = email
        row["Score"] = score
        rows.append(row)

    df = pd.DataFrame(rows)

    # Reorder columns for clean CSV output
    question_cols = [col for col in df.columns if col.startswith("Q")]
    return df[["Name", "Email"] + question_cols + ["Score"]]


# ============================= MAIN PAGE =============================
def show_google_form_page(raw_text):
    st.subheader("📄 Create Google Form")
    if not raw_text:
        st.warning("Please upload a file first!")
        return

    if "form_created" not in st.session_state:
        st.session_state.form_created = False

    num_questions = st.number_input("Number of Questions", 1, 20, 5)
    form_title = st.text_input("Google Form Title", "AI Generated Form")
    q_type = st.selectbox("Question Type", ["MCQ", "Blanks", "Mixed"])
    timer_minutes = st.number_input("Form Active Duration (minutes)", 1, value=5)

    if st.button("Generate Google Form"):
        service = authenticate_google()
        questions = generate_questions(raw_text, num_questions, q_type)
        if questions is None:
            return
        form_id, form_url = create_form(service, form_title, questions, q_type)
        st.session_state.form_id = form_id
        st.session_state.form_url = form_url
        st.session_state.questions_data = questions
        st.session_state.form_start_time = time.time()
        st.session_state.form_created = True

    if st.session_state.form_created:
        st.success(f"✅ Form Created: [Open Form]({st.session_state.form_url})")

        # Grant edit access
        editor_email = st.text_input("Email to grant edit access")
        if st.button("Grant Edit Access"):
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
            drive_service = build("drive", "v3", credentials=creds)
            drive_service.permissions().create(
                fileId=st.session_state.form_id,
                body={"type": "user", "role": "writer", "emailAddress": editor_email},
                fields="id"
            ).execute()
            st.success(f"✅ Edit access granted to {editor_email}!")

        elapsed = (time.time() - st.session_state.form_start_time) / 60
        remaining = timer_minutes - elapsed
        if remaining <= 0:
            st.warning("⏰ Time is up! The form is now closed.")
        else:
            st.info(f"⏳ Remaining Time: {int(remaining)} min")

        # Download responses
        if st.button("Download Responses"):
            service = authenticate_google()
            df = download_responses(service, st.session_state.form_id, st.session_state.questions_data, q_type)
            st.dataframe(df)
            st.download_button("Download CSV", df.to_csv(index=False), "responses.csv")

    if st.button("🏠 Back to Home"):
        st.session_state.page = "upload"
        st.session_state.form_created = False
        st.rerun()
