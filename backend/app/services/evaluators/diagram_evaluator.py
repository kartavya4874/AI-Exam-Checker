"""
Module 6D: Diagram Answer Evaluator
Evaluates diagrams based on label extraction (always flags for manual review)
"""
from typing import Dict, List, Optional
import re


class DiagramAnswerEvaluator:
    """Evaluates diagram answers through label extraction"""
    
    def __init__(self):
        """Initialize diagram evaluator"""
        pass
    
    def extract_diagram_labels(self, ocr_text: str) -> List[str]:
        """
        Extract labels from OCR text of diagram region
        
        Args:
            ocr_text: OCR extracted text from diagram area
            
        Returns:
            List of extracted labels
        """
        # Split by common delimiters
        labels = []
        
        # Remove common diagram artifacts
        cleaned_text = re.sub(r'[→←↑↓⟶⟵⟷]', ' ', ocr_text)
        
        # Split by newlines and common separators
        parts = re.split(r'[\n,;]', cleaned_text)
        
        for part in parts:
            part = part.strip()
            if part and len(part) > 1:  # Ignore single characters
                labels.append(part)
        
        return labels
    
    def check_required_components(
        self,
        extracted_labels: List[str],
        required_components: List[str]
    ) -> Dict:
        """
        Check if required components are present in extracted labels
        
        Args:
            extracted_labels: Labels extracted from student's diagram
            required_components: Required components from model answer
            
        Returns:
            Dictionary with match statistics
        """
        extracted_lower = [label.lower() for label in extracted_labels]
        matches = []
        missing = []
        
        for component in required_components:
            component_lower = component.lower()
            # Check if component or similar text is in extracted labels
            found = any(component_lower in label or label in component_lower 
                       for label in extracted_lower)
            
            if found:
                matches.append(component)
            else:
                missing.append(component)
        
        return {
            "matched_components": matches,
            "missing_components": missing,
            "match_count": len(matches),
            "total_required": len(required_components),
            "match_percentage": (len(matches) / len(required_components) * 100) if required_components else 0
        }
    
    def evaluate_diagram_answer(
        self,
        ocr_text: str,
        required_components: List[str],
        max_marks: int
    ) -> Dict:
        """
        Evaluate diagram answer (with automatic manual review flag)
        
        Args:
            ocr_text: OCR text from diagram region
            required_components: Required components/labels
            max_marks: Maximum marks
            
        Returns:
            Evaluation result (always flagged for review)
        """
        # Extract labels
        extracted_labels = self.extract_diagram_labels(ocr_text)
        
        # Check components
        component_check = self.check_required_components(
            extracted_labels,
            required_components
        )
        
        # Calculate partial marks based on label coverage
        # This is a preliminary score - faculty will review
        match_percentage = component_check["match_percentage"]
        preliminary_marks = (match_percentage / 100) * max_marks
        
        result = {
            "marks_awarded": round(preliminary_marks, 1),
            "max_marks": max_marks,
            "extracted_labels": extracted_labels,
            "matched_components": component_check["matched_components"],
            "missing_components": component_check["missing_components"],
            "match_percentage": match_percentage,
            "feedback": self._generate_feedback(component_check),
            "needs_review": True,  # ALWAYS flag for manual review
            "review_reason": "Diagram evaluation requires visual verification"
        }
        
        return result
    
    def _generate_feedback(self, component_check: Dict) -> str:
        """Generate feedback based on component matching"""
        
        match_count = component_check["match_count"]
        total = component_check["total_required"]
        percentage = component_check["match_percentage"]
        
        feedback = f"Preliminary label-based evaluation: {match_count}/{total} components detected ({percentage:.1f}%). "
        
        if percentage >= 80:
            feedback += "Most required components appear to be present. "
        elif percentage >= 50:
            feedback += "Some required components are present. "
        else:
            feedback += "Many required components may be missing. "
        
        feedback += "⚠️ Manual visual review required for accurate assessment."
        
        return feedback


# Convenience function
def evaluate_diagram(
    ocr_text: str,
    required_components: List[str],
    max_marks: int
) -> Dict:
    """
    Quick diagram evaluation function
    
    Args:
        ocr_text: OCR text from diagram
        required_components: Required labels/components
        max_marks: Maximum marks
        
    Returns:
        Evaluation result (always flagged for review)
    """
    evaluator = DiagramAnswerEvaluator()
    return evaluator.evaluate_diagram_answer(
        ocr_text, required_components, max_marks
    )
