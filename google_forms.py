import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from gemini_integration import generate_quiz_questions

SCOPES = ["https://www.googleapis.com/auth/forms.body", "https://www.googleapis.com/auth/forms.responses.readonly"]

def authenticate_google():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return build("forms", "v1", credentials=creds)

def create_form(service, title, questions):
    form = {
        "info": {
            "title": title
        }
    }

    result = service.forms().create(body=form).execute()
    form_id = result["formId"]

    requests = []
    for q in questions:
        question_item = {
            "createItem": {
                "item": {
                    "title": q["question"],
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [{"value": option} for option in q["options"]],
                                "shuffle": False,
                            }
                        }
                    }
                },
                "location": {"index": 0}
            }
        }
        requests.append(question_item)

    service.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()
    return f"https://docs.google.com/forms/d/{form_id}/edit"

def show_google_form_page(text):
    st.subheader("📄 Generate Google Form Quiz")
    title = st.text_input("Form Title", "AI Quiz")

    num_questions = st.slider("Number of Questions", 1, 10, 5)
    difficulty = st.selectbox("Difficulty", ["basic", "advanced", "hard"])

    if st.button("Generate Google Form"):
        with st.spinner("Generating quiz and creating form..."):
            try:
                questions = generate_quiz_questions(text, num_questions, difficulty)
                service = authenticate_google()
                form_url = create_form(service, title, questions)
                st.success("✅ Form created successfully!")
                st.markdown(f"[Open Google Form]({form_url})")
            except Exception as e:
                st.error(f"Failed to create form: {e}")
