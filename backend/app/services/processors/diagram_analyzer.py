"""
Enhanced Diagram Analyzer
Provides visual analysis beyond simple label extraction
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from ...services.ocr.ocr_engine import HybridOCR


class DiagramAnalyzer:
    """Enhanced diagram analysis with visual feature detection"""
    
    def __init__(self, ocr_engine: HybridOCR):
        """
        Initialize diagram analyzer
        
        Args:
            ocr_engine: OCR engine for label extraction
        """
        self.ocr = ocr_engine
    
    def detect_diagram_region(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect the region containing the diagram
        
        Args:
            image: Input image
            
        Returns:
            Bounding box (x, y, w, h) or None
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Find largest contour (likely the diagram)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Only return if it's a significant portion of the image
        image_area = image.shape[0] * image.shape[1]
        diagram_area = w * h
        
        if diagram_area > image_area * 0.1:  # At least 10% of image
            return (x, y, w, h)
        
        return None
    
    def count_components(self, image: np.ndarray) -> int:
        """
        Count distinct visual components in diagram
        
        Args:
            image: Diagram image
            
        Returns:
            Number of components
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Threshold
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Find connected components
        num_labels, labels = cv2.connectedComponents(binary)
        
        # Subtract background
        return num_labels - 1
    
    def detect_arrows(self, image: np.ndarray) -> int:
        """
        Detect arrows in diagram (approximate)
        
        Args:
            image: Diagram image
            
        Returns:
            Estimated number of arrows
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
        
        if lines is None:
            return 0
        
        # Approximate: longer lines might be arrows
        arrow_count = 0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
            if length > 50:  # Significant length
                arrow_count += 1
        
        return arrow_count
    
    def extract_text_regions(self, image: np.ndarray) -> List[str]:
        """
        Extract text from different regions of the diagram
        
        Args:
            image: Diagram image
            
        Returns:
            List of text strings from different regions
        """
        texts = []
        
        # Divide image into grid (e.g., 3x3)
        h, w = image.shape[:2]
        grid_h, grid_w = h // 3, w // 3
        
        for i in range(3):
            for j in range(3):
                y1, y2 = i * grid_h, (i + 1) * grid_h
                x1, x2 = j * grid_w, (j + 1) * grid_w
                
                region = image[y1:y2, x1:x2]
                
                # OCR this region
                result = self.ocr.extract_text_with_confidence(region)
                if result.text.strip():
                    texts.append(result.text.strip())
        
        return texts
    
    def analyze_diagram(
        self,
        image: np.ndarray,
        required_components: List[str] = None
    ) -> Dict:
        """
        Complete diagram analysis
        
        Args:
            image: Diagram image
            required_components: Optional list of required labels
            
        Returns:
            Analysis results dictionary
        """
        # Detect diagram region
        diagram_bbox = self.detect_diagram_region(image)
        
        # Extract diagram region if detected
        if diagram_bbox:
            x, y, w, h = diagram_bbox
            diagram_image = image[y:y+h, x:x+w]
        else:
            diagram_image = image
        
        # Count components
        component_count = self.count_components(diagram_image)
        
        # Detect arrows
        arrow_count = self.detect_arrows(diagram_image)
        
        # Extract text regions
        text_regions = self.extract_text_regions(diagram_image)
        
        # OCR full diagram for labels
        ocr_result = self.ocr.extract_text_with_confidence(diagram_image)
        all_labels = [label.strip() for label in ocr_result.text.split('\n') if label.strip()]
        
        # Check required components if provided
        matched_components = []
        missing_components = []
        
        if required_components:
            all_text_lower = ocr_result.text.lower()
            for component in required_components:
                if component.lower() in all_text_lower:
                    matched_components.append(component)
                else:
                    missing_components.append(component)
        
        return {
            "diagram_detected": diagram_bbox is not None,
            "diagram_bbox": diagram_bbox,
            "component_count": component_count,
            "arrow_count": arrow_count,
            "extracted_labels": all_labels,
            "text_regions": text_regions,
            "ocr_confidence": ocr_result.confidence,
            "matched_components": matched_components,
            "missing_components": missing_components,
            "match_percentage": (len(matched_components) / len(required_components) * 100) if required_components else 0,
            "visual_complexity": self._calculate_complexity(component_count, arrow_count, len(all_labels))
        }
    
    def _calculate_complexity(self, components: int, arrows: int, labels: int) -> str:
        """Calculate visual complexity level"""
        total_elements = components + arrows + labels
        
        if total_elements > 20:
            return "High"
        elif total_elements > 10:
            return "Medium"
        else:
            return "Low"


# Convenience function
def analyze_diagram(
    image: np.ndarray,
    required_components: List[str],
    ocr_engine: HybridOCR
) -> Dict:
    """
    Quick diagram analysis
    
    Args:
        image: Diagram image
        required_components: Required labels/components
        ocr_engine: OCR engine
        
    Returns:
        Analysis results
    """
    analyzer = DiagramAnalyzer(ocr_engine)
    return analyzer.analyze_diagram(image, required_components)
