# 🎓 Complete Exam Checker System

Universal automated exam evaluation system for universities covering ALL exam types: theory, math, coding, diagrams, and MCQs across all departments.

## 🌟 Features

- ✅ **Multi-format OCR**: Handwriting, math equations, code blocks
- ✅ **AI-powered evaluation**: Using Gemini API (production: Claude)
- ✅ **Smart question mapping**: Handles out-of-order answers
- ✅ **Content-aware grading**: Different strategies for text, math, code, diagrams, MCQs
- ✅ **Partial credit**: Step-wise marks for math, logic-based for code
- ✅ **Faculty review interface**: Override any marks, add comments, approve results
- ✅ **Batch processing**: Scalable for university-wide deployment
- ✅ **Export results**: Excel and PDF reports

## 🏗️ Architecture

```
Backend: FastAPI + PostgreSQL + Celery + Redis
Frontend: Streamlit
OCR: Google Cloud Vision + Mathpix
AI: Gemini API (dev) → Claude API (production)
```

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- API Keys:
  - Google Cloud Vision API (handwriting OCR)
  - Mathpix API (math OCR)
  - Gemini API (AI evaluation)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone and navigate to project
cd Exam_Checker

# 2. Copy environment file and add your API keys
cp .env.example .env
# Edit .env and add your API keys

# 3. Start all services
docker-compose up -d

# 4. Access the applications
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# 1. Set up backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 2. Set up environment
cp ..\.env.example .env
# Edit .env and add your API keys

# 3. Run backend
uvicorn app.main:app --reload

# 4. In a new terminal, set up frontend
cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 5. Run frontend
streamlit run Home.py
```

## 📁 Project Structure

```
Exam_Checker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database connection
│   │   ├── models/              # SQLAlchemy models
│   │   ├── services/            # Business logic
│   │   │   ├── ocr/             # OCR services
│   │   │   ├── preprocessor/    # Document preprocessing
│   │   │   ├── processors/      # Question/Answer processors
│   │   │   ├── evaluators/      # Evaluation engines
│   │   │   └── batch/           # Batch processing
│   │   └── api/                 # API routes
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── Home.py                  # Main Streamlit app
│   ├── pages/                   # Streamlit pages
│   ├── components/              # Reusable components
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Configuration

Edit `.env` file with your settings:

```env
# Database (SQLite for dev, PostgreSQL for production)
DATABASE_URL=sqlite:///./exam_checker.db

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_CLOUD_VISION_API_KEY=your_google_cloud_vision_key_here
MATHPIX_APP_ID=your_mathpix_app_id_here
MATHPIX_APP_KEY=your_mathpix_app_key_here

# OCR Settings
OCR_CONFIDENCE_THRESHOLD=0.70
DPI_SETTING=300

# Evaluation (False = Gemini, True = Claude)
USE_CLAUDE=False
```

## 📖 Usage Workflow

### Setup Phase (One-time per exam)

1. **Upload Question Paper PDF**
   - System extracts questions, marks, Bloom's taxonomy
   - Faculty reviews extracted questions

2. **Upload Answer Key PDF**
   - System extracts model answers
   - AI generates keywords and marking scheme
   - Faculty reviews and approves

### Evaluation Phase (Per student batch)

3. **Upload Student Answer Sheets**
   - Batch upload all PDFs for a course
   - System processes each sheet:
     - OCR extraction
     - Question number detection
     - Content type identification
     - AI evaluation
     - Confidence scoring

4. **Faculty Review**
   - View all students and their marks
   - Review flagged answers
   - Override marks if needed
   - Add faculty comments
   - Approve final marks

5. **Export Results**
   - Download Excel/PDF reports
   - Share with students

## 🎯 Key Capabilities

### Content Type Detection
- **Text answers**: Theory, descriptive questions
- **Math answers**: Equations, formulas, calculations
- **Code answers**: Programming solutions
- **Diagrams**: Labeled diagrams, flowcharts
- **MCQs**: Multiple choice questions

### Evaluation Strategies
- **Text**: Concept coverage, accuracy, completeness
- **Math**: Step-wise partial credit
- **Code**: Algorithm correctness (no execution)
- **Diagrams**: Label extraction + manual review
- **MCQs**: Direct comparison

### Smart Features
- Handles out-of-order answers (Q1, Q5, Q3, Q2)
- Detects unattempted questions
- Flags low-confidence answers for review
- Partial credit for correct methods
- Faculty can override all decisions

## 🧪 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Database Schema

8 main tables:
- `courses`: Course information
- `question_papers`: Question paper metadata
- `questions`: Individual questions
- `answer_keys`: Answer key metadata
- `model_answers`: Model answers with keywords
- `student_exams`: Student exam metadata
- `student_answers`: Individual answers with marks

## 🔄 Migration to Production

To switch from Gemini to Claude:

```env
# In .env file
USE_CLAUDE=True
CLAUDE_API_KEY=your_claude_api_key_here
```

No code changes required - the system automatically switches.

## 🐛 Troubleshooting

### Database connection issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### OCR not working
- Verify API keys in `.env`
- Check API quota limits
- Ensure images are high quality (300 DPI)

### Low accuracy
- Increase DPI setting
- Improve scan quality
- Adjust confidence threshold

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ for universities worldwide**
