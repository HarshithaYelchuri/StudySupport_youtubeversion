import streamlit as st
import os
from PIL import Image
from reportlab.pdfgen import canvas

from backend.pdf_loader import load_pdf_text
from backend.vector_store import create_vector_store, load_vector_store
from backend.qa_chain import ask_question
from backend.quiz_generator import generate_mcq_quiz, parse_mcq_output
import google_forms
from backend.youtube_recommender import recommend_videos

DB_PATH = "data/db"
UPLOAD_FOLDER = "data/uploads"
LOGO_PATH = "data/logo.png"

# ——— Header ———
def show_header():
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH)
        col1, col2 = st.columns([1, 6])
        with col1:
            st.image(logo, width=70)
        with col2:
            st.markdown("<h1 style='padding-top:15px; font-size:40px;'>StudySupport</h1>", unsafe_allow_html=True)
    else:
        st.title("StudySupport")

show_header()

# ——— Session State ———
if "page" not in st.session_state:
    st.session_state.page = "upload"
if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None
if "raw_text" not in st.session_state:
    st.session_state.raw_text = None
if "quiz_state" not in st.session_state:
    st.session_state.quiz_state = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ——— Page Router ———
def show_page():
    if st.session_state.page == "upload":
        show_upload_page()
    elif st.session_state.page == "ask":
        show_ask_page()
    elif st.session_state.page == "quiz":
        show_quiz_page()
    elif st.session_state.page == "google_form":
        google_forms.show_google_form_page(st.session_state.raw_text)
    elif st.session_state.page == "youtube_videos":
        show_youtube_videos_page()

# ——— Upload Page ———
def show_upload_page():
    st.subheader("📤 Upload your PDF, DOCX, or TXT")

    if st.session_state.raw_text:
        st.success(f"✅ You already uploaded: {os.path.basename(st.session_state.pdf_path)}")

        st.write("### What do you want to do next?")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("💬 Ask a Question"):
                st.session_state.page = "ask"
                st.rerun()
        with c2:
            if st.button("📝 Generate Quiz"):
                st.session_state.page = "quiz"
                st.rerun()
        with c3:
            if st.button("📄 Create Google Form"):
                st.session_state.page = "google_form"
                st.rerun()
        with c4:
            if st.button("▶️ YouTube Videos"):
                st.session_state.page = "youtube_videos"
                st.rerun()
    else:
        uploaded_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt"])
        if uploaded_file:
            uploaded_file.seek(0)
            raw_text = load_pdf_text(uploaded_file)

            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            st.session_state.pdf_path = file_path
            st.session_state.raw_text = raw_text

            create_vector_store(raw_text, DB_PATH)
            st.success("✅ File processed successfully!")
            st.rerun()

# ——— Ask Page ———
def show_ask_page():
    st.subheader("💬 Ask your Document")
    if not st.session_state.raw_text:
        st.warning("Please upload and process a file first.")
        return

    for q, a in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            st.write(a)

    question = st.chat_input("Type your question here")
    if question:
        db = load_vector_store(DB_PATH)
        docs = db.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        answer = ask_question(context, question)
        st.session_state.chat_history.append((question, answer))
        st.rerun()

    st.write("---")
    if st.button("🏠 Back to Home"):
        st.session_state.page = "upload"
        st.rerun()

# ——— Quiz Page ———
def show_quiz_page():
    st.subheader("📝 Generate a Quiz")
    if not st.session_state.raw_text:
        st.warning("Please upload and process a file first.")
        return

    diff_map = {"Easy": "basic", "Medium": "advanced", "Challenging": "hard"}
    ui_diff = st.selectbox("Select Difficulty", list(diff_map.keys()))
    difficulty = diff_map[ui_diff]
    num_q = st.number_input("Number of Questions", 1, 20, 5)
    if st.button("Generate Quiz"):
        db = load_vector_store(DB_PATH)
        docs = db.similarity_search("generate quiz", k=5)
        ctx = "\n\n".join([d.page_content for d in docs])
        quiz_text = generate_mcq_quiz(ctx, difficulty=difficulty, num_questions=num_q)
        st.session_state.quiz_state = {
            "questions": parse_mcq_output(quiz_text),
            "submitted": [False]*num_q,
            "feedback": [""]*num_q,
            "score": 0
        }
        st.rerun()
    if "questions" in st.session_state.quiz_state:
        render_quiz()

    st.write("---")
    if st.button("🏠 Back to Home"):
        st.session_state.page = "upload"
        st.rerun()

def render_quiz():
    quiz_state = st.session_state.quiz_state
    st.markdown("### 🎯 Quiz")

    for idx, q in enumerate(quiz_state["questions"]):
        st.markdown(f"**Q{idx + 1}. {q['question']}**")

        options_list = list(q["options"].items())
        selected = st.radio(
            "Options:",
            options_list,
            format_func=lambda x: f"{x[0]}. {x[1]}",
            index=None,
            key=f"radio_{idx}"
        )

        if not quiz_state["submitted"][idx]:
            if st.button("Submit", key=f"submit_{idx}"):
                quiz_state["submitted"][idx] = True
                if selected and selected[0] == q["answer"]:
                    quiz_state["score"] += 1
                    quiz_state["feedback"][idx] = f"✅ Correct! {q['explanation']}"
                else:
                    quiz_state["feedback"][idx] = f"❌ Incorrect. Correct answer: {q['answer']}. {q['explanation']}"
                st.rerun()

        if quiz_state["submitted"][idx]:
            if "✅" in quiz_state["feedback"][idx]:
                st.success(quiz_state["feedback"][idx])
            else:
                st.error(quiz_state["feedback"][idx])

        st.write("---")

    if all(quiz_state["submitted"]):
        st.markdown(f"### Final Score: `{quiz_state['score']}/{len(quiz_state['questions'])}`")
        export_quiz_to_pdf()

def export_quiz_to_pdf():
    quiz_state = st.session_state.quiz_state
    export_path = "data/quiz_output.pdf"
    c = canvas.Canvas(export_path)
    c.setFont("Helvetica", 12)
    y = 800

    if os.path.exists(LOGO_PATH):
        c.drawInlineImage(LOGO_PATH, 40, y, width=100, preserveAspectRatio=True)
        y -= 100

    for idx, q in enumerate(quiz_state["questions"]):
        c.drawString(40, y, f"Q{idx + 1}: {q['question']}")
        y -= 20
        for opt_key, opt_val in q["options"].items():
            c.drawString(60, y, f"{opt_key}. {opt_val}")
            y -= 20
        feedback = quiz_state["feedback"][idx].replace("✅ ", "").replace("❌ ", "")
        c.drawString(60, y, feedback)
        y -= 40
        if y < 100:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 800

    c.save()
    with open(export_path, "rb") as f:
        st.download_button("⬇️ Download Quiz PDF", f, file_name="quiz.pdf")

# ——— YouTube Videos Page ———
def show_youtube_videos_page():
    st.subheader("▶️ YouTube Recommendations")
    if not st.session_state.raw_text:
        st.warning("Please upload and process a file first.")
        return

    st.write("🔎 Searching YouTube for videos related to your document...")

    with st.spinner("Fetching videos..."):
        videos = recommend_videos(st.session_state.raw_text)

    if videos:
        for vid in videos:
            st.markdown(f"**{vid['title']}**")
            st.video(vid['url'])
            st.write("---")
    else:
        st.error("❌ No videos found.")

    if st.button("🏠 Back to Home"):
        st.session_state.page = "upload"
        st.rerun()

# ——— Run App ———
show_page()
