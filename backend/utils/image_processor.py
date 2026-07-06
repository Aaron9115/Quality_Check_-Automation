# pylint: disable=no-member
import cv2
import numpy as np
from PIL import Image
import io
from typing import Dict, Tuple

class ImageAlignmentChecker:
    """Check logo alignment and overlap with background"""
    
    def check_overlap(self, logo_file, background_file) -> Dict:
        """Detect overlap percentage between logo and background"""
        try:
            # Read images
            logo_img = self._read_image(logo_file)
            bg_img = self._read_image(background_file)
            
            if logo_img is None or bg_img is None:
                return {"error": "Could not read images", "overlap_percent": 0}
            
            # Resize background to match logo if needed
            if logo_img.shape != bg_img.shape:
                bg_img = cv2.resize(bg_img, (logo_img.shape[1], logo_img.shape[0]))  # pylint: disable=no-member
            
            # Convert to grayscale for edge detection
            logo_gray = cv2.cvtColor(logo_img, cv2.COLOR_BGR2GRAY)  # pylint: disable=no-member
            bg_gray = cv2.cvtColor(bg_img, cv2.COLOR_BGR2GRAY)  # pylint: disable=no-member
            
            # Detect edges
            logo_edges = cv2.Canny(logo_gray, 50, 150)  # pylint: disable=no-member
            bg_edges = cv2.Canny(bg_gray, 50, 150)  # pylint: disable=no-member
            
            # Calculate overlap
            overlap = np.logical_and(logo_edges > 0, bg_edges > 0)
            overlap_pixels = np.sum(overlap)
            logo_pixels = np.sum(logo_edges > 0)
            
            overlap_percent = (overlap_pixels / logo_pixels * 100) if logo_pixels > 0 else 0
            
            # Determine status
            if overlap_percent > 50:
                status = "critical overlap detected"
            elif overlap_percent > 20:
                status = "partial overlap detected"
            elif overlap_percent > 5:
                status = "minor overlap detected"
            else:
                status = "no significant overlap"
            
            return {
                "overlap_percent": round(overlap_percent, 2),
                "status": status,
                "suggestion": self._get_suggestion(overlap_percent)
            }
            
        except Exception as e:
            return {"error": str(e), "overlap_percent": 0}
    
    def _read_image(self, file):
        """Read uploaded image file"""
        contents = file.file.read()
        np_array = np.frombuffer(contents, np.uint8)
        return cv2.imdecode(np_array, cv2.IMREAD_COLOR)  # pylint: disable=no-member
    
    def _get_suggestion(self, overlap_percent: float) -> str:
        """Get suggestion based on overlap percentage"""
        if overlap_percent > 50:
            return "Move logo away from background elements or reduce size"
        elif overlap_percent > 20:
            return "Adjust logo position to reduce overlap"
        elif overlap_percent > 5:
            return "Minor overlap - consider repositioning for clarity"
        else:
            return "Logo placement looks good"