"""
Module 6A: Text Answer Evaluator
Evaluates theory/descriptive answers using AI
"""
from typing import Dict, List, Optional
import json
import re
from .ai_client import AIEvaluator


class TextAnswerEvaluator:
    """Evaluates text-based answers using AI"""
    
    def __init__(self, ai_evaluator: AIEvaluator):
        """
        Initialize text evaluator
        
        Args:
            ai_evaluator: AI evaluator instance (Gemini or Claude)
        """
        self.ai = ai_evaluator
    
    def evaluate_text_answer(
        self,
        student_answer: str,
        model_answer: str,
        keywords: List[str],
        max_marks: int,
        question_text: Optional[str] = None
    ) -> Dict:
        """
        Evaluate a text answer using AI
        
        Args:
            student_answer: Student's answer text
            model_answer: Model/correct answer
            keywords: Key concepts that should be covered
            max_marks: Maximum marks for this question
            question_text: Optional question text for context
            
        Returns:
            Dictionary with marks, feedback, strengths, improvements
        """
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            student_answer,
            model_answer,
            keywords,
            max_marks,
            question_text
        )
        
        # Get AI response
        response = self.ai.generate(prompt, max_tokens=1500)
        
        # Parse response
        result = self._parse_ai_response(response, max_marks)
        
        # Add metadata
        result["keywords_matched"] = self._count_keyword_matches(student_answer, keywords)
        result["total_keywords"] = len(keywords)
        
        return result
    
    def _build_evaluation_prompt(
        self,
        student_answer: str,
        model_answer: str,
        keywords: List[str],
        max_marks: int,
        question_text: Optional[str] = None
    ) -> str:
        """Build prompt for AI evaluation"""
        
        prompt = f"""You are an expert examiner evaluating a student's answer for a university exam.

**Question:** {question_text if question_text else "Not provided"}

**Maximum Marks:** {max_marks}

**Model Answer:**
{model_answer}

**Key Concepts (must be covered):**
{', '.join(keywords)}

**Student's Answer:**
{student_answer}

**Evaluation Instructions:**
1. Be STRICT on factual accuracy and core concepts
2. Be CONTEXT-AWARE on wording differences (same meaning = acceptable)
3. Award partial credit for partially correct concepts
4. Check coverage of key concepts listed above
5. Evaluate completeness and depth of explanation

**Provide your evaluation in this EXACT format:**

MARKS: [X/{max_marks}]
FEEDBACK: [Overall assessment in 2-3 sentences]
STRENGTHS: [What the student did well, bullet points]
IMPROVEMENTS: [What could be improved, bullet points]

Be fair but strict. Focus on conceptual understanding over exact wording.
"""
        return prompt
    
    def _parse_ai_response(self, response: str, max_marks: int) -> Dict:
        """Parse AI response into structured format"""
        
        result = {
            "marks_awarded": 0.0,
            "max_marks": max_marks,
            "feedback": "",
            "strengths": [],
            "improvements": []
        }
        
        try:
            # Extract marks
            marks_match = re.search(r'MARKS:\s*(\d+(?:\.\d+)?)', response, re.IGNORECASE)
            if marks_match:
                marks = float(marks_match.group(1))
                result["marks_awarded"] = min(marks, max_marks)
            
            # Extract feedback
            feedback_match = re.search(r'FEEDBACK:\s*(.+?)(?=STRENGTHS:|IMPROVEMENTS:|$)', response, re.IGNORECASE | re.DOTALL)
            if feedback_match:
                result["feedback"] = feedback_match.group(1).strip()
            
            # Extract strengths
            strengths_match = re.search(r'STRENGTHS:\s*(.+?)(?=IMPROVEMENTS:|$)', response, re.IGNORECASE | re.DOTALL)
            if strengths_match:
                strengths_text = strengths_match.group(1).strip()
                result["strengths"] = [s.strip('- ').strip() for s in strengths_text.split('\n') if s.strip()]
            
            # Extract improvements
            improvements_match = re.search(r'IMPROVEMENTS:\s*(.+?)$', response, re.IGNORECASE | re.DOTALL)
            if improvements_match:
                improvements_text = improvements_match.group(1).strip()
                result["improvements"] = [i.strip('- ').strip() for i in improvements_text.split('\n') if i.strip()]
        
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            result["feedback"] = "Error parsing evaluation. Please review manually."
        
        return result
    
    def _count_keyword_matches(self, student_answer: str, keywords: List[str]) -> int:
        """Count how many keywords are present in student answer"""
        student_lower = student_answer.lower()
        matches = 0
        
        for keyword in keywords:
            if keyword.lower() in student_lower:
                matches += 1
        
        return matches


# Convenience function
def evaluate_text(
    student_answer: str,
    model_answer: str,
    keywords: List[str],
    max_marks: int,
    ai_evaluator: AIEvaluator,
    question_text: Optional[str] = None
) -> Dict:
    """
    Quick text evaluation function
    
    Args:
        student_answer: Student's answer
        model_answer: Model answer
        keywords: Key concepts
        max_marks: Maximum marks
        ai_evaluator: AI evaluator instance
        question_text: Optional question text
        
    Returns:
        Evaluation result dictionary
    """
    evaluator = TextAnswerEvaluator(ai_evaluator)
    return evaluator.evaluate_text_answer(
        student_answer, model_answer, keywords, max_marks, question_text
    )
