"""
Module 5: Student Answer Sheet Processor
Handles header extraction, content detection, and smart question mapping
"""
import re
from typing import Dict, List, Optional, Tuple
import numpy as np
from ...services.ocr.ocr_engine import HybridOCR
from ...services.preprocessor.pdf_processor import DocumentPreprocessor


class StudentAnswerSheetProcessor:
    """Processes student answer sheets with smart question mapping"""
    
    def __init__(self, ocr_engine: HybridOCR, preprocessor: DocumentPreprocessor):
        """
        Initialize student answer sheet processor
        
        Args:
            ocr_engine: OCR engine
            preprocessor: Document preprocessor
        """
        self.ocr = ocr_engine
        self.preprocessor = preprocessor
    
    def extract_header_info(self, first_page_image: np.ndarray) -> Dict:
        """
        Extract student information from header (top 15% of first page)
        
        Args:
            first_page_image: First page image
            
        Returns:
            Dictionary with student info
        """
        # Extract top 15% of page
        header_region = self.preprocessor.extract_region(
            first_page_image,
            top_percent=0,
            bottom_percent=15
        )
        
        # OCR header
        result = self.ocr.extract_text_with_confidence(header_region)
        header_text = result.text
        
        # Extract information using regex
        info = {
            "roll_number": self._extract_roll_number(header_text),
            "name": self._extract_name(header_text),
            "course_code": self._extract_course_code(header_text),
            "date": self._extract_date(header_text)
        }
        
        return info
    
    def _extract_roll_number(self, text: str) -> str:
        """Extract roll number from header text"""
        patterns = [
            r'Roll\s*(?:No|Number|#)[:\s]*([A-Z0-9]+)',
            r'Roll[:\s]*([A-Z0-9]+)',
            r'ID[:\s]*([A-Z0-9]+)',
            r'\b([A-Z]{2,}\d{4,})\b',  # Pattern like CS2021001
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "UNKNOWN"
    
    def _extract_name(self, text: str) -> str:
        """Extract student name from header text"""
        patterns = [
            r'Name[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Student[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "UNKNOWN"
    
    def _extract_course_code(self, text: str) -> str:
        """Extract course code from header text"""
        patterns = [
            r'Course[:\s]*([A-Z]{2,}\d{3,})',
            r'Subject[:\s]*([A-Z]{2,}\d{3,})',
            r'\b([A-Z]{2,}\d{3,})\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "UNKNOWN"
    
    def _extract_date(self, text: str) -> str:
        """Extract date from header text"""
        patterns = [
            r'Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ""
    
    def detect_content_types(self, image: np.ndarray) -> str:
        """
        Detect content type in image region
        
        Args:
            image: Image region
            
        Returns:
            Content type (text, math, code, diagram, mcq, mixed)
        """
        # Use OCR's content detection
        return self.ocr.detect_content_type(image)
    
    def scan_all_question_numbers(self, full_text: str) -> List[Tuple[str, int]]:
        """
        Scan entire document to find ALL question numbers and their positions
        CRITICAL: This prevents marking questions as "not attempted" when they're out of order
        
        Args:
            full_text: Complete OCR text from all pages
            
        Returns:
            List of (question_number, position) tuples
        """
        question_positions = []
        
        # Question number patterns
        patterns = [
            r'Q\.?\s*(\d+[a-z]?)\s*[:\.\)]',  # Q1: or Q.1)
            r'Question\s+(\d+[a-z]?)\s*[:\.\)]',  # Question 1:
            r'^\s*(\d+[a-z]?)\s*[\.\)]',  # 1. or 1) at start of line
            r'\((\d+[a-z]?)\)',  # (1) or (1a)
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, full_text, re.MULTILINE | re.IGNORECASE):
                question_num = match.group(1)
                position = match.start()
                question_positions.append((question_num, position))
        
        # Remove duplicates, keep first occurrence
        seen = set()
        unique_positions = []
        for qnum, pos in question_positions:
            if qnum not in seen:
                seen.add(qnum)
                unique_positions.append((qnum, pos))
        
        # Sort by position (not by question number!)
        unique_positions.sort(key=lambda x: x[1])
        
        return unique_positions
    
    def map_answers_to_questions(
        self,
        full_text: str,
        questions: List[Dict]
    ) -> List[Dict]:
        """
        Map student answers to questions (handles out-of-order answers)
        
        Args:
            full_text: Complete OCR text
            questions: List of questions from question paper
            
        Returns:
            List of answer dictionaries
        """
        # Scan for all question numbers
        question_positions = self.scan_all_question_numbers(full_text)
        
        # Create mapping of question numbers to questions
        question_map = {q["number"]: q for q in questions}
        
        answers = []
        
        # Extract answer text between question markers
        for i, (qnum, start_pos) in enumerate(question_positions):
            # Find end position (next question or end of text)
            if i < len(question_positions) - 1:
                end_pos = question_positions[i + 1][1]
            else:
                end_pos = len(full_text)
            
            # Extract answer text
            answer_text = full_text[start_pos:end_pos].strip()
            
            # Remove question number from answer text
            answer_text = re.sub(r'^Q\.?\s*\d+[a-z]?[:\.\)]\s*', '', answer_text, flags=re.IGNORECASE)
            answer_text = re.sub(r'^Question\s+\d+[a-z]?[:\.\)]\s*', '', answer_text, flags=re.IGNORECASE)
            answer_text = re.sub(r'^\s*\d+[a-z]?[\.\)]\s*', '', answer_text)
            
            # Check if question exists in question paper
            if qnum in question_map:
                question = question_map[qnum]
                
                answers.append({
                    "question_id": question.get("id"),
                    "question_number": qnum,
                    "answer_text": answer_text,
                    "is_attempted": len(answer_text.strip()) > 5,  # At least some content
                    "position_in_sheet": i + 1
                })
        
        # Mark questions not found as unattempted
        attempted_numbers = {a["question_number"] for a in answers}
        for question in questions:
            if question["number"] not in attempted_numbers:
                answers.append({
                    "question_id": question.get("id"),
                    "question_number": question["number"],
                    "answer_text": "",
                    "is_attempted": False,
                    "position_in_sheet": -1
                })
        
        return answers
    
    def process_student_answer_sheet(
        self,
        images: List[np.ndarray],
        questions: List[Dict],
        student_exam_id: int
    ) -> Dict:
        """
        Complete processing of student answer sheet
        
        Args:
            images: Preprocessed images of answer sheet
            questions: Questions from question paper
            student_exam_id: Database ID of student exam
            
        Returns:
            Processing result with header info and answers
        """
        # Extract header from first page
        header_info = self.extract_header_info(images[0])
        
        # OCR all pages
        full_text = ""
        for image in images:
            result = self.ocr.extract_text_with_confidence(image)
            full_text += result.text + "\n\n"
        
        # Map answers to questions
        answers = self.map_answers_to_questions(full_text, questions)
        
        # Add student_exam_id to each answer
        for answer in answers:
            answer["student_exam_id"] = student_exam_id
        
        return {
            "header_info": header_info,
            "answers": answers,
            "total_questions": len(questions),
            "attempted_questions": sum(1 for a in answers if a["is_attempted"]),
            "unattempted_questions": sum(1 for a in answers if not a["is_attempted"])
        }


# Convenience function
def process_student_sheet(
    images: List[np.ndarray],
    questions: List[Dict],
    student_exam_id: int,
    ocr_engine: HybridOCR,
    preprocessor: DocumentPreprocessor
) -> Dict:
    """
    Quick student sheet processing
    
    Args:
        images: Preprocessed images
        questions: Questions from question paper
        student_exam_id: Database ID
        ocr_engine: OCR engine
        preprocessor: Document preprocessor
        
    Returns:
        Processing result
    """
    processor = StudentAnswerSheetProcessor(ocr_engine, preprocessor)
    return processor.process_student_answer_sheet(images, questions, student_exam_id)
