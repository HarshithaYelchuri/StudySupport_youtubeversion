# 📚 StudySupport: Smart PDF Assistant with Q\&A, Quizzes, Google Forms, and YouTube Recommendations

**StudySupport** is a Streamlit-based educational tool that transforms any uploaded PDF, DOCX, or TXT file into an interactive learning environment. The app offers AI-powered features like:

* 💬 Document Q\&A
* 📝 Quiz Generation
* 📄 Google Form Creation
* ▶️ YouTube Video Recommendations
* 📥 Response Collection & Analysis

---

## 🚀 Features

### 1. **Upload and Analyze Documents**

Upload `.pdf`, `.docx`, or `.txt` files. The app reads and extracts content for further use.

---

### 2. **Ask Questions from Document**

Chat with your uploaded document using an AI model (Gemini 1.5 Flash) that answers based on the content.

---

### 3. **Auto-Generate Quizzes**

Create multiple-choice quizzes from document content:

* Choose difficulty: Easy, Medium, Challenging
* Customize number of questions
* Get real-time answer feedback
* Export quiz results as a PDF

---

### 4. **Generate Google Forms**

Create an auto-filled Google Form:

* Choose question type (MCQ, Fill in the Blanks, Mixed)
* Control number of questions and form duration
* Share form link
* Grant edit access to others
* Download form responses as CSV

---

### 5. **YouTube Video Recommendations**

Get curated YouTube video recommendations **based on your document topic**:

* AI-powered search and ranking
* Ranked by views, likes, and channel subscribers


---

## 🧠 Tech Stack

| Component            | Tech Used                            |
| -------------------- | ------------------------------------ |
| Frontend             | Streamlit                            |
| Embeddings & Vector  | FAISS + GoogleGenerativeAIEmbeddings |
| LLM for QA & Quiz    | Gemini 1.5 Flash                     |
| Document Parsing     | PyPDF2, docx2txt                     |
| YouTube Integration  | Google API (YouTube Data v3)         |
| Google Forms API     | Google API + OAuth2                  |
| Environment Handling | `python-dotenv`                      |

---

## 🗂 Folder Structure

```
📁 StudySupport/
│
├── app.py                  # Main Streamlit app
├── .env                    # API keys and config (not shared)
├── data/
│   ├── uploads/            # Uploaded documents
│   ├── db/                 # FAISS vector database
│   └── logo.png            # App logo (optional)
│
├── backend/
│   ├── pdf_loader.py       # Loads and parses PDF/DOCX/TXT
│   ├── vector_store.py     # Embedding + FAISS DB
│   ├── qa_chain.py         # Gemini-based Q&A
│   ├── quiz_generator.py   # Quiz generation + parsing
│   └── youtube_recommender.py # YouTube search & ranking
│
├── google_forms.py         # Google Form generation and results
└── requirements.txt        # Required Python packages
```

---

## 🛠️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/studysupport.git
cd studysupport
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Environment Setup

Create a `.env` file in the root folder with:

```env
GEMINI_API_KEY=your_google_gemini_api_key
YOUTUBE_API_KEY=your_youtube_data_api_key
```

Place your Google Cloud `service_account.json` file in the root directory.

---

### 4. Run the App

```bash
streamlit run app.py
```

---

## ✅ Requirements

```txt
streamlit
PyPDF2
docx2txt
google-generativeai
langchain
langchain-google-genai
python-dotenv
reportlab
pandas
google-api-python-client
```

You can generate this with:

```bash
pip freeze > requirements.txt
```

---

## 🔐 Authentication

To enable Google Form integration:

1. Create a project in Google Cloud Console
2. Enable **Google Forms API** and **Google Drive API**
3. Generate and download a service account key JSON file
4. Share your form with the service account email to allow form creation

For YouTube Recommendations:

1. Enable **YouTube Data API v3** in Google Cloud Console
2. Create an API key and add it to your `.env` file

---

## 📸 Screenshots (Optional)

You may want to add:

* Upload and preview page
* Chat Q\&A interface
* Quiz view with feedback
* Generated Google Form URL + responses
* YouTube recommendations with filtering

---

## 🧑‍💻 Developer Notes

* Model used: `gemini-1.5-flash`
* Text is chunked (1000 characters with 100 overlap) before embedding
* Uses LangChain FAISS store for semantic search
* Chat history is maintained per session
* Google Form access and CSV download available post-creation
* YouTube recommendations ranked by views, likes, and channel subscribers, with filtering support

---

## ✨ Future Enhancements

* Support for image-based PDFs
* Richer quiz formats (matching, drag & drop)
* Login and document history
* Multi-user database support
* Advanced YouTube filtering (date, duration, region)

---

## 📜 License

MIT License (add a proper `LICENSE` file if needed)

---

