"""
Model Fine-Tuning System
Learns from sample answer sheets and faculty marking patterns
"""
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class MarkingPatternLearner:
    """Learns and adapts to faculty marking patterns"""
    
    def __init__(self, storage_path: str = "./marking_patterns"):
        """
        Initialize marking pattern learner
        
        Args:
            storage_path: Directory to store learned patterns
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """Load existing marking patterns"""
        pattern_file = self.storage_path / "patterns.json"
        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                return json.load(f)
        return {
            "courses": {},
            "faculty_preferences": {},
            "common_adjustments": [],
            "keyword_weights": {}
        }
    
    def _save_patterns(self):
        """Save marking patterns to disk"""
        pattern_file = self.storage_path / "patterns.json"
        with open(pattern_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def record_faculty_adjustment(
        self,
        course_code: str,
        question_type: str,
        ai_marks: float,
        faculty_marks: float,
        reason: str = "",
        faculty_id: str = ""
    ):
        """
        Record when faculty overrides AI marks
        
        Args:
            course_code: Course code
            question_type: Type of question (text, math, code, etc.)
            ai_marks: Marks given by AI
            faculty_marks: Marks given by faculty
            reason: Reason for adjustment
            faculty_id: Faculty identifier
        """
        # Initialize course if not exists
        if course_code not in self.patterns["courses"]:
            self.patterns["courses"][course_code] = {
                "adjustments": [],
                "avg_difference": 0.0,
                "strictness_factor": 1.0
            }
        
        # Record adjustment
        adjustment = {
            "timestamp": datetime.now().isoformat(),
            "question_type": question_type,
            "ai_marks": ai_marks,
            "faculty_marks": faculty_marks,
            "difference": faculty_marks - ai_marks,
            "reason": reason,
            "faculty_id": faculty_id
        }
        
        self.patterns["courses"][course_code]["adjustments"].append(adjustment)
        self.patterns["common_adjustments"].append(adjustment)
        
        # Update strictness factor
        self._update_strictness_factor(course_code)
        
        # Save patterns
        self._save_patterns()
    
    def _update_strictness_factor(self, course_code: str):
        """Calculate strictness factor based on historical adjustments"""
        adjustments = self.patterns["courses"][course_code]["adjustments"]
        
        if len(adjustments) < 5:  # Need minimum data
            return
        
        # Calculate average difference
        recent_adjustments = adjustments[-20:]  # Last 20 adjustments
        avg_diff = sum(a["difference"] for a in recent_adjustments) / len(recent_adjustments)
        
        self.patterns["courses"][course_code]["avg_difference"] = avg_diff
        
        # Strictness factor: if faculty consistently gives lower marks, AI should be stricter
        # Positive avg_diff = faculty more lenient, negative = faculty stricter
        self.patterns["courses"][course_code]["strictness_factor"] = 1.0 + (avg_diff / 10.0)
    
    def get_adjusted_marks(
        self,
        course_code: str,
        question_type: str,
        ai_marks: float,
        max_marks: float
    ) -> float:
        """
        Get AI marks adjusted based on learned patterns
        
        Args:
            course_code: Course code
            question_type: Question type
            ai_marks: Original AI marks
            max_marks: Maximum marks
            
        Returns:
            Adjusted marks
        """
        if course_code not in self.patterns["courses"]:
            return ai_marks
        
        strictness = self.patterns["courses"][course_code].get("strictness_factor", 1.0)
        
        # Apply strictness factor
        adjusted = ai_marks * strictness
        
        # Ensure within bounds
        adjusted = max(0, min(adjusted, max_marks))
        
        return round(adjusted, 1)
    
    def get_keyword_weight(self, keyword: str, course_code: str = "") -> float:
        """
        Get learned weight for a keyword
        
        Args:
            keyword: Keyword to check
            course_code: Optional course code for course-specific weights
            
        Returns:
            Weight (1.0 = normal, >1.0 = more important, <1.0 = less important)
        """
        key = f"{course_code}:{keyword}" if course_code else keyword
        return self.patterns["keyword_weights"].get(key, 1.0)
    
    def update_keyword_weight(
        self,
        keyword: str,
        importance: float,
        course_code: str = ""
    ):
        """
        Update keyword importance based on faculty feedback
        
        Args:
            keyword: Keyword
            importance: Importance weight
            course_code: Optional course code
        """
        key = f"{course_code}:{keyword}" if course_code else keyword
        self.patterns["keyword_weights"][key] = importance
        self._save_patterns()
    
    def get_marking_insights(self, course_code: str) -> Dict:
        """
        Get insights about marking patterns for a course
        
        Args:
            course_code: Course code
            
        Returns:
            Insights dictionary
        """
        if course_code not in self.patterns["courses"]:
            return {
                "adjustments_count": 0,
                "avg_difference": 0.0,
                "strictness_factor": 1.0,
                "recommendation": "No data yet. System will learn as faculty reviews answers."
            }
        
        course_data = self.patterns["courses"][course_code]
        adjustments = course_data["adjustments"]
        
        # Analyze patterns
        total_adjustments = len(adjustments)
        avg_diff = course_data.get("avg_difference", 0.0)
        strictness = course_data.get("strictness_factor", 1.0)
        
        # Generate recommendation
        if avg_diff > 1.0:
            recommendation = "Faculty tends to be more lenient. AI will adjust marks upward."
        elif avg_diff < -1.0:
            recommendation = "Faculty tends to be stricter. AI will adjust marks downward."
        else:
            recommendation = "AI marking aligns well with faculty expectations."
        
        return {
            "adjustments_count": total_adjustments,
            "avg_difference": round(avg_diff, 2),
            "strictness_factor": round(strictness, 2),
            "recommendation": recommendation,
            "recent_adjustments": adjustments[-5:] if adjustments else []
        }


class FeedbackGenerator:
    """Generates comprehensive feedback for every answer sheet"""
    
    def __init__(self, pattern_learner: Optional[MarkingPatternLearner] = None):
        """
        Initialize feedback generator
        
        Args:
            pattern_learner: Optional pattern learner for personalized feedback
        """
        self.pattern_learner = pattern_learner
    
    def generate_answer_feedback(
        self,
        question: Dict,
        student_answer: Dict,
        evaluation_result: Dict,
        model_answer: Dict = None
    ) -> Dict:
        """
        Generate detailed feedback for a single answer
        
        Args:
            question: Question dictionary
            student_answer: Student answer dictionary
            evaluation_result: Evaluation result
            model_answer: Optional model answer
            
        Returns:
            Comprehensive feedback dictionary
        """
        feedback = {
            "question_number": question.get("number"),
            "question_text": question.get("text", "")[:100] + "...",  # Truncate for display
            "marks_awarded": evaluation_result.get("marks_awarded", 0),
            "max_marks": question.get("max_marks", 0),
            "percentage": round((evaluation_result.get("marks_awarded", 0) / max(question.get("max_marks", 1), 1)) * 100, 1),
            "evaluation_type": student_answer.get("content_type", "text"),
            "ocr_confidence": student_answer.get("ocr_confidence", 0),
            "needs_review": student_answer.get("needs_review", False),
            "review_reason": student_answer.get("review_reason", ""),
            "detailed_feedback": evaluation_result.get("feedback", ""),
            "strengths": evaluation_result.get("strengths", []),
            "improvements": evaluation_result.get("improvements", []),
            "keywords_matched": evaluation_result.get("keywords_matched", 0),
            "total_keywords": evaluation_result.get("total_keywords", 0),
            "suggestions": self._generate_suggestions(evaluation_result, question)
        }
        
        # Add type-specific feedback
        if student_answer.get("content_type") == "math":
            feedback["step_analysis"] = {
                "correct_steps": evaluation_result.get("correct_steps", 0),
                "total_steps": evaluation_result.get("total_steps", 0),
                "final_answer_correct": evaluation_result.get("final_answer_correct", False),
                "step_breakdown": evaluation_result.get("step_breakdown", "")
            }
        
        elif student_answer.get("content_type") == "code":
            feedback["code_analysis"] = {
                "logic_score": evaluation_result.get("logic_score", 0),
                "approach_correct": evaluation_result.get("approach_correct", "Unknown"),
                "edge_cases": evaluation_result.get("edge_cases", "")
            }
        
        elif student_answer.get("content_type") == "diagram":
            feedback["diagram_analysis"] = {
                "matched_components": evaluation_result.get("matched_components", []),
                "missing_components": evaluation_result.get("missing_components", []),
                "match_percentage": evaluation_result.get("match_percentage", 0)
            }
        
        return feedback
    
    def _generate_suggestions(self, evaluation_result: Dict, question: Dict) -> List[str]:
        """Generate actionable suggestions for improvement"""
        suggestions = []
        
        marks_percentage = (evaluation_result.get("marks_awarded", 0) / max(question.get("max_marks", 1), 1)) * 100
        
        if marks_percentage < 40:
            suggestions.append("Review fundamental concepts for this topic")
            suggestions.append("Practice similar problems to improve understanding")
        elif marks_percentage < 70:
            suggestions.append("Good attempt, but more detail needed")
            suggestions.append("Focus on covering all key concepts")
        else:
            suggestions.append("Excellent work! Minor improvements possible")
        
        # Add keyword-based suggestions
        keywords_matched = evaluation_result.get("keywords_matched", 0)
        total_keywords = evaluation_result.get("total_keywords", 1)
        
        if keywords_matched < total_keywords * 0.5:
            suggestions.append(f"Cover more key concepts ({keywords_matched}/{total_keywords} mentioned)")
        
        return suggestions
    
    def generate_sheet_summary(
        self,
        student_exam: Dict,
        all_answers_feedback: List[Dict]
    ) -> Dict:
        """
        Generate overall summary for entire answer sheet
        
        Args:
            student_exam: Student exam dictionary
            all_answers_feedback: List of feedback for all answers
            
        Returns:
            Summary dictionary
        """
        total_marks = student_exam.get("total_obtained", 0)
        max_marks = student_exam.get("total_max", 0)
        percentage = round((total_marks / max(max_marks, 1)) * 100, 1)
        
        # Count by performance level
        excellent = sum(1 for f in all_answers_feedback if f["percentage"] >= 80)
        good = sum(1 for f in all_answers_feedback if 60 <= f["percentage"] < 80)
        average = sum(1 for f in all_answers_feedback if 40 <= f["percentage"] < 60)
        poor = sum(1 for f in all_answers_feedback if f["percentage"] < 40)
        
        # Count flagged for review
        flagged_count = sum(1 for f in all_answers_feedback if f["needs_review"])
        
        # Overall assessment
        if percentage >= 80:
            overall_assessment = "Excellent"
        elif percentage >= 60:
            overall_assessment = "Good"
        elif percentage >= 40:
            overall_assessment = "Average"
        else:
            overall_assessment = "Needs Improvement"
        
        return {
            "student_name": student_exam.get("name", ""),
            "roll_number": student_exam.get("roll_number", ""),
            "total_marks": total_marks,
            "max_marks": max_marks,
            "percentage": percentage,
            "overall_assessment": overall_assessment,
            "performance_breakdown": {
                "excellent": excellent,
                "good": good,
                "average": average,
                "poor": poor
            },
            "flagged_for_review": flagged_count,
            "total_questions": len(all_answers_feedback),
            "strengths": self._identify_strengths(all_answers_feedback),
            "areas_for_improvement": self._identify_improvements(all_answers_feedback),
            "faculty_action_required": flagged_count > 0
        }
    
    def _identify_strengths(self, all_feedback: List[Dict]) -> List[str]:
        """Identify overall strengths across all answers"""
        strengths = []
        
        # Find questions with high scores
        high_scoring = [f for f in all_feedback if f["percentage"] >= 80]
        
        if len(high_scoring) > len(all_feedback) * 0.5:
            strengths.append("Strong overall understanding of course material")
        
        # Check for specific question types
        question_types = {}
        for f in all_feedback:
            qtype = f["evaluation_type"]
            if qtype not in question_types:
                question_types[qtype] = []
            question_types[qtype].append(f["percentage"])
        
        for qtype, scores in question_types.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 75:
                strengths.append(f"Excellent performance in {qtype} questions")
        
        return strengths[:3]  # Top 3 strengths
    
    def _identify_improvements(self, all_feedback: List[Dict]) -> List[str]:
        """Identify areas needing improvement"""
        improvements = []
        
        # Find questions with low scores
        low_scoring = [f for f in all_feedback if f["percentage"] < 50]
        
        if len(low_scoring) > 0:
            improvements.append(f"Focus on {len(low_scoring)} questions that need more attention")
        
        # Check keyword coverage
        total_keywords_matched = sum(f.get("keywords_matched", 0) for f in all_feedback)
        total_keywords = sum(f.get("total_keywords", 1) for f in all_feedback)
        
        if total_keywords > 0 and (total_keywords_matched / total_keywords) < 0.6:
            improvements.append("Cover more key concepts in answers")
        
        # Check for specific weak areas
        question_types = {}
        for f in all_feedback:
            qtype = f["evaluation_type"]
            if qtype not in question_types:
                question_types[qtype] = []
            question_types[qtype].append(f["percentage"])
        
        for qtype, scores in question_types.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 50:
                improvements.append(f"Practice more {qtype} questions")
        
        return improvements[:3]  # Top 3 improvements


# Convenience functions
def create_pattern_learner(storage_path: str = "./marking_patterns") -> MarkingPatternLearner:
    """Create marking pattern learner instance"""
    return MarkingPatternLearner(storage_path)


def create_feedback_generator(pattern_learner: Optional[MarkingPatternLearner] = None) -> FeedbackGenerator:
    """Create feedback generator instance"""
    return FeedbackGenerator(pattern_learner)
