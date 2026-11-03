# Image Detection System with Qwen/VL-235B-A22B-instruct

This system implements image detection using the Qwen/VL-235B-A22B-instruct model through OpenRouter API. It allows for object detection in product images and returns bounding box coordinates for detected objects.

## Features

- **Image detection** using Qwen/VL-235B-A22B-instruct model
- **Bounding box coordinates** for detected objects (x_min, y_min, x_max, y_max)  
- **Local image processing** (no remote image downloads)
- **CSV integration** for product and image data
- **Image serving capability** via `/images/<filename>` endpoint
- **CORS support** for frontend integration

## API Endpoints

### 1. Analyze Product
```
POST /analyze-product
{
  "product_id": "39506410299"
}
```

Returns object detection results with bounding box coordinates.

### 2. Get Product Images
```
GET /product-images/{product_id}
```

Returns list of available images for a product.

### 3. Serve Image Files
```
GET /images/{filename}
```

Serves image files from the Pics directory. For example: `/images/175336730299.jpg`

## File Structure

- `Pics/` - Directory containing product images  
- `products.csv` - Product information
- `images.csv` - Image associations with products
- `requirements.txt` - Python dependencies
- `backend_endpoint.py` - Flask backend with image serving capability
- `src/App.js` - React frontend (if applicable)

## Setup and Usage

### 1. Backend Setup

1. Create a `.env` file with your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Run the backend server:
```bash
python backend_endpoint.py
```

### 2. Frontend Setup (React Application)

If you want to run the React frontend, first ensure all dependencies are installed:
```bash
npm install react react-dom react-scripts
```

Then run:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

### 3. Static HTML Frontend

For the HTML version, simply run:
```bash
python3 -m http.server 8083
```

The HTML frontend will be available at `http://localhost:8083/index.html`

## Using Image URLs

The system provides direct URLs to images in the Pics folder:
```
http://localhost:5002/images/175336730299.jpg
http://localhost:5002/images/175336740299.jpg
```

## Example API Usage

```bash
# Get product image list
curl http://localhost:5002/product-images/39506410299

# Analyze product
curl -X POST http://localhost:5002/analyze-product \
  -H "Content-Type: application/json" \
  -d '{"product_id": "39506410299"}'

# Serve an image
curl http://localhost:5002/images/175336730299.jpg
```

## Requirements

- Python 3.7+
- Flask
- OpenAI Python SDK
- Flask-CORS
- requests
- python-dotenv

## Running the System

### Backend Server
1. Start the backend server:
```bash
python3 backend_endpoint.py
```

2. The backend will serve on port 5002.

### Frontend Server

#### For React Application:
1. Install dependencies:
```bash
npm install
```
2. Run the React app:
```bash
npm start
```

#### For Static HTML:
1. Run HTTP server:
```bash
python3 -m http.server 8083
```

## Complete Workflow

1. **Backend** on port 5002 handles all API requests:
   - `/analyze-product` - analyzes images
   - `/product-images/{product_id}` - gets image lists
   - `/images/{filename}` - serves images

2. **Frontend** (React or HTML) makes requests to backend:
   - Gets product information and image files
   - Receives object detection results with bounding box coordinates

3. **Result**:
   - Real product images served via URL
   - Coordinates for object positions in images
   - Complete analysis workflow

## Security Notes

The image serving endpoint:
- Validates file paths to prevent directory traversal
- Only serves files from the Pics directory
- Includes proper error handling for missing files

## Future Improvements

- Add image preprocessing capabilities
- Implement batch processing with better throttling
- Add support for different model versions
- Include confidence scores for detections
- Add support for saving detection results in structured formats

## Limitations and Considerations

- Requires internet connectivity for API calls to OpenRouter
- Performance depends on image size and complexity
- API calls may be subject to rate limits
- Accuracy varies based on image quality and object complexity
- Model response time depends on OpenRouter's infrastructure# Image_Detector
