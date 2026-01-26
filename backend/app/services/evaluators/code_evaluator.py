"""
Module 6C: Code Answer Evaluator
Evaluates programming answers based on logic (NO CODE EXECUTION for security)
"""
from typing import Dict, List, Optional
import re
from .ai_client import AIEvaluator


class CodeAnswerEvaluator:
    """Evaluates code answers based on algorithm and logic"""
    
    def __init__(self, ai_evaluator: AIEvaluator):
        """
        Initialize code evaluator
        
        Args:
            ai_evaluator: AI evaluator instance
        """
        self.ai = ai_evaluator
    
    def extract_code_blocks(self, answer_text: str) -> List[str]:
        """
        Extract code blocks from answer text
        
        Args:
            answer_text: Student's answer text
            
        Returns:
            List of code blocks
        """
        code_blocks = []
        
        # Look for code fence markers
        fence_pattern = r'```[\w]*\n(.*?)```'
        fenced_blocks = re.findall(fence_pattern, answer_text, re.DOTALL)
        if fenced_blocks:
            return fenced_blocks
        
        # Look for indented blocks (common in handwritten code)
        lines = answer_text.split('\n')
        current_block = []
        in_code = False
        
        for line in lines:
            # Check if line is indented (starts with spaces/tabs)
            if line.startswith(('    ', '\t')) or (in_code and line.strip()):
                current_block.append(line)
                in_code = True
            else:
                if current_block:
                    code_blocks.append('\n'.join(current_block))
                    current_block = []
                in_code = False
        
        # Add last block if exists
        if current_block:
            code_blocks.append('\n'.join(current_block))
        
        # If no blocks found, treat entire text as code
        if not code_blocks:
            code_blocks = [answer_text]
        
        return code_blocks
    
    def evaluate_code_answer(
        self,
        student_answer: str,
        model_answer: str,
        max_marks: int,
        question_text: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict:
        """
        Evaluate code answer based on logic and algorithm
        
        Args:
            student_answer: Student's code
            model_answer: Model code solution
            max_marks: Maximum marks
            question_text: Optional question text
            language: Programming language (optional)
            
        Returns:
            Evaluation result
        """
        # Extract code blocks
        student_code_blocks = self.extract_code_blocks(student_answer)
        model_code_blocks = self.extract_code_blocks(model_answer)
        
        # Build evaluation prompt
        prompt = self._build_code_prompt(
            student_code_blocks,
            model_code_blocks,
            max_marks,
            question_text,
            language
        )
        
        # Get AI evaluation
        response = self.ai.generate(prompt, max_tokens=2000)
        
        # Parse response
        result = self._parse_code_response(response, max_marks)
        
        return result
    
    def _build_code_prompt(
        self,
        student_code: List[str],
        model_code: List[str],
        max_marks: int,
        question_text: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        """Build prompt for code evaluation"""
        
        lang_note = f" (Language: {language})" if language else ""
        
        prompt = f"""You are an expert programming instructor evaluating a student's code{lang_note}.

**CRITICAL: DO NOT EXECUTE THE CODE. Evaluate based on logic and algorithm only.**

**Question:** {question_text if question_text else "Not provided"}

**Maximum Marks:** {max_marks}

**Model Solution:**
{chr(10).join(model_code)}

**Student's Solution:**
{chr(10).join(student_code)}

**Evaluation Instructions:**
1. **DO NOT execute the code** - evaluate logic only
2. **Ignore variable names** - focus on algorithm correctness
3. **Ignore minor syntax differences** - focus on approach
4. **Check algorithm correctness** - is the logic sound?
5. **Check edge case handling** - does it consider special cases?
6. **Evaluate code structure** - is it well-organized?
7. Award partial credit for correct approach even if implementation has issues

**Provide evaluation in this EXACT format:**

MARKS: [X/{max_marks}]
LOGIC_SCORE: [Score out of 10 for algorithm correctness]
APPROACH_CORRECT: [Yes/No/Partial]
FEEDBACK: [Overall assessment]
STRENGTHS: [What the student did well]
IMPROVEMENTS: [What could be improved]
EDGE_CASES: [How well edge cases are handled]

Focus on conceptual understanding over syntax perfection.
"""
        return prompt
    
    def _parse_code_response(self, response: str, max_marks: int) -> Dict:
        """Parse code evaluation response"""
        
        result = {
            "marks_awarded": 0.0,
            "max_marks": max_marks,
            "logic_score": 0.0,
            "approach_correct": "Unknown",
            "feedback": "",
            "strengths": "",
            "improvements": "",
            "edge_cases": ""
        }
        
        try:
            # Extract marks
            marks_match = re.search(r'MARKS:\s*(\d+(?:\.\d+)?)', response, re.IGNORECASE)
            if marks_match:
                result["marks_awarded"] = min(float(marks_match.group(1)), max_marks)
            
            # Logic score
            logic_match = re.search(r'LOGIC_SCORE:\s*(\d+(?:\.\d+)?)', response, re.IGNORECASE)
            if logic_match:
                result["logic_score"] = float(logic_match.group(1))
            
            # Approach correct
            approach_match = re.search(r'APPROACH_CORRECT:\s*(Yes|No|Partial)', response, re.IGNORECASE)
            if approach_match:
                result["approach_correct"] = approach_match.group(1)
            
            # Feedback
            feedback_match = re.search(r'FEEDBACK:\s*(.+?)(?=STRENGTHS:|$)', response, re.IGNORECASE | re.DOTALL)
            if feedback_match:
                result["feedback"] = feedback_match.group(1).strip()
            
            # Strengths
            strengths_match = re.search(r'STRENGTHS:\s*(.+?)(?=IMPROVEMENTS:|$)', response, re.IGNORECASE | re.DOTALL)
            if strengths_match:
                result["strengths"] = strengths_match.group(1).strip()
            
            # Improvements
            improvements_match = re.search(r'IMPROVEMENTS:\s*(.+?)(?=EDGE_CASES:|$)', response, re.IGNORECASE | re.DOTALL)
            if improvements_match:
                result["improvements"] = improvements_match.group(1).strip()
            
            # Edge cases
            edge_match = re.search(r'EDGE_CASES:\s*(.+?)$', response, re.IGNORECASE | re.DOTALL)
            if edge_match:
                result["edge_cases"] = edge_match.group(1).strip()
        
        except Exception as e:
            print(f"Error parsing code response: {e}")
            result["feedback"] = "Error parsing evaluation. Please review manually."
        
        return result


# Convenience function
def evaluate_code(
    student_answer: str,
    model_answer: str,
    max_marks: int,
    ai_evaluator: AIEvaluator,
    question_text: Optional[str] = None,
    language: Optional[str] = None
) -> Dict:
    """
    Quick code evaluation function
    
    Args:
        student_answer: Student's code
        model_answer: Model code
        max_marks: Maximum marks
        ai_evaluator: AI evaluator instance
        question_text: Optional question text
        language: Programming language
        
    Returns:
        Evaluation result
    """
    evaluator = CodeAnswerEvaluator(ai_evaluator)
    return evaluator.evaluate_code_answer(
        student_answer, model_answer, max_marks, question_text, language
    )
