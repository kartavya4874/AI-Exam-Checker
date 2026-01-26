"""
Module 6E: MCQ Evaluator
Simple pattern matching for multiple choice questions
"""
from typing import Dict, Optional
import re


class MCQEvaluator:
    """Evaluates MCQ answers through pattern matching"""
    
    def __init__(self):
        """Initialize MCQ evaluator"""
        pass
    
    def extract_selected_option(self, answer_text: str) -> Optional[str]:
        """
        Extract the selected option from answer text
        
        Args:
            answer_text: Student's answer text
            
        Returns:
            Selected option (A, B, C, D, etc.) or None
        """
        # Clean the text
        text = answer_text.strip().upper()
        
        # Pattern 1: Just the letter (A, B, C, D)
        if len(text) == 1 and text in 'ABCDEFGH':
            return text
        
        # Pattern 2: Letter with parentheses (A), (B)
        match = re.search(r'\(([A-H])\)', text)
        if match:
            return match.group(1)
        
        # Pattern 3: Letter with dot A., B.
        match = re.search(r'([A-H])\.', text)
        if match:
            return match.group(1)
        
        # Pattern 4: "Option A", "Answer: B"
        match = re.search(r'(?:OPTION|ANSWER|ANS)[:\s]*([A-H])', text)
        if match:
            return match.group(1)
        
        # Pattern 5: First letter that appears
        match = re.search(r'([A-H])', text)
        if match:
            return match.group(1)
        
        return None
    
    def compare_with_key(
        self,
        selected_option: Optional[str],
        correct_option: str
    ) -> bool:
        """
        Compare selected option with correct answer
        
        Args:
            selected_option: Student's selected option
            correct_option: Correct option from answer key
            
        Returns:
            True if correct, False otherwise
        """
        if selected_option is None:
            return False
        
        return selected_option.upper() == correct_option.upper()
    
    def evaluate_mcq_answer(
        self,
        student_answer: str,
        correct_option: str,
        marks_per_question: int = 1
    ) -> Dict:
        """
        Evaluate MCQ answer
        
        Args:
            student_answer: Student's answer text
            correct_option: Correct option (A, B, C, D, etc.)
            marks_per_question: Marks for correct answer (default: 1)
            
        Returns:
            Evaluation result
        """
        # Extract selected option
        selected = self.extract_selected_option(student_answer)
        
        # Compare with correct answer
        is_correct = self.compare_with_key(selected, correct_option)
        
        # Calculate marks
        marks_awarded = marks_per_question if is_correct else 0
        
        result = {
            "marks_awarded": marks_awarded,
            "max_marks": marks_per_question,
            "selected_option": selected if selected else "Not detected",
            "correct_option": correct_option,
            "is_correct": is_correct,
            "feedback": self._generate_feedback(selected, correct_option, is_correct),
            "needs_review": selected is None  # Flag if option couldn't be detected
        }
        
        return result
    
    def _generate_feedback(
        self,
        selected: Optional[str],
        correct: str,
        is_correct: bool
    ) -> str:
        """Generate feedback for MCQ"""
        
        if selected is None:
            return "⚠️ Could not detect selected option. Please review manually."
        
        if is_correct:
            return f"✓ Correct! Selected option {selected}."
        else:
            return f"✗ Incorrect. Selected {selected}, correct answer is {correct}."


# Convenience function
def evaluate_mcq(
    student_answer: str,
    correct_option: str,
    marks_per_question: int = 1
) -> Dict:
    """
    Quick MCQ evaluation function
    
    Args:
        student_answer: Student's answer
        correct_option: Correct option
        marks_per_question: Marks for correct answer
        
    Returns:
        Evaluation result
    """
    evaluator = MCQEvaluator()
    return evaluator.evaluate_mcq_answer(
        student_answer, correct_option, marks_per_question
    )
