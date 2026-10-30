# CareerPilot AI 🤖

**An AI-powered career assistant that helps entry-level technology job seekers with career guidance, technical learning, resume improvement, interview preparation, and general questions.**

## 🚀 Project Overview

CareerPilot AI is an interactive AI chatbot built using Python, FastAPI, Streamlit, SQLite, and Groq.

It supports both general-purpose questions and career-related assistance. Users can ask technical questions, get resume suggestions, explore job requirements, and prepare for interviews through a conversational interface.

The application also maintains multiple conversations and stores chat history locally using SQLite.

## ✨ Key Features

- **General Q&A:** Ask questions about technology and other topics.
- **Career Guidance:** Get practical job-search and career advice.
- **Resume Assistance:** Receive suggestions to improve resume content.
- **Job Description Analysis:** Understand job requirements and identify skill gaps.
- **Interview Preparation:** Practice technical and HR interview questions.
- **Multiple Conversations:** Create and switch between different chats.
- **Persistent Chat History:** Store and retrieve conversations using SQLite.
- **Input Validation:** Validate requests using Pydantic.
- **Error Handling:** Handle API failures, connection issues, and invalid requests.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend API development |
| Streamlit | Interactive frontend |
| Groq API | Large Language Model integration |
| SQLite | Conversation and message storage |
| Pydantic | Request validation |
| Requests | Frontend-backend communication |
| Uvicorn | ASGI application server |
| Python-dotenv | Environment variable management |

## 🏗️ Project Architecture

```text
              User
               |
               v
       Streamlit Frontend
               |
          HTTP Requests
               |
               v
        FastAPI Backend
               |
        +------+------+
        |             |
        v             v
     Groq API      SQLite DB
        |             |
        v             v
     AI Reply     Chat History
        |             |
        +------+------+
               |
               v
       Streamlit Frontend
               |
               v
          AI Response
```

## 📂 Project Structure

```text
CareerPilot-AI/
│
├── main.py             # FastAPI backend
├── app.py              # Streamlit frontend
├── requirements.txt    # Project dependencies
├── .gitignore          # Excluded files and secrets
├── README.md           # Project documentation
│
└── careerpilot.db      # Local database (generated at runtime)
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Sanjureddy-17/CareerPilot-AI.git
cd CareerPilot-AI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Get an API key from [Groq Console](https://console.groq.com/).

**Important:** Never commit your `.env` file or expose your API key publicly.

### 5. Start the FastAPI backend

Open the first terminal:

```bash
uvicorn main:app --reload
```

Backend URL:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### 6. Start the Streamlit frontend

Open a second terminal:

```bash
streamlit run app.py
```

Open the application:

`http://localhost:8501`

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check backend status |
| POST | `/conversations` | Create a conversation |
| GET | `/conversations` | Retrieve conversations |
| GET | `/history` | Retrieve conversation messages |
| POST | `/chat` | Send a message and receive an AI response |

## 📸 Application Screenshots

### 1. CareerPilot AI Chat Interface

![CareerPilot AI Chat](screenshots/chatbot.png)

### 2. Conversation History

![Conversation History](screenshots/conversation-history.png)

### 3. FastAPI Backend Documentation

![FastAPI Documentation](screenshots/api-docs.png)

## 🧠 What I Learned

Through this project, I gained practical experience in:

- Integrating Large Language Models through an API.
- Building RESTful APIs using FastAPI.
- Connecting frontend applications with backend services.
- Managing conversational data using SQLite.
- Implementing request validation with Pydantic.
- Handling API exceptions and network errors.
- Managing environment variables and API credentials.
- Using Git and GitHub for version control.

## 🔮 Future Improvements

- Implement Retrieval-Augmented Generation (RAG) for personalized career resources.
- Add user authentication and account management.
- Integrate job-search APIs for relevant job opportunities.
- Introduce resume parsing and automated skill-gap analysis.
- Deploy the application to a cloud platform.

## 👨‍💻 Developer

**Muvva Sanjeeva Reddy**

Computer Science Graduate | Python | FastAPI | SQL | Data Science | Generative AI

- GitHub: [Sanjureddy-17](https://github.com/Sanjureddy-17)
- Project Repository: [CareerPilot AI](https://github.com/Sanjureddy-17/CareerPilot-AI)

---

*Built as a hands-on project to explore LLM integration, backend development, and practical AI application engineering.*
