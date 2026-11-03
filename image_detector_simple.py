import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class ImageDetector:
    def __init__(self):
        # Initialize OpenAI client with OpenRouter
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        
    def detect_objects(self, image_path):
        """
        Detect objects in an image using Qwen/Qwen3-VL-235B-A22B-instruct model
        """
        try:
            # Read image file and encode as base64
            with open(image_path, "rb") as image_file:
                import base64
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create the request to OpenRouter
            response = self.client.chat.completions.create(
                model="qwen/qwen3-vl-235B-A22B-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image and list all the objects you can identify in it. For each object, provide:\n1. What the object is\n2. Its location (top, bottom, left, right, center)\n3. Approximate size"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error occurred during object detection: {str(e)}"
    
    def process_multiple_images(self, image_paths):
        """
        Process multiple images and return their detection results
        """
        results = {}
        for path in image_paths:
            results[path] = self.detect_objects(path)
        return results

# Example usage
if __name__ == "__main__":
    # Initialize the image detector
    detector = ImageDetector()
    
    # Print instructions for usage
    print("Image Detection using Qwen/VL-235B-A22B-instruct via OpenRouter")
    print("To use this PoC:")
    print("1. Set your OPENROUTER_API_KEY in a .env file")
    print("2. Place images in the same directory or provide absolute paths")
    print("3. Call detector.detect_objects(image_path) with a valid image path")