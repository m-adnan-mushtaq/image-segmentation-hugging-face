"""Application configuration and constants."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
BACKGROUNDS_DIR = BASE_DIR / "backgrounds"
TEMP_DIR = BASE_DIR / "temp"
UPLOADS_DIR = BASE_DIR / "uploads"

HF_TOKEN = os.environ.get("HF_TOKEN")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

CORS_ORIGINS = [
    origin.strip()
    for origin in FRONTEND_URL.split(",")
    if origin.strip()
]

VALID_BACKGROUNDS = ["studio", "road", "showroom"]
DEFAULT_BACKGROUND = "studio"

OUTPUT_WIDTH = 1920
OUTPUT_HEIGHT = 1080

SHADOW_OPACITY = 0.4
SHADOW_BLUR_RADIUS = 51
VEHICLE_GROUND_OFFSET = 50
