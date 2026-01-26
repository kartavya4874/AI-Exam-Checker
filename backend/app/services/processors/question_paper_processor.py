"""
Module 3: Question Paper Processor
Extracts questions, marks allocation, and Bloom's taxonomy from question papers
"""
import re
from typing import Dict, List, Optional, Tuple
from ...services.ocr.ocr_engine import HybridOCR


class QuestionPaperProcessor:
    """Processes question papers to extract structured question data"""
    
    def __init__(self, ocr_engine: HybridOCR):
        """
        Initialize question paper processor
        
        Args:
            ocr_engine: OCR engine for text extraction
        """
        self.ocr = ocr_engine
        
        # Bloom's taxonomy keywords
        self.bloom_keywords = {
            "Remember": ["define", "list", "name", "identify", "recall", "state", "what is"],
            "Understand": ["explain", "describe", "summarize", "interpret", "discuss", "compare"],
            "Apply": ["apply", "demonstrate", "calculate", "solve", "use", "implement"],
            "Analyze": ["analyze", "examine", "differentiate", "distinguish", "investigate"],
            "Evaluate": ["evaluate", "assess", "justify", "critique", "argue", "defend"],
            "Create": ["design", "create", "develop", "formulate", "construct", "propose"]
        }
    
    def extract_questions(self, ocr_text: str) -> List[Dict]:
        """
        Extract questions from OCR text
        
        Args:
            ocr_text: OCR extracted text from question paper
            
        Returns:
            List of question dictionaries
        """
        questions = []
        
        # Question number patterns
        patterns = [
            r'Q\.?\s*(\d+[a-z]?)\s*[:\.\)]\s*(.+?)(?=Q\.?\s*\d+|$)',  # Q1: or Q.1)
            r'Question\s+(\d+[a-z]?)\s*[:\.\)]\s*(.+?)(?=Question\s+\d+|$)',  # Question 1:
            r'^(\d+[a-z]?)\s*[\.\)]\s*(.+?)(?=^\d+[a-z]?[\.\)]|$)',  # 1. or 1)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, ocr_text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if matches:
                for number, text in matches:
                    question = self._parse_question(number, text.strip())
                    if question:
                        questions.append(question)
                break  # Use first matching pattern
        
        return questions
    
    def _parse_question(self, number: str, text: str) -> Optional[Dict]:
        """Parse individual question"""
        
        if not text or len(text) < 5:
            return None
        
        # Extract marks
        marks = self.extract_marks(text)
        
        # Extract Bloom's level
        bloom_level = self.extract_bloom_level(text)
        
        # Detect question type
        question_type = self._detect_question_type(text)
        
        return {
            "number": number,
            "text": text,
            "max_marks": marks,
            "bloom_level": bloom_level,
            "question_type": question_type
        }
    
    def extract_marks(self, question_text: str) -> int:
        """
        Extract marks allocation from question text
        
        Args:
            question_text: Question text
            
        Returns:
            Marks (default: 5 if not found)
        """
        # Patterns for marks
        patterns = [
            r'\[(\d+)\s*marks?\]',  # [5 marks]
            r'\((\d+)\s*marks?\)',  # (5 marks)
            r'Marks?\s*[:\-]\s*(\d+)',  # Marks: 5
            r'(\d+)\s*marks?',  # 5 marks
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question_text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 5  # Default marks
    
    def extract_bloom_level(self, question_text: str) -> str:
        """
        Extract Bloom's taxonomy level from question text
        
        Args:
            question_text: Question text
            
        Returns:
            Bloom's level (Remember, Understand, Apply, etc.)
        """
        text_lower = question_text.lower()
        
        # Check for explicit Bloom's level mention
        for level in self.bloom_keywords.keys():
            if level.lower() in text_lower:
                return level
        
        # Infer from keywords
        for level, keywords in self.bloom_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level
        
        return "Understand"  # Default level
    
    def _detect_question_type(self, text: str) -> str:
        """Detect question type from text"""
        
        text_lower = text.lower()
        
        # MCQ indicators
        if re.search(r'\(a\)|\(b\)|\(c\)|\(d\)', text_lower):
            return "mcq"
        
        # Diagram indicators
        if any(word in text_lower for word in ["draw", "diagram", "sketch", "illustrate", "label"]):
            return "diagram"
        
        # Code indicators
        if any(word in text_lower for word in ["program", "code", "algorithm", "function", "class"]):
            return "code"
        
        # Math indicators
        if any(word in text_lower for word in ["solve", "calculate", "prove", "derive", "integrate"]):
            return "math"
        
        return "text"  # Default
    
    def process_question_paper(
        self,
        images: List,
        question_paper_id: int
    ) -> List[Dict]:
        """
        Complete processing of question paper
        
        Args:
            images: List of preprocessed images
            question_paper_id: Database ID of question paper
            
        Returns:
            List of extracted questions
        """
        # OCR all pages
        full_text = ""
        for image in images:
            result = self.ocr.extract_text_with_confidence(image)
            full_text += result.text + "\n\n"
        
        # Extract questions
        questions = self.extract_questions(full_text)
        
        # Add question_paper_id to each question
        for q in questions:
            q["question_paper_id"] = question_paper_id
        
        return questions


# Convenience function
def process_question_paper(
    images: List,
    question_paper_id: int,
    ocr_engine: HybridOCR
) -> List[Dict]:
    """
    Quick question paper processing
    
    Args:
        images: Preprocessed images
        question_paper_id: Database ID
        ocr_engine: OCR engine instance
        
    Returns:
        List of questions
    """
    processor = QuestionPaperProcessor(ocr_engine)
    return processor.process_question_paper(images, question_paper_id)
