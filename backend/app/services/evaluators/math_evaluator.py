"""
Module 6B: Math Answer Evaluator
Evaluates mathematical answers with step-wise partial credit
"""
from typing import Dict, List, Optional
import re
from .ai_client import AIEvaluator


class MathAnswerEvaluator:
    """Evaluates math answers with step-wise grading"""
    
    def __init__(self, ai_evaluator: AIEvaluator):
        """
        Initialize math evaluator
        
        Args:
            ai_evaluator: AI evaluator instance
        """
        self.ai = ai_evaluator
    
    def extract_steps(self, math_answer: str) -> List[str]:
        """
        Extract individual steps from math answer
        
        Args:
            math_answer: Student's math answer
            
        Returns:
            List of steps
        """
        steps = []
        
        # Look for explicit step markers
        step_patterns = [
            r'Step\s+\d+[:\.]?\s*(.+?)(?=Step\s+\d+|$)',
            r'\d+\.\s*(.+?)(?=\d+\.|$)',
            r'\(\d+\)\s*(.+?)(?=\(\d+\)|$)'
        ]
        
        for pattern in step_patterns:
            matches = re.findall(pattern, math_answer, re.IGNORECASE | re.DOTALL)
            if matches:
                steps = [m.strip() for m in matches if m.strip()]
                return steps
        
        # If no explicit markers, split by line breaks
        lines = [line.strip() for line in math_answer.split('\n') if line.strip()]
        if len(lines) > 1:
            return lines
        
        # Single step answer
        return [math_answer]
    
    def evaluate_math_answer(
        self,
        student_answer: str,
        model_answer: str,
        max_marks: int,
        question_text: Optional[str] = None
    ) -> Dict:
        """
        Evaluate math answer with step-wise partial credit
        
        Args:
            student_answer: Student's math answer
            model_answer: Model answer
            max_marks: Maximum marks
            question_text: Optional question text
            
        Returns:
            Evaluation result with step-wise breakdown
        """
        # Extract steps
        student_steps = self.extract_steps(student_answer)
        model_steps = self.extract_steps(model_answer)
        
        # Build evaluation prompt
        prompt = self._build_math_prompt(
            student_answer,
            student_steps,
            model_answer,
            model_steps,
            max_marks,
            question_text
        )
        
        # Get AI evaluation
        response = self.ai.generate(prompt, max_tokens=2000)
        
        # Parse response
        result = self._parse_math_response(response, max_marks, len(student_steps))
        
        return result
    
    def _build_math_prompt(
        self,
        student_answer: str,
        student_steps: List[str],
        model_answer: str,
        model_steps: List[str],
        max_marks: int,
        question_text: Optional[str] = None
    ) -> str:
        """Build prompt for math evaluation"""
        
        prompt = f"""You are an expert mathematics examiner evaluating a student's solution.

**Question:** {question_text if question_text else "Not provided"}

**Maximum Marks:** {max_marks}

**Model Solution:**
{model_answer}

**Model Steps ({len(model_steps)}):**
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(model_steps))}

**Student's Solution:**
{student_answer}

**Student's Steps ({len(student_steps)}):**
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(student_steps))}

**Evaluation Instructions:**
1. Award PARTIAL CREDIT for each correct step
2. If METHOD is correct but CALCULATION is wrong, give partial marks
3. Check if final answer is correct
4. Evaluate mathematical reasoning and approach
5. Be strict on mathematical accuracy but fair on minor errors

**Provide evaluation in this EXACT format:**

MARKS: [X/{max_marks}]
CORRECT_STEPS: [Number of correct steps]
TOTAL_STEPS: [Total number of steps]
FINAL_ANSWER: [Correct/Incorrect]
METHOD_SCORE: [Score for approach/method out of 10]
FEEDBACK: [Overall assessment]
STEP_BREAKDOWN: [Brief note on each step's correctness]

Provide fair step-wise partial credit.
"""
        return prompt
    
    def _parse_math_response(self, response: str, max_marks: int, total_steps: int) -> Dict:
        """Parse math evaluation response"""
        
        result = {
            "marks_awarded": 0.0,
            "max_marks": max_marks,
            "correct_steps": 0,
            "total_steps": total_steps,
            "final_answer_correct": False,
            "method_score": 0.0,
            "feedback": "",
            "step_breakdown": ""
        }
        
        try:
            # Extract marks
            marks_match = re.search(r'MARKS:\s*(\d+(?:\.\d+)?)', response, re.IGNORECASE)
            if marks_match:
                result["marks_awarded"] = min(float(marks_match.group(1)), max_marks)
            
            # Extract correct steps
            correct_steps_match = re.search(r'CORRECT_STEPS:\s*(\d+)', response, re.IGNORECASE)
            if correct_steps_match:
                result["correct_steps"] = int(correct_steps_match.group(1))
            
            # Extract total steps
            total_steps_match = re.search(r'TOTAL_STEPS:\s*(\d+)', response, re.IGNORECASE)
            if total_steps_match:
                result["total_steps"] = int(total_steps_match.group(1))
            
            # Final answer
            final_answer_match = re.search(r'FINAL_ANSWER:\s*(Correct|Incorrect)', response, re.IGNORECASE)
            if final_answer_match:
                result["final_answer_correct"] = final_answer_match.group(1).lower() == "correct"
            
            # Method score
            method_match = re.search(r'METHOD_SCORE:\s*(\d+(?:\.\d+)?)', response, re.IGNORECASE)
            if method_match:
                result["method_score"] = float(method_match.group(1))
            
            # Feedback
            feedback_match = re.search(r'FEEDBACK:\s*(.+?)(?=STEP_BREAKDOWN:|$)', response, re.IGNORECASE | re.DOTALL)
            if feedback_match:
                result["feedback"] = feedback_match.group(1).strip()
            
            # Step breakdown
            breakdown_match = re.search(r'STEP_BREAKDOWN:\s*(.+?)$', response, re.IGNORECASE | re.DOTALL)
            if breakdown_match:
                result["step_breakdown"] = breakdown_match.group(1).strip()
        
        except Exception as e:
            print(f"Error parsing math response: {e}")
            result["feedback"] = "Error parsing evaluation. Please review manually."
        
        return result


# Convenience function
def evaluate_math(
    student_answer: str,
    model_answer: str,
    max_marks: int,
    ai_evaluator: AIEvaluator,
    question_text: Optional[str] = None
) -> Dict:
    """
    Quick math evaluation function
    
    Args:
        student_answer: Student's math answer
        model_answer: Model answer
        max_marks: Maximum marks
        ai_evaluator: AI evaluator instance
        question_text: Optional question text
        
    Returns:
        Evaluation result with step-wise breakdown
    """
    evaluator = MathAnswerEvaluator(ai_evaluator)
    return evaluator.evaluate_math_answer(
        student_answer, model_answer, max_marks, question_text
    )
