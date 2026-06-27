# Vehicle Background Replacement API

A FastAPI application that removes vehicle backgrounds and composites them onto new backgrounds with realistic shadows.

## Features

- Background removal using RMBG-2.0 model via Hugging Face
- Shadow extraction and preservation from original image
- Multiple background options (studio, road, showroom, gradient)
- Automatic vehicle centering and positioning

## Project Structure

```
server/
├── main.py                 # FastAPI application
├── config.py               # Configuration and constants
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (HF_TOKEN)
├── services/
│   ├── __init__.py
│   └── background_removal.py  # HuggingFace RMBG integration
├── utils/
│   ├── __init__.py
│   ├── file_utils.py       # File handling utilities
│   └── image_utils.py      # Image processing & compositing
├── backgrounds/            # Background images
│   ├── studio.jpg
│   ├── road.jpg
│   ├── showroom.jpg
│   └── gradient.jpg
└── temp/                   # Temporary files (auto-created)
```

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # .env file
   HF_TOKEN=your_huggingface_token_here
   ```

4. Add background images to `backgrounds/` folder

## Running the Server

```bash
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`

## API Endpoints

### POST /replace-bg

Replace vehicle background with selected scene.

**Request:**
- Content-Type: `multipart/form-data`
- `image`: Vehicle image file (required)
- `background`: Background option (optional, default: "studio")
  - Options: "studio", "road", "showroom", "gradient"

**Response:**
- Content-Type: `image/png`
- Final composited image

### GET /backgrounds

List available background options.

### GET /

Health check endpoint.

## Example Usage

### cURL

```bash
# Basic usage with default background
curl -X POST "http://localhost:8000/replace-bg" \
  -F "image=@vehicle.jpg" \
  -o output.png

# Specify background
curl -X POST "http://localhost:8000/replace-bg" \
  -F "image=@vehicle.jpg" \
  -F "background=showroom" \
  -o output.png
```

### Python

```python
import requests

url = "http://localhost:8000/replace-bg"
files = {"image": open("vehicle.jpg", "rb")}
data = {"background": "road"}

response = requests.post(url, files=files, data=data)

with open("output.png", "wb") as f:
    f.write(response.content)
```

## Configuration

Edit `config.py` to customize:

- `OUTPUT_WIDTH`, `OUTPUT_HEIGHT`: Final image dimensions (default: 1920x1080)
- `SHADOW_OPACITY`: Shadow transparency (default: 0.4)
- `SHADOW_BLUR_RADIUS`: Shadow blur amount (default: 51)
- `VEHICLE_GROUND_OFFSET`: Vehicle position from bottom (default: 50px)
