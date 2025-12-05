import mss
import mss.tools
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import tempfile
import os

# Try to import opencv for enhanced preprocessing (optional)
try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

# Optional: set tesseract path if not in PATH (Windows example)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def capture_and_ocr(region=None):
    """
    Captures a screen region and returns extracted text.
    region: dict like {"top": y, "left": x, "width": w, "height": h}
    If None, captures primary monitor's full screen.
    """
    with mss.mss() as sct:
        if region is None:
            region = sct.monitors[1]  # Primary monitor

        # Capture screen
        screenshot = sct.grab(region)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        
        # Optional: improve OCR with basic image preprocessing
        if HAS_OPENCV:
            # Use OpenCV for advanced preprocessing
            open_cv_image = np.array(img)
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Convert back to PIL Image for pytesseract (ensure L mode for grayscale)
            img = Image.fromarray(thresh).convert('L')
        else:
            # Use PIL for basic preprocessing (fallback)
            img = img.convert('L')  # Convert to grayscale
            img = img.filter(ImageFilter.MedianFilter())  # Reduce noise
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)  # Increase contrast
        
        # Extract text - use temporary file for compatibility with older Tesseract versions
        # This avoids PNG library issues in older Tesseract builds
        try:
            # Try direct method first (works with newer Tesseract)
            text = pytesseract.image_to_string(img, lang='eng')
        except Exception:
            # Fallback: save to temporary file (works with older Tesseract versions)
            with tempfile.NamedTemporaryFile(suffix='.tiff', delete=False) as tmp_file:
                img.save(tmp_file.name, format='TIFF')
                try:
                    text = pytesseract.image_to_string(tmp_file.name, lang='eng')
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(tmp_file.name)
                    except:
                        pass
        return text.strip()

if __name__ == "__main__":
    # 🔍 ADJUST THIS TO CAPTURE YOUR QUIZ/INTERVIEW WINDOW
    # Example: capture a 800x400 area starting at (200, 200)
    target_region = {"top": 200, "left": 200, "width": 800, "height": 400}
    
    print("Capturing screen region...")
    extracted_text = capture_and_ocr(target_region)
    
    print("\n📄 Extracted Text:\n")
    print(extracted_text if extracted_text else "[No text detected]")

