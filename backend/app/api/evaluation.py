"""
Evaluation endpoints for grading answers
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..services.evaluators.ai_client import AIEvaluator

router = APIRouter()


class AnswerEvaluationRequest(BaseModel):
    student_answer: str
    model_answer: str
    question_text: str
    marks: int
    question_type: str = "text"  # text, math, code, diagram, mcq


class AnswerEvaluationResponse(BaseModel):
    marks_awarded: float
    feedback: str
    confidence: float
    should_review: bool


@router.post("/evaluate-answer", response_model=AnswerEvaluationResponse)
async def evaluate_answer_endpoint(
    request: AnswerEvaluationRequest,
    db: Session = Depends(get_db)
):
    """
    Evaluate a single student answer against model answer
    """
    try:
        # Call the AI evaluation service
        result = await evaluate_answer(
            student_answer=request.student_answer,
            model_answer=request.model_answer,
            question_text=request.question_text,
            marks=request.marks,
            question_type=request.question_type
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/batch-evaluate")
async def batch_evaluate(
    data: dict,
    db: Session = Depends(get_db)
):
    """
    Batch evaluate multiple answers
    """
    try:
        answers = data.get("answers", [])
        results = []
        
        for answer in answers:
            result = await evaluate_answer(
                student_answer=answer.get("student_answer", ""),
                model_answer=answer.get("model_answer", ""),
                question_text=answer.get("question_text", ""),
                marks=answer.get("marks", 0),
                question_type=answer.get("question_type", "text")
            )
            results.append({
                "question_id": answer.get("question_id"),
                "evaluation": result
            })
        
        return {
            "status": "success",
            "total_evaluated": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch evaluation failed: {str(e)}")


@router.get("/ocr-text/{document_id}")
async def extract_ocr_text(document_id: str):
    """
    Extract text from a document using OCR
    """
    try:
        # This would call the OCR service to extract text from PDFs
        return {
            "status": "success",
            "document_id": document_id,
            "text": "OCR extracted text would appear here"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")
