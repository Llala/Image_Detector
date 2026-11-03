import os
import sys
import csv
import time
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Добавляем поддержку CORS

PROMPT = """
You are a visual product analysis assistant.

Your task is to identify visually distinctive and
important product features (highlights) in the image.

A highlight is a visible product detail that helps
describe or distinguish the product, such as:
- Logos and branding
- Pockets
- Zippers and fasteners
- Buttons and buckles
- Decorative elements
- Distinctive materials or textures
- Functional design features

Instructions:
1. Identify the main product in the image.
2. Find all clearly visible, meaningful highlights.
3. For each highlight, provide:
   - name: short feature name
   - description: what makes it distinctive
   - bbox: bounding box coordinates
4. Use normalized coordinates from 0 to 1000.
5. Bounding boxes must tightly enclose the
   visible highlight, not the entire product.
6. Do not invent features that are not visible.
7. Do not include background objects.
8. If no highlights are found, return an empty array.
9. Return ONLY valid JSON, without markdown.

JSON format:
{
  "objects": [
    {
      "name": "product_name",
      "highlights": [
        {
          "name": "feature_name",
          "description": "feature_description",
          "bbox": {
            "x_min": 0,
            "y_min": 0,
            "x_max": 0,
            "y_max": 0
          }
        }
      ]
    }
  ]
}

Coordinate rules:
- Origin (0, 0) is the top-left corner.
- (1000, 1000) is the bottom-right corner.
- x_min < x_max
- y_min < y_max
- All coordinates must be between 0 and 1000.
"""


class ImageDetector:
    def __init__(self):
        # Initialize OpenAI client with OpenRouter
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    def detect_objects(self, image_path, product_id=None):
        """
        Detect objects in a local image file using Qwen/Qwen3-VL-235B-A22B-instruct model
        """
        try:
            # Check if the local image file exists
            if not os.path.exists(image_path):
                return {
                    "product_id": product_id,
                    "image_path": image_path,
                    "error": f"Local image file not found: {image_path}"
                }

            # Read and encode the image file to base64
            import base64
            with open(image_path, "rb") as image_file:
                img_str = base64.b64encode(image_file.read()).decode('utf-8')

            # Create the request to OpenRouter with improved instruction for bounding boxes
            response = self.client.chat.completions.create(
                model="qwen/qwen3-vl-235B-A22B-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{PROMPT}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_str}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
            )

            # Parse the response to extract object information including bounding boxes
            response_content = response.choices[0].message.content
            print("response_content", response_content)

            # Обрабатываем текстовый ответ и пытаемся экстрактить JSON
            try:
                import json
                # Ищем начало JSON, если ответ содержит в себе больше текста
                json_start = response_content.find('{')
                json_end = response_content.rfind('}') + 1
                
                if json_start != -1 and json_end != -1:
                    json_string = response_content[json_start:json_end]
                    parsed_response = json.loads(json_string)
                    
                    print("parsed_response", json.dumps(parsed_response, indent=2))
                    
                    # Обработка различный форматов ответа от модели
                    if 'objects' in parsed_response:
                        # Log bbox information if available
                        print("✅ Found 'objects' in response")
                        for obj in parsed_response.get('objects', []):
                            print(f"Object: {obj.get('name', 'Unknown')}")
                            # Обработка обоих форматов: highlights и прямые bbox
                            if 'highlights' in obj and obj['highlights']:
                                for highlight in obj.get('highlights', []):
                                    bbox = highlight.get('bbox')
                                    if bbox:
                                        print(f"  Highlight BBox: x_min={bbox.get('x_min')}, y_min={bbox.get('y_min')}, "
                                              f"x_max={bbox.get('x_max')}, y_max={bbox.get('y_max')}")
                            elif 'bbox' in obj:
                                bbox = obj.get('bbox')
                                if bbox:
                                    print(f"  Direct BBox: x_min={bbox.get('x_min')}, y_min={bbox.get('y_min')}, "
                                          f"x_max={bbox.get('x_max')}, y_max={bbox.get('y_max')}")
                        
                        return {
                            "product_id": product_id,
                            "image_path": image_path,
                            "objects": parsed_response['objects']
                        }
                    else:
                        print("❌ No 'objects' found in response")
                        return {
                            "product_id": product_id,
                            "image_path": image_path,
                            "objects": [],
                            "raw_response": response_content
                        }
                else:
                    print("❌ Could not extract JSON from response")
                    return {
                        "product_id": product_id,
                        "image_path": image_path,
                        "objects": [],
                        "raw_response": response_content
                    }
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
                print(f"Raw content length: {len(response_content)}")
                print(f"Raw content preview: {response_content[:500]}")
                return {
                    "product_id": product_id,
                    "image_path": image_path,
                    "objects": [],
                    "raw_response": response_content
                }

        except Exception as e:
            error_msg = f"Error occurred during object detection: {str(e)}"
            return {
                "product_id": product_id,
                "image_path": image_path,
                "error": error_msg
            }

    def process_product_images(self, product_id):
        """
        Process all images associated with a product
        """
        # Read products.csv to get product information
        products = {}
        try:
            # Using utf-8-sig to handle BOM in CSV files
            with open("products.csv", 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    products[row['product_id']] = {
                        'name': row['name'],
                        'description': row['description']
                    }
        except Exception as e:
            return {"error": f"Error reading products.csv: {str(e)}"}

        # Read images.csv to get image information
        product_images = {}
        try:
            # Using utf-8-sig to handle BOM in CSV files
            with open("images.csv", 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    image_product_id = row['product_id']
                    if image_product_id not in product_images:
                        product_images[image_product_id] = []
                    product_images[image_product_id].append({
                        'order': int(row['image_order']),
                        'url': row['image_url']
                    })
        except Exception as e:
            return {"error": f"Error reading images.csv: {str(e)}"}

        # Process images for the specific product
        results = []
        processed_count = 0
        image_paths = []

        if product_id in product_images:
            images = sorted(product_images[product_id], key=lambda x: x['order'])

            # Process all images
            for img_info in images:
                # Extract filename from image_url (last part after /)
                image_filename = img_info['url'].split('/')[-1]
                image_path = os.path.join("Pics", image_filename)
                image_paths.append(image_path)

                # Check if file exists
                if os.path.exists(image_path):
                    # Process the local image file with Qwen model
                    result = self.detect_objects(image_path, product_id)
                    results.append(result)
                    processed_count += 1
                else:
                    # File doesn't exist, return error
                    results.append({
                        "product_id": product_id,
                        "image_path": image_path,
                        "error": f"Image file not found: {image_path}"
                    })
        else:
            # Если продукт не найден в images.csv, но есть в products.csv
            # Проверим, есть ли файлы в Pics с соответствующим префиксом
            # Поиск файлов в Pics, которые могут быть связаны с этим product_id
            pics_files = []
            for filename in os.listdir("Pics"):
                if filename.startswith(product_id):
                    pics_files.append(filename)

            # Если найдены файлы в Pics, попробуем обработать их
            if pics_files:
                for filename in sorted(pics_files):
                    image_path = os.path.join("Pics", filename)
                    result = self.detect_objects(image_path, product_id)
                    results.append(result)
                    processed_count += 1
                    image_paths.append(image_path)

        # Формируем финальный ответ с объектами
        # Сохраняем структуру, которая ожидается фронтендом:
        # features: [[obj1, obj2], [obj3, obj4]] где каждый внутренний массив соответствует одному изображению
        features = []
        for result in results:
            if 'objects' in result:
                features.append(result['objects'])
            else:
                features.append([])  # Пустой массив для случая ошибки
        return {
            "product_id": product_id,
            "images_processed": processed_count,
            "image_paths": image_paths,
            "features": features  # Возвращаем как массив массивов объектов
        }

    def get_product_images(self, product_id):
        """Get a list of available images for a product"""
        # Read images.csv to get image information
        product_images = {}
        try:
            # Using utf-8-sig to handle BOM in CSV files
            with open("images.csv", 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    image_product_id = row['product_id']
                    if image_product_id not in product_images:
                        product_images[image_product_id] = []
                    product_images[image_product_id].append({
                        'order': int(row['image_order']),
                        'url': row['image_url'],
                        'filename': row['image_url'].split('/')[-1]
                    })
        except Exception as e:
            return {"error": f"Error reading images.csv: {str(e)}"}

        # Get image info for specific product
        if product_id in product_images:
            images = sorted(product_images[product_id], key=lambda x: x['order'])
            available_images = []

            for img_info in images:
                image_path = os.path.join("Pics", img_info['filename'])
                available_images.append({
                    "order": img_info['order'],
                    "filename": img_info['filename'],
                    "path": image_path,
                    "exists": os.path.exists(image_path)
                })

            return {
                "product_id": product_id,
                "images": available_images
            }
        else:
            return {
                "product_id": product_id,
                "images": []
            }

# Create detector instance
detector = ImageDetector()

@app.route('/analyze-product', methods=['POST'])
def analyze_product():
    """
    Endpoint to analyze images for a specific product and return object features with bounding boxes
    """
    try:
        # Get product ID from request
        data = request.get_json()
        product_id = data.get('product_id')

        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400

        # Process images for the product
        result = detector.process_product_images(product_id)

        if "error" in result:
            return jsonify(result), 500

        # Return success response
        return jsonify({
            "status": "success",
            "product_id": result["product_id"],
            "images_processed": result["images_processed"],
            "image_paths": result["image_paths"],
            "features": result["features"]
        })

    except Exception as e:
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500

@app.route('/product-images/<product_id>', methods=['GET'])
def get_product_images(product_id):
    """
    Endpoint to get list of available images for a product
    """
    try:
        result = detector.get_product_images(product_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Error fetching images: {str(e)}"}), 500

@app.route('/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    """
    Serve image files from Pics directory
    """
    try:
        # Construct full path to the image in Pics folder
        image_path = os.path.join("Pics", filename)

        # Check if the file exists and is within the Pics directory
        if not os.path.exists(image_path):
            return jsonify({"error": "Image not found"}), 404

        # Verify the path is within Pics directory (security check)
        if not os.path.abspath(image_path).startswith(os.path.abspath("Pics")):
            return jsonify({"error": "Invalid path"}), 400

        # Serve the file
        return send_file(image_path)

    except Exception as e:
        return jsonify({"error": f"Error serving image: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)