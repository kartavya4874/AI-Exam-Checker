"""
Document upload and management endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime
from ..database import get_db
from ..models.database_models import QuestionPaper, Course

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-question-paper")
async def upload_question_paper(
    file: UploadFile = File(...),
    course_code: str = None,
    db: Session = Depends(get_db)
):
    """
    Upload a question paper PDF
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Create upload directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_dir = os.path.join(UPLOAD_DIR, f"question_papers_{timestamp}")
        os.makedirs(doc_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(doc_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Create or get course
        course = db.query(Course).filter(Course.course_code == course_code).first()
        if not course:
            course = Course(
                course_code=course_code or "UNKNOWN",
                name="Unknown Course",
                department="Unknown"
            )
            db.add(course)
            db.commit()
        
        # Create question paper record
        qp = QuestionPaper(
            course_id=course.id,
            pdf_path=file_path,
            total_marks=100  # Default, can be updated later
        )
        db.add(qp)
        db.commit()
        db.refresh(qp)
        
        return {
            "status": "success",
            "message": "Question paper uploaded successfully",
            "question_paper_id": qp.id,
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-answer-key")
async def upload_answer_key(
    file: UploadFile = File(...),
    question_paper_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Upload an answer key PDF
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Create upload directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_dir = os.path.join(UPLOAD_DIR, f"answer_keys_{timestamp}")
        os.makedirs(doc_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(doc_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        return {
            "status": "success",
            "message": "Answer key uploaded successfully",
            "file_path": file_path,
            "question_paper_id": question_paper_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-student-answers")
async def upload_student_answers(
    files: list[UploadFile] = File(...),
    question_paper_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Batch upload student answer sheets
    """
    uploaded_files = []
    
    try:
        # Create upload directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_dir = os.path.join(UPLOAD_DIR, f"student_answers_{timestamp}")
        os.makedirs(doc_dir, exist_ok=True)
        
        for file in files:
            if not file.filename.endswith('.pdf'):
                continue
            
            file_path = os.path.join(doc_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            uploaded_files.append({
                "filename": file.filename,
                "file_path": file_path
            })
        
        return {
            "status": "success",
            "message": f"Uploaded {len(uploaded_files)} student answer sheets",
            "files": uploaded_files,
            "question_paper_id": question_paper_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/documents/{doc_type}")
async def get_documents(doc_type: str, db: Session = Depends(get_db)):
    """
    Get list of uploaded documents
    doc_type: 'question_papers', 'answer_keys', 'student_answers'
    """
    try:
        if doc_type == "question_papers":
            docs = db.query(QuestionPaper).all()
            return {
                "status": "success",
                "documents": [
                    {
                        "id": d.id,
                        "course": d.course.course_code,
                        "path": d.pdf_path,
                        "created_at": d.created_at.isoformat(),
                        "processed": d.processed
                    }
                    for d in docs
                ]
            }
        else:
            return {
                "status": "success",
                "documents": []
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
