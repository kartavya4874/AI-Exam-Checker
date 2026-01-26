"""
Module 4: Answer Key Processor
Extracts model answers and uses AI to generate keywords and marking schemes
"""
import re
from typing import Dict, List, Optional
from ...services.ocr.ocr_engine import HybridOCR
from ...services.evaluators.ai_client import AIEvaluator


class AnswerKeyProcessor:
    """Processes answer keys to extract model answers and generate marking schemes"""
    
    def __init__(self, ocr_engine: HybridOCR, ai_evaluator: AIEvaluator):
        """
        Initialize answer key processor
        
        Args:
            ocr_engine: OCR engine for text extraction
            ai_evaluator: AI evaluator for keyword extraction
        """
        self.ocr = ocr_engine
        self.ai = ai_evaluator
    
    def extract_model_answers(
        self,
        ocr_text: str,
        questions: List[Dict]
    ) -> List[Dict]:
        """
        Extract model answers matching questions
        
        Args:
            ocr_text: OCR text from answer key
            questions: List of questions from question paper
            
        Returns:
            List of model answer dictionaries
        """
        model_answers = []
        
        # Create question number to ID mapping
        question_map = {q["number"]: q for q in questions}
        
        # Extract answers using similar patterns as questions
        patterns = [
            r'(?:Ans|Answer|A)\.?\s*(\d+[a-z]?)\s*[:\.\)]\s*(.+?)(?=(?:Ans|Answer|A)\.?\s*\d+|$)',
            r'Q\.?\s*(\d+[a-z]?)\s*[:\.\)]\s*(.+?)(?=Q\.?\s*\d+|$)',
            r'^(\d+[a-z]?)\s*[\.\)]\s*(.+?)(?=^\d+[a-z]?[\.\)]|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, ocr_text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if matches:
                for number, text in matches:
                    if number in question_map:
                        question = question_map[number]
                        model_answer = {
                            "question_id": question.get("id"),
                            "question_number": number,
                            "text": text.strip(),
                            "keywords": [],
                            "marking_scheme": {}
                        }
                        model_answers.append(model_answer)
                break
        
        return model_answers
    
    def extract_keywords_with_ai(self, model_answer_text: str, question_text: str = "") -> List[str]:
        """
        Use AI to extract key concepts from model answer
        
        Args:
            model_answer_text: Model answer text
            question_text: Optional question text for context
            
        Returns:
            List of keywords/key concepts
        """
        prompt = f"""Extract the KEY CONCEPTS and KEYWORDS from this model answer that students MUST mention to get full marks.

Question: {question_text if question_text else "Not provided"}

Model Answer:
{model_answer_text}

Instructions:
1. Identify 5-10 essential concepts/keywords
2. Focus on technical terms, important facts, and core ideas
3. These will be used to evaluate student answers

Provide ONLY a comma-separated list of keywords, nothing else.
Example: photosynthesis, chlorophyll, light energy, glucose, carbon dioxide
"""
        
        response = self.ai.generate(prompt, max_tokens=500)
        
        # Parse keywords
        keywords = [k.strip() for k in response.split(',') if k.strip()]
        
        # Clean up any extra text
        keywords = [k for k in keywords if len(k) < 50]  # Remove overly long items
        
        return keywords[:10]  # Limit to 10 keywords
    
    def create_marking_scheme(
        self,
        model_answer_text: str,
        keywords: List[str],
        max_marks: int,
        question_text: str = ""
    ) -> Dict:
        """
        Generate AI-powered marking scheme
        
        Args:
            model_answer_text: Model answer
            keywords: Extracted keywords
            max_marks: Maximum marks for question
            question_text: Optional question text
            
        Returns:
            Marking scheme dictionary
        """
        prompt = f"""Create a detailed marking scheme for this question.

Question: {question_text if question_text else "Not provided"}
Maximum Marks: {max_marks}

Model Answer:
{model_answer_text}

Key Concepts:
{', '.join(keywords)}

Create a marking scheme that specifies:
1. How marks should be distributed across concepts
2. Partial credit guidelines
3. What constitutes a complete answer

Format as JSON:
{{
  "full_marks_criteria": "Description of what gets full marks",
  "partial_credit": [
    {{"marks": X, "criteria": "What gets X marks"}},
    ...
  ],
  "deductions": ["Common mistakes that lose marks"]
}}
"""
        
        response = self.ai.generate(prompt, max_tokens=1000)
        
        # Try to extract JSON
        try:
            import json
            # Find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                scheme = json.loads(json_match.group(0))
                return scheme
        except:
            pass
        
        # Fallback scheme
        return {
            "full_marks_criteria": f"Complete answer covering all {len(keywords)} key concepts",
            "partial_credit": [
                {"marks": max_marks * 0.7, "criteria": "Covers most key concepts"},
                {"marks": max_marks * 0.5, "criteria": "Covers some key concepts"},
            ],
            "deductions": ["Missing key concepts", "Factual errors"]
        }
    
    def process_answer_key(
        self,
        images: List,
        questions: List[Dict],
        answer_key_id: int
    ) -> List[Dict]:
        """
        Complete processing of answer key
        
        Args:
            images: Preprocessed images of answer key
            questions: List of questions from question paper
            answer_key_id: Database ID of answer key
            
        Returns:
            List of model answers with keywords and schemes
        """
        # OCR all pages
        full_text = ""
        for image in images:
            result = self.ocr.extract_text_with_confidence(image)
            full_text += result.text + "\n\n"
        
        # Extract model answers
        model_answers = self.extract_model_answers(full_text, questions)
        
        # Process each model answer
        for ma in model_answers:
            # Find corresponding question
            question = next((q for q in questions if q["number"] == ma["question_number"]), None)
            
            if question:
                # Extract keywords using AI
                ma["keywords"] = self.extract_keywords_with_ai(
                    ma["text"],
                    question.get("text", "")
                )
                
                # Create marking scheme
                ma["marking_scheme"] = self.create_marking_scheme(
                    ma["text"],
                    ma["keywords"],
                    question.get("max_marks", 10),
                    question.get("text", "")
                )
                
                ma["answer_key_id"] = answer_key_id
        
        return model_answers


# Convenience function
def process_answer_key(
    images: List,
    questions: List[Dict],
    answer_key_id: int,
    ocr_engine: HybridOCR,
    ai_evaluator: AIEvaluator
) -> List[Dict]:
    """
    Quick answer key processing
    
    Args:
        images: Preprocessed images
        questions: Questions from question paper
        answer_key_id: Database ID
        ocr_engine: OCR engine
        ai_evaluator: AI evaluator
        
    Returns:
        List of model answers with keywords and schemes
    """
    processor = AnswerKeyProcessor(ocr_engine, ai_evaluator)
    return processor.process_answer_key(images, questions, answer_key_id)
