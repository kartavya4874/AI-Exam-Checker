"""
Confidence scoring system for OCR and evaluation results
Module 7: Confidence Scorer
"""
from typing import Dict, List
from enum import Enum


class ReviewReason(Enum):
    """Reasons for flagging an answer for manual review"""
    LOW_OCR_CONFIDENCE = "OCR confidence below threshold"
    DIAGRAM_CONTENT = "Contains diagram (always requires review)"
    AMBIGUOUS_CONTENT = "Ambiguous content type detected"
    EVALUATION_UNCERTAINTY = "AI evaluation uncertainty"
    MISSING_ANSWER = "Answer not attempted"
    MULTIPLE_INTERPRETATIONS = "Multiple valid interpretations possible"


class ConfidenceScorer:
    """Calculates confidence scores and determines if manual review is needed"""
    
    def __init__(self, ocr_threshold: float = 0.70):
        """
        Initialize confidence scorer
        
        Args:
            ocr_threshold: Minimum OCR confidence (default: 0.70)
        """
        self.ocr_threshold = ocr_threshold
    
    def calculate_ocr_confidence(
        self,
        ocr_result
    ) -> float:
        """
        Calculate overall OCR confidence from result
        
        Args:
            ocr_result: OCRResult object
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        return ocr_result.confidence
    
    def calculate_evaluation_confidence(
        self,
        answer_type: str,
        evaluation_result: Dict
    ) -> float:
        """
        Calculate confidence in evaluation based on answer type
        
        Args:
            answer_type: Type of answer (text, math, code, diagram, mcq)
            evaluation_result: Evaluation result dictionary
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Different confidence calculations based on type
        
        if answer_type == "mcq":
            # MCQs are deterministic - high confidence
            return 1.0
        
        elif answer_type == "diagram":
            # Diagrams always need review - low confidence
            return 0.3
        
        elif answer_type == "text":
            # Text evaluation confidence based on keyword matches
            keywords_matched = evaluation_result.get("keywords_matched", 0)
            total_keywords = evaluation_result.get("total_keywords", 1)
            match_ratio = keywords_matched / max(total_keywords, 1)
            
            # High match ratio = high confidence
            return min(0.9, 0.5 + (match_ratio * 0.4))
        
        elif answer_type == "math":
            # Math confidence based on step correctness
            correct_steps = evaluation_result.get("correct_steps", 0)
            total_steps = evaluation_result.get("total_steps", 1)
            step_ratio = correct_steps / max(total_steps, 1)
            
            return min(0.9, 0.6 + (step_ratio * 0.3))
        
        elif answer_type == "code":
            # Code evaluation is more subjective - moderate confidence
            logic_score = evaluation_result.get("logic_score", 0.5)
            return min(0.85, 0.5 + (logic_score * 0.35))
        
        else:
            # Unknown type - low confidence
            return 0.5
    
    def should_flag_for_review(
        self,
        ocr_confidence: float,
        evaluation_confidence: float,
        answer_type: str,
        is_attempted: bool
    ) -> tuple[bool, List[ReviewReason]]:
        """
        Determine if answer should be flagged for manual review
        
        Args:
            ocr_confidence: OCR confidence score
            evaluation_confidence: Evaluation confidence score
            answer_type: Type of answer
            is_attempted: Whether student attempted the question
            
        Returns:
            Tuple of (should_flag, list_of_reasons)
        """
        reasons = []
        
        # Not attempted
        if not is_attempted:
            reasons.append(ReviewReason.MISSING_ANSWER)
        
        # Low OCR confidence
        if ocr_confidence < self.ocr_threshold:
            reasons.append(ReviewReason.LOW_OCR_CONFIDENCE)
        
        # Diagrams always need review
        if answer_type == "diagram":
            reasons.append(ReviewReason.DIAGRAM_CONTENT)
        
        # Low evaluation confidence
        if evaluation_confidence < 0.6:
            reasons.append(ReviewReason.EVALUATION_UNCERTAINTY)
        
        # Ambiguous content
        if answer_type == "mixed" or answer_type == "unknown":
            reasons.append(ReviewReason.AMBIGUOUS_CONTENT)
        
        should_flag = len(reasons) > 0
        
        return should_flag, reasons
    
    def calculate_overall_confidence(
        self,
        ocr_confidence: float,
        evaluation_confidence: float
    ) -> float:
        """
        Calculate overall confidence score
        
        Args:
            ocr_confidence: OCR confidence
            evaluation_confidence: Evaluation confidence
            
        Returns:
            Overall confidence (weighted average)
        """
        # Weight: 40% OCR, 60% evaluation
        return (ocr_confidence * 0.4) + (evaluation_confidence * 0.6)
    
    def get_confidence_level(self, confidence: float) -> str:
        """
        Get human-readable confidence level
        
        Args:
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            Confidence level string
        """
        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.75:
            return "High"
        elif confidence >= 0.6:
            return "Medium"
        elif confidence >= 0.4:
            return "Low"
        else:
            return "Very Low"


# Convenience function
def score_answer_confidence(
    ocr_result,
    evaluation_result: Dict,
    answer_type: str,
    is_attempted: bool = True,
    ocr_threshold: float = 0.70
) -> Dict:
    """
    Complete confidence scoring for an answer
    
    Args:
        ocr_result: OCRResult object
        evaluation_result: Evaluation result dictionary
        answer_type: Type of answer
        is_attempted: Whether answer was attempted
        ocr_threshold: OCR confidence threshold
        
    Returns:
        Dictionary with confidence scores and review flags
    """
    scorer = ConfidenceScorer(ocr_threshold)
    
    ocr_conf = scorer.calculate_ocr_confidence(ocr_result)
    eval_conf = scorer.calculate_evaluation_confidence(answer_type, evaluation_result)
    overall_conf = scorer.calculate_overall_confidence(ocr_conf, eval_conf)
    
    should_flag, reasons = scorer.should_flag_for_review(
        ocr_conf, eval_conf, answer_type, is_attempted
    )
    
    return {
        "ocr_confidence": ocr_conf,
        "evaluation_confidence": eval_conf,
        "overall_confidence": overall_conf,
        "confidence_level": scorer.get_confidence_level(overall_conf),
        "needs_review": should_flag,
        "review_reasons": [r.value for r in reasons]
    }
