import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

def authenticate_google():
    SCOPES = [
        "https://www.googleapis.com/auth/forms.body",
        "https://www.googleapis.com/auth/forms.responses.readonly"
    ]
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=SCOPES
    )
    return creds


def create_google_form(service, quiz_title, questions):
    form = {
        "info": {
            "title": quiz_title,
            "documentTitle": quiz_title
        },
        "items": []
    }

    for i, q in enumerate(questions):
        item = {
            "title": f"Question {i + 1}",
            "questionItem": {
                "question": {
                    "required": True,
                    "question": q["question"],
                    "choiceQuestion": {
                        "type": "RADIO",
                        "options": [{"value": option} for option in q["options"]],
                        "shuffle": False
                    }
                }
            }
        }
        form["items"].append(item)

    try:
        created_form = service.forms().create(body=form).execute()
        return created_form["formId"], f"https://docs.google.com/forms/d/{created_form['formId']}/edit"
    except HttpError as error:
        st.error(f"An error occurred: {error}")
        return None, None


def show_google_form_page(raw_text):
    st.subheader("📋 Generate Google Form Quiz")

    title = st.text_input("Enter Quiz Title", "StudySupport Quiz")

    num_questions = st.slider("How many questions do you want to generate?", 1, 10, 3)

    if st.button("Generate Google Form"):
        with st.spinner("Generating questions and creating Google Form..."):
            from openai_integration import generate_quiz_questions

            questions = generate_quiz_questions(raw_text, num_questions)

            service = build('forms', 'v1', credentials=authenticate_google())

            form_id, form_url = create_google_form(service, title, questions)

            if form_url:
                st.success("Form Created Successfully!")
                st.markdown(f"[Click here to open the form]({form_url})", unsafe_allow_html=True)
