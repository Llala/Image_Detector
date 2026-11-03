import os
import sys
import csv
import time
import json
import base64
import mimetypes
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
10. bbox MUST be an array of EXACTLY four numbers: [x_min, y_min, x_max, y_max].
11. Never put an array inside a coordinate key such as x_min.
12. Keep descriptions short (under 15 words) and return at most 6 highlights.

JSON format:
{
  "objects": [
    {
      "name": "product_name",
      "highlights": [
        {
          "name": "feature_name",
          "description": "feature_description",
          "bbox": [100, 200, 300, 400]
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

    @staticmethod
    def normalize_bbox(bbox):
        """Convert [xmin, ymin, xmax, ymax] or a dict into a validated dict."""
        keys = ("x_min", "y_min", "x_max", "y_max")
        if isinstance(bbox, list) and len(bbox) == 4:
            bbox = dict(zip(keys, bbox))
        elif isinstance(bbox, dict) and len(bbox) == 1:
            # Recover Qwen output such as {"x_min": [x1, y1, x2, y2]}.
            only_value = next(iter(bbox.values()))
            if isinstance(only_value, list) and len(only_value) == 4:
                bbox = dict(zip(keys, only_value))
        if not isinstance(bbox, dict) or any(key not in bbox for key in keys):
            raise ValueError("bbox must contain x_min, y_min, x_max, y_max")
        values = [bbox[key] for key in keys]
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in values):
            raise ValueError("bbox coordinates must be numeric")
        x1, y1, x2, y2 = values
        if not (0 <= x1 < x2 <= 1000 and 0 <= y1 < y2 <= 1000):
            raise ValueError("bbox coordinates must satisfy 0 <= min < max <= 1000")
        return dict(zip(keys, values))

    def detect_objects(self, image_path, product_id=None):
        """Detect product highlights in a local image via OpenRouter."""
        if not os.path.isfile(image_path):
            return {"product_id": product_id, "image_path": image_path,
                    "error": f"Local image file not found: {image_path}"}

        try:
            with open(image_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode("ascii")
            mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{mime_type};base64,{encoded}"
                    }},
                ],
            }]
            last_error = None
            raw_content = ""

            for attempt in range(2):
                # JSON mode support depends on the selected OpenRouter provider.
                response = self.client.chat.completions.create(
                    model="qwen/qwen3-vl-235B-A22B-instruct",
                    messages=messages,
                    response_format={"type": "json_object"},
                    max_tokens=3000,
                    temperature=0,
                )
                choice = response.choices[0]
                raw_content = choice.message.content or ""
                try:
                    if choice.finish_reason == "length":
                        raise ValueError("Model response was truncated (finish_reason=length)")
                    if choice.finish_reason != "stop":
                        raise ValueError(f"Unexpected finish_reason: {choice.finish_reason}")

                    parsed = json.loads(raw_content)
                    objects = parsed.get("objects")
                    if not isinstance(objects, list):
                        raise ValueError("objects must be an array")
                    normalized_objects = []
                    for obj in objects:
                        if not isinstance(obj, dict):
                            raise ValueError("Each object must be a JSON object")
                        highlights = obj.get("highlights", [])
                        if not isinstance(highlights, list):
                            raise ValueError("highlights must be an array")
                        normalized_highlights = []
                        for highlight in highlights:
                            if not isinstance(highlight, dict):
                                raise ValueError("Each highlight must be a JSON object")
                            normalized_highlights.append({
                                "name": str(highlight.get("name", "")),
                                "description": str(highlight.get("description", "")),
                                "bbox": self.normalize_bbox(highlight.get("bbox")),
                            })
                        normalized_objects.append({
                            "name": str(obj.get("name", "")),
                            "highlights": normalized_highlights,
                        })
                    return {"product_id": product_id, "image_path": image_path,
                            "objects": normalized_objects}
                except (json.JSONDecodeError, ValueError, TypeError) as exc:
                    last_error = str(exc)
                    print(f"Invalid model output (attempt {attempt + 1}/2): {last_error}")
                    print(f"finish_reason={choice.finish_reason}, preview={raw_content[:500]!r}")
                    if attempt == 0:
                        # Regenerate from the image, rather than trying to patch broken JSON.
                        messages[0]["content"][0]["text"] = (
                            PROMPT + "\nIMPORTANT: Previous output was invalid. "
                            "Return complete valid JSON. Every bbox must be a four-number "
                            "array [x_min, y_min, x_max, y_max]. Keep the response concise."
                        )

            return {"product_id": product_id, "image_path": image_path,
                    "objects": [], "error": f"Invalid model response: {last_error}",
                    "raw_response": raw_content}
        except Exception as exc:
            return {"product_id": product_id, "image_path": image_path,
                    "error": f"Error occurred during object detection: {exc}"}

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