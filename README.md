# EduBridge — Student Management & Hybrid Learning Platform (Classes 3–12)

EduBridge is a comprehensive hybrid ed-tech platform built according to the official project specification. It unites school students, teachers, and administrators with an integrated assignment loop, secure live classes, automatic attendance, and an advanced 4-model AI engine.

---

## 🚀 Quick Start

Run the entire platform with one command:

```bash
python run_project.py
```

- **Live Web Application (Admin & Student Portals)**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔑 Demo Login Accounts

| Role | Name | Phone Number | Password | Notes |
|---|---|---|---|---|
| **Super Admin** | Harish Kumar D | `9876543210` | `Admin@123` | Full access to classes, students, content, review queue |
| **Teacher** | Priya Sundaram | `9876543211` | `Teacher@123` | Authors material, grades submissions, starts live classes |
| **Student (Class 4)** | Kavya Ramesh | `9876543220` | `Student@123` | **Tier 1 (Classes 3–5)**: Playful UI, warm colors, large cards |
| **Student (Class 8)** | Aarav Kumar | `9876543221` | `Student@123` | **Tier 2 (Classes 6–8)**: Structured navigation, subject explorer |
| **Student (Class 10)** | Diya Sharma | `9876543222` | `Student@123` | **Tier 3 (Classes 9–12)**: Dense analytical dashboard, dark mode |

> In the web app, you can switch between these profiles with a single click using the top switcher bar!

---

## 🤖 4 Integrated AI Models

1. **AI Syllabus Doubt Solver (`POST /api/v1/ai/doubt/ask`)**
   - Answers doubts based on curriculum materials.
   - Automatically adapts tone and depth to student's grade tier (Primary, Middle, or High School).
   - Generates step-by-step logic, key takeaways, and self-check practice questions.

2. **AI Socratic Homework Tutor (`POST /api/v1/ai/homework/hint`)**
   - Analyzes student homework questions and drafts.
   - Guides students toward the answer without spoiling solutions.

3. **AI Teacher Auto-Grading Evaluator (`POST /api/v1/ai/grading/assist`)**
   - Analyzes student submissions against assignment max marks.
   - Evaluates completeness and suggests fair marks with constructive remarks.

4. **AI Chapter Quiz Generator (`POST /api/v1/ai/quiz/generate`)**
   - Generates multiple-choice revision quizzes directly from chapter topics.
   - Real-time interactive quiz experience with instant answer checking and explanations.

---

## 📁 Project Architecture

```
EduBridge/
├── backend/
│   ├── app/
│   │   ├── api/             # API routes (auth, admin, content, assignments, live, student, files, ai)
│   │   ├── models/          # SQLAlchemy ORM models (User, Class, Student, Subject, Assignment, etc.)
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Business logic, 15m signed URLs, pure bcrypt auth, AI engine
│   │   ├── config.py        # Settings & JWT configuration
│   │   ├── database.py      # SQLite / PostgreSQL database session
│   │   ├── main.py          # FastAPI application & static mount
│   │   └── seed_data.py     # Initial seed database script
│   ├── requirements.txt     # Python backend dependencies
│   └── test_backend.py      # 12-test automated backend test suite
├── frontend/
│   ├── index.html           # Modern responsive web app (Admin & Student multi-tier UI)
│   └── app.js               # Client application logic & Jitsi WebRTC integration
├── mobile_app/              # Flutter 3.x Android/iOS portable mobile client
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/         # Multi-tier student screens (Classes 3-5, 6-8, 9-12)
│   │   └── services/        # Mobile API client
│   └── pubspec.yaml
└── run_project.py           # Unified one-click runner
```

---

## 🧪 Testing Backend

Run the automated backend test suite:

```bash
cd backend
python test_backend.py
```
