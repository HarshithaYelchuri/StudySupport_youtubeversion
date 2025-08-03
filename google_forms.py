import streamlit as st
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ✅ Gemini integration instead of OpenAI
from gemini_integration import generate_quiz_questions

SCOPES = ['https://www.googleapis.com/auth/forms.body', 'https://www.googleapis.com/auth/forms.responses.readonly']
SERVICE_ACCOUNT_FILE = "credentials.json"

def authenticate_google():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('forms', 'v1', credentials=creds)
    return service

def create_form(service, title, description):
    NEW_FORM = {
        "info": {
            "title": title,
            "description": description
        }
    }

    try:
        form = service.forms().create(body=NEW_FORM).execute()
        return form["formId"]
    except HttpError as error:
        st.error(f"An error occurred while creating the form: {error}")
        return None

def add_questions_to_form(service, form_id, questions):
    requests_batch = []

    for q in questions:
        req = {
            "createItem": {
                "item": {
                    "title": q["question"],
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [{"value": opt} for opt in q["options"]],
                                "shuffle": True
                            }
                        }
                    }
                },
                "location": {"index": 0}
            }
        }
        requests_batch.append(req)

    batch_update_request = {"requests": requests_batch}

    try:
        service.forms().batchUpdate(formId=form_id, body=batch_update_request).execute()
    except HttpError as error:
        st.error(f"An error occurred while adding questions: {error}")

def get_form_url(form_id):
    return f"https://docs.google.com/forms/d/{form_id}/edit"

def show_google_form_page(text):
    st.markdown("## 📄 Generate Google Form Quiz")

    col1, col2 = st.columns(2)
    with col1:
        difficulty = st.selectbox("Select Difficulty", ["Basic", "Advanced", "Hard"])
    with col2:
        num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)

    if st.button("🚀 Generate Google Form"):
        with st.spinner("Generating quiz and creating form..."):
            try:
                service = authenticate_google()
                questions = generate_quiz_questions(text, num_questions, difficulty)

                form_title = f"{difficulty} Quiz"
                form_description = f"A quiz on the given topic at {difficulty} level."

                form_id = create_form(service, form_title, form_description)
                if form_id:
                    add_questions_to_form(service, form_id, questions)
                    form_url = get_form_url(form_id)

                    st.success("✅ Google Form created successfully!")
                    st.markdown(f"[📝 Click here to view your Google Form]({form_url})", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Something went wrong: {e}")
