"""
Module 2: Multi-Engine OCR System
Handles text extraction using Google Cloud Vision and Mathpix for equations
"""
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import re
import base64


class OCRResult:
    """Container for OCR results with confidence scores"""
    
    def __init__(self, text: str, confidence: float, word_confidences: List[float] = None):
        self.text = text
        self.confidence = confidence
        self.word_confidences = word_confidences or []
    
    def __repr__(self):
        return f"OCRResult(text='{self.text[:50]}...', confidence={self.confidence:.2f})"


class OCREngine(ABC):
    """Base class for OCR engines"""
    
    @abstractmethod
    def extract_text(self, image: np.ndarray) -> OCRResult:
        """Extract text from image"""
        pass


class GoogleVisionOCR(OCREngine):
    """Google Cloud Vision API for handwriting OCR"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google Cloud Vision OCR
        
        Args:
            api_key: Google Cloud Vision API key
        """
        self.api_key = api_key
        self.client = None
        
        if api_key:
            try:
                from google.cloud import vision
                import os
                
                # Set API key as environment variable
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = api_key
                self.client = vision.ImageAnnotatorClient()
            except ImportError:
                print("Warning: google-cloud-vision not installed")
            except Exception as e:
                print(f"Warning: Could not initialize Google Vision: {e}")
    
    def extract_text(self, image: np.ndarray) -> OCRResult:
        """
        Extract text using Google Cloud Vision
        
        Args:
            image: Input image as numpy array
            
        Returns:
            OCRResult with text and confidence
        """
        if not self.client:
            # Fallback to mock OCR for development
            return self._mock_ocr(image)
        
        try:
            from google.cloud import vision
            
            # Convert numpy array to bytes
            success, encoded_image = cv2.imencode('.png', image)
            if not success:
                raise Exception("Failed to encode image")
            
            content = encoded_image.tobytes()
            
            # Create vision image
            vision_image = vision.Image(content=content)
            
            # Perform document text detection
            response = self.client.document_text_detection(image=vision_image)
            
            if response.error.message:
                raise Exception(f"API Error: {response.error.message}")
            
            # Extract text and confidence
            full_text = response.full_text_annotation.text
            
            # Calculate average confidence from pages
            confidences = []
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    confidences.append(block.confidence)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                word_confidences=confidences
            )
        
        except Exception as e:
            print(f"Google Vision OCR error: {e}")
            return self._mock_ocr(image)
    
    def _mock_ocr(self, image: np.ndarray) -> OCRResult:
        """Mock OCR for development/testing"""
        return OCRResult(
            text="[Mock OCR] This is sample extracted text from the image. Configure Google Cloud Vision API for actual OCR.",
            confidence=0.85
        )


class MathpixOCR(OCREngine):
    """Mathpix API for math equation OCR"""
    
    def __init__(self, app_id: Optional[str] = None, app_key: Optional[str] = None):
        """
        Initialize Mathpix OCR
        
        Args:
            app_id: Mathpix App ID
            app_key: Mathpix App Key
        """
        self.app_id = app_id
        self.app_key = app_key
    
    def extract_text(self, image: np.ndarray) -> OCRResult:
        """
        Extract math equations using Mathpix
        
        Args:
            image: Input image as numpy array
            
        Returns:
            OCRResult with LaTeX equations
        """
        if not self.app_id or not self.app_key:
            return self._mock_math_ocr(image)
        
        try:
            import requests
            
            # Convert image to base64
            success, encoded_image = cv2.imencode('.png', image)
            if not success:
                raise Exception("Failed to encode image")
            
            image_base64 = base64.b64encode(encoded_image.tobytes()).decode()
            
            # Mathpix API request
            url = "https://api.mathpix.com/v3/text"
            headers = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "Content-type": "application/json"
            }
            data = {
                "src": f"data:image/png;base64,{image_base64}",
                "formats": ["text", "latex_styled"],
                "data_options": {
                    "include_asciimath": True,
                    "include_latex": True
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            result = response.json()
            
            if "error" in result:
                raise Exception(f"Mathpix error: {result['error']}")
            
            latex_text = result.get("latex_styled", result.get("text", ""))
            confidence = result.get("latex_confidence", 0.8)
            
            return OCRResult(
                text=latex_text,
                confidence=confidence
            )
        
        except Exception as e:
            print(f"Mathpix OCR error: {e}")
            return self._mock_math_ocr(image)
    
    def _mock_math_ocr(self, image: np.ndarray) -> OCRResult:
        """Mock math OCR for development/testing"""
        return OCRResult(
            text="[Mock Math OCR] \\int_{0}^{\\infty} x^2 dx = \\frac{x^3}{3}",
            confidence=0.80
        )


class HybridOCR:
    """
    Hybrid OCR system that routes content to appropriate engine
    Combines Google Vision (text) and Mathpix (equations)
    """
    
    def __init__(
        self,
        google_api_key: Optional[str] = None,
        mathpix_app_id: Optional[str] = None,
        mathpix_app_key: Optional[str] = None
    ):
        """Initialize hybrid OCR with both engines"""
        self.text_ocr = GoogleVisionOCR(google_api_key)
        self.math_ocr = MathpixOCR(mathpix_app_id, mathpix_app_key)
    
    def detect_content_type(self, image: np.ndarray) -> str:
        """
        Detect if image contains primarily text or math
        
        Args:
            image: Input image
            
        Returns:
            'text', 'math', or 'mixed'
        """
        # Simple heuristic: check for math symbols
        # In production, could use ML model for better detection
        
        # First, do quick OCR
        result = self.text_ocr.extract_text(image)
        text = result.text.lower()
        
        # Count math indicators
        math_indicators = [
            r'\int', r'\sum', r'\frac', r'\sqrt',  # LaTeX
            '∫', '∑', '√', '∂', '∆',  # Unicode math symbols
            '=', '+', '-', '×', '÷', '^',  # Operators
        ]
        
        math_count = sum(1 for indicator in math_indicators if indicator in text)
        
        # Heuristic thresholds
        if math_count > 5:
            return 'math'
        elif math_count > 2:
            return 'mixed'
        else:
            return 'text'
    
    def extract_text_with_confidence(
        self,
        image: np.ndarray,
        content_type: Optional[str] = None
    ) -> OCRResult:
        """
        Extract text using appropriate engine based on content type
        
        Args:
            image: Input image
            content_type: Optional content type ('text', 'math', 'mixed')
                         If None, will auto-detect
            
        Returns:
            OCRResult with extracted text and confidence
        """
        if content_type is None:
            content_type = self.detect_content_type(image)
        
        if content_type == 'math':
            return self.math_ocr.extract_text(image)
        elif content_type == 'mixed':
            # Use both engines and combine results
            text_result = self.text_ocr.extract_text(image)
            math_result = self.math_ocr.extract_text(image)
            
            # Combine texts
            combined_text = f"{text_result.text}\n[Math]: {math_result.text}"
            avg_confidence = (text_result.confidence + math_result.confidence) / 2
            
            return OCRResult(
                text=combined_text,
                confidence=avg_confidence
            )
        else:
            return self.text_ocr.extract_text(image)
    
    def extract_math_equations(self, image: np.ndarray) -> List[str]:
        """
        Extract only math equations from image
        
        Args:
            image: Input image
            
        Returns:
            List of LaTeX equations
        """
        result = self.math_ocr.extract_text(image)
        
        # Split by common equation delimiters
        equations = re.split(r'[\n;,]', result.text)
        equations = [eq.strip() for eq in equations if eq.strip()]
        
        return equations


# Convenience function
def create_ocr_engine(
    google_api_key: Optional[str] = None,
    mathpix_app_id: Optional[str] = None,
    mathpix_app_key: Optional[str] = None
) -> HybridOCR:
    """
    Create hybrid OCR engine
    
    Args:
        google_api_key: Google Cloud Vision API key
        mathpix_app_id: Mathpix App ID
        mathpix_app_key: Mathpix App Key
        
    Returns:
        HybridOCR instance
    """
    return HybridOCR(google_api_key, mathpix_app_id, mathpix_app_key)
