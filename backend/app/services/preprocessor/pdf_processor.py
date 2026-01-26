"""
Module 1: Document Preprocessor
Converts PDFs to high-quality images and enhances them for OCR
"""
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from typing import List, Tuple
import os
from pathlib import Path


class DocumentPreprocessor:
    """Handles PDF to image conversion and image enhancement for OCR"""
    
    def __init__(self, dpi: int = 300):
        """
        Initialize preprocessor
        
        Args:
            dpi: Resolution for PDF to image conversion (default: 300)
        """
        self.dpi = dpi
    
    def pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """
        Convert PDF pages to high-quality images
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of images as numpy arrays (one per page)
        """
        try:
            # Convert PDF to PIL images
            pil_images = convert_from_path(pdf_path, dpi=self.dpi)
            
            # Convert PIL images to numpy arrays
            images = []
            for pil_img in pil_images:
                # Convert to RGB if needed
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                # Convert to numpy array
                img_array = np.array(pil_img)
                # Convert RGB to BGR for OpenCV
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                images.append(img_bgr)
            
            return images
        except Exception as e:
            raise Exception(f"Error converting PDF to images: {str(e)}")
    
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """
        Apply image enhancement techniques for better OCR
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Enhanced image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Deskew (correct rotation)
        deskewed = self._deskew_image(denoised)
        
        # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(deskewed)
        
        return enhanced
    
    def binarize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Convert image to binary (black and white) for optimal OCR
        
        Args:
            image: Grayscale image
            
        Returns:
            Binary image
        """
        # Adaptive thresholding works better for varying lighting conditions
        binary = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        return binary
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Correct image rotation/skew
        
        Args:
            image: Input grayscale image
            
        Returns:
            Deskewed image
        """
        # Calculate skew angle
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return image
        
        angle = cv2.minAreaRect(coords)[-1]
        
        # Adjust angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Only deskew if angle is significant (> 0.5 degrees)
        if abs(angle) < 0.5:
            return image
        
        # Rotate image
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image,
            M,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated
    
    def preprocess_document(
        self,
        pdf_path: str,
        output_dir: str = None,
        save_intermediate: bool = False
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Complete preprocessing pipeline: PDF → Images → Enhanced → Binary
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Optional directory to save processed images
            save_intermediate: Whether to save intermediate processing steps
            
        Returns:
            List of tuples (enhanced_image, binary_image) for each page
        """
        # Convert PDF to images
        images = self.pdf_to_images(pdf_path)
        
        processed_images = []
        
        for idx, image in enumerate(images):
            # Enhance image
            enhanced = self.enhance_image(image)
            
            # Binarize image
            binary = self.binarize_image(enhanced)
            
            # Save if requested
            if output_dir and save_intermediate:
                os.makedirs(output_dir, exist_ok=True)
                cv2.imwrite(
                    os.path.join(output_dir, f"page_{idx+1}_enhanced.png"),
                    enhanced
                )
                cv2.imwrite(
                    os.path.join(output_dir, f"page_{idx+1}_binary.png"),
                    binary
                )
            
            processed_images.append((enhanced, binary))
        
        return processed_images
    
    def extract_region(
        self,
        image: np.ndarray,
        top_percent: float = 0,
        bottom_percent: float = 100,
        left_percent: float = 0,
        right_percent: float = 100
    ) -> np.ndarray:
        """
        Extract a specific region from image (useful for header extraction)
        
        Args:
            image: Input image
            top_percent: Top boundary (0-100)
            bottom_percent: Bottom boundary (0-100)
            left_percent: Left boundary (0-100)
            right_percent: Right boundary (0-100)
            
        Returns:
            Cropped image region
        """
        h, w = image.shape[:2]
        
        top = int(h * top_percent / 100)
        bottom = int(h * bottom_percent / 100)
        left = int(w * left_percent / 100)
        right = int(w * right_percent / 100)
        
        return image[top:bottom, left:right]


# Convenience function
def preprocess_pdf(pdf_path: str, dpi: int = 300) -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    Quick preprocessing function
    
    Args:
        pdf_path: Path to PDF file
        dpi: Resolution for conversion
        
    Returns:
        List of (enhanced, binary) image tuples
    """
    preprocessor = DocumentPreprocessor(dpi=dpi)
    return preprocessor.preprocess_document(pdf_path)
