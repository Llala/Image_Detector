import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from image_detector import ImageDetector

# Load environment variables
load_dotenv()

# Create image detector instance
detector = ImageDetector()

# Test with a simple valid URL that should work (using a public URL for testing)
test_url = "https://upload.wikimedia.org/wikipedia/commons/4/47/American_Eskimo_Dog.jpg"
print(f"Testing with URL: {test_url}")

# Test with the demo function
result = detector.detect_objects(test_url, product_id="TEST001")
print(f"Result type: {type(result)}")
if isinstance(result, dict):
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print("Success! Objects detected:")
        print(result['objects'][:200] + "..." if len(result['objects']) > 200 else result['objects'])
else:
    print(f"Unexpected result: {result}")