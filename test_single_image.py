import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from image_detector import ImageDetector

# Load environment variables
load_dotenv()

# Create image detector instance
detector = ImageDetector()

# Test with a simple image URL
test_url = "https://www.sportmaster.ru/upload/mdm/media_content/280/172116570299.jpg"
print(f"Testing with URL: {test_url}")

# Test with the demo function
result = detector.detect_objects(test_url, product_id="TEST001")
print(f"Result: {result}")