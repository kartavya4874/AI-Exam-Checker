# 🚀 Quick Start Guide - Exam Checker System

## Prerequisites

- Python 3.11+
- Redis (for Celery)
- PostgreSQL (optional, SQLite works for development)
- Git

## Installation

### Option 1: Local Development (Recommended for Testing)

#### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd c:\Users\karta\Exam_Checker

# Create virtual environment for backend
cd backend
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Configure Environment

```bash
# Copy environment template
cd ..
copy .env.example .env

# Edit .env file and add your API keys
notepad .env
```

**Minimum required in `.env`:**
```env
# Database (SQLite for development)
DATABASE_URL=sqlite:///./exam_checker.db

# Gemini API (get free key from https://aistudio.google.com)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional OCR APIs (system has mock fallbacks)
GOOGLE_CLOUD_VISION_API_KEY=
MATHPIX_APP_ID=
MATHPIX_APP_KEY=
```

#### Step 3: Start Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will start at:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

#### Step 4: Start Frontend (New Terminal)

```bash
cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

streamlit run Home.py
```

**Frontend will start at:** http://localhost:8501

#### Step 5: Start Celery Worker (Optional - for parallel processing)

**Terminal 3:**
```bash
cd backend
venv\Scripts\activate

# Start Redis first (download from https://redis.io/download)
# Or use Docker: docker run -d -p 6379:6379 redis

# Start Celery worker
celery -A celery_worker.celery_app worker --loglevel=info --concurrency=4
```

**Terminal 4 (Optional - Celery monitoring):**
```bash
cd backend
celery -A celery_worker.celery_app flower
```
**Flower dashboard:** http://localhost:5555

---

### Option 2: Docker (Production-Ready)

```bash
# Make sure Docker Desktop is running

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services will be available at:**
- Frontend: http://localhost:8501
- Backend: http://localhost:8000
- Flower: http://localhost:5555

---

## First-Time Setup

### 1. Initialize Database

The database will be created automatically when you start the backend. Tables are created on first run.

### 2. Test the System

**Check Backend Health:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "gemini_api": "configured",
  "ocr_api": "not configured"
}
```

**Access Frontend:**
Open http://localhost:8501 in your browser

---

## Basic Workflow

### Setup Phase (One-time per exam)

#### 1. Upload Question Paper

```python
# Example using Python
from app.services.preprocessor.pdf_processor import DocumentPreprocessor
from app.services.ocr.ocr_engine import create_ocr_engine
from app.services.processors.question_paper_processor import process_question_paper

# Initialize services
preprocessor = DocumentPreprocessor(dpi=300)
ocr_engine = create_ocr_engine(gemini_api_key="your_key")

# Process PDF
images = preprocessor.pdf_to_images("question_paper.pdf")
processed_images = preprocessor.preprocess_document("question_paper.pdf")

# Extract questions
questions = process_question_paper(
    images=[img[0] for img in processed_images],
    question_paper_id=1,
    ocr_engine=ocr_engine
)

print(f"Extracted {len(questions)} questions")
```

#### 2. Upload Answer Key

```python
from app.services.processors.answer_key_processor import process_answer_key
from app.services.evaluators.ai_client import create_ai_evaluator

ai_evaluator = create_ai_evaluator(gemini_api_key="your_key")

model_answers = process_answer_key(
    images=[img[0] for img in processed_images],
    questions=questions,
    answer_key_id=1,
    ocr_engine=ocr_engine,
    ai_evaluator=ai_evaluator
)

print(f"Extracted {len(model_answers)} model answers")
```

### Evaluation Phase

#### 3. Process Student Answer Sheets

```python
from app.services.processors.student_answer_processor import process_student_sheet

# Process one student
result = process_student_sheet(
    images=[img[0] for img in student_images],
    questions=questions,
    student_exam_id=1,
    ocr_engine=ocr_engine,
    preprocessor=preprocessor
)

print(f"Student: {result['header_info']['name']}")
print(f"Attempted: {result['attempted_questions']}/{result['total_questions']}")
```

#### 4. Evaluate Answers

```python
from app.services.evaluators.text_evaluator import evaluate_text
from app.services.evaluators.math_evaluator import evaluate_math
from app.services.evaluators.code_evaluator import evaluate_code

# Evaluate based on question type
for answer in result['answers']:
    if answer['is_attempted']:
        question = next(q for q in questions if q['id'] == answer['question_id'])
        
        if question['question_type'] == 'text':
            eval_result = evaluate_text(
                student_answer=answer['answer_text'],
                model_answer=model_answers[0]['text'],
                keywords=model_answers[0]['keywords'],
                max_marks=question['max_marks'],
                ai_evaluator=ai_evaluator
            )
        elif question['question_type'] == 'math':
            eval_result = evaluate_math(
                student_answer=answer['answer_text'],
                model_answer=model_answers[0]['text'],
                max_marks=question['max_marks'],
                ai_evaluator=ai_evaluator
            )
        # ... etc for other types
        
        print(f"Q{question['number']}: {eval_result['marks_awarded']}/{question['max_marks']}")
```

#### 5. Generate Feedback

```python
from app.services.processors.model_training import FeedbackGenerator

generator = FeedbackGenerator()

feedback = generator.generate_answer_feedback(
    question=question,
    student_answer=answer,
    evaluation_result=eval_result
)

print(f"Feedback: {feedback['detailed_feedback']}")
print(f"Strengths: {feedback['strengths']}")
print(f"Improvements: {feedback['improvements']}")
```

### Parallel Processing

#### 6. Evaluate Multiple Courses

```python
from app.services.batch.parallel_processor import evaluate_courses_parallel

courses = [
    {"course_code": "CS101"},
    {"course_code": "CS102"},
    {"course_code": "MATH201"},
]

def process_course(course):
    # Your course processing logic
    return {"status": "completed"}

results = evaluate_courses_parallel(
    courses=courses,
    evaluation_function=process_course,
    max_workers=4
)

print(f"Processed {results['successful']}/{results['total_courses']} courses")
print(f"Time: {results['elapsed_time']}s")
```

---

## Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <process_id> /F

# Or use different port
uvicorn app.main:app --port 8001
```

### Frontend won't start

```bash
# Check if port 8501 is in use
netstat -ano | findstr :8501

# Use different port
streamlit run Home.py --server.port 8502
```

### Database errors

```bash
# Delete and recreate database
rm exam_checker.db

# Restart backend (will recreate tables)
uvicorn app.main:app --reload
```

### Celery worker not starting

```bash
# Make sure Redis is running
redis-cli ping
# Should return: PONG

# If Redis not installed, use Docker
docker run -d -p 6379:6379 redis
```

### API key errors

```bash
# Check if API key is set
echo %GEMINI_API_KEY%  # Windows
echo $GEMINI_API_KEY   # Linux/Mac

# If not set, add to .env file
# System will use mock responses if API keys not configured
```

---

## Development Tips

### Hot Reload

Both backend and frontend support hot reload:
- **Backend**: Changes auto-reload with `--reload` flag
- **Frontend**: Streamlit auto-detects changes

### Viewing Logs

```bash
# Backend logs (in terminal)
# Frontend logs (in terminal)

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker
```

### Database Inspection

```bash
# SQLite
sqlite3 exam_checker.db
.tables
.schema student_answers
SELECT * FROM courses;

# PostgreSQL
psql -U examchecker -d exam_checker
\dt
\d student_answers
SELECT * FROM courses;
```

---

## Next Steps

1. **Test with sample PDFs** - Try processing a simple question paper
2. **Review API docs** - Visit http://localhost:8000/docs
3. **Explore frontend** - Navigate through http://localhost:8501
4. **Check parallel processing** - Run example from `backend/app/services/batch/examples.py`

---

## Getting Help

- **API Documentation**: http://localhost:8000/docs
- **Celery Monitoring**: http://localhost:5555
- **Check logs** in terminal windows
- **Review** [README.md](file:///c:/Users/karta/Exam_Checker/README.md) for detailed info

---

**System is ready to use!** 🚀
