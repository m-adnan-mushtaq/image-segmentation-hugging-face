"""FastAPI application for vehicle background replacement."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PIL import Image

from config import (
    BACKGROUNDS_DIR,
    CORS_ORIGINS,
    DEFAULT_BACKGROUND,
    MAX_UPLOAD_SIZE_BYTES,
    MAX_UPLOAD_SIZE_MB,
    TEMP_DIR,
    VALID_BACKGROUNDS,
)
from services.background_removal import remove_background
from utils import (
    cleanup_temp_files,
    composite_final_image,
    extract_shadow_mask,
    generate_temp_filepath,
    get_background_path,
    load_and_prepare_background,
    prepare_vehicle_cutout,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure required directories exist on startup."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    BACKGROUNDS_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="Vehicle Background Replacement API",
    description="Replace vehicle backgrounds with custom scenes",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _save_upload_file(upload_file: UploadFile) -> Path:
    """Save uploaded file to temp directory."""
    suffix = Path(upload_file.filename or "image.jpg").suffix or ".jpg"
    temp_path = generate_temp_filepath(suffix)

    content = await upload_file.read()

    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File size must not exceed {MAX_UPLOAD_SIZE_MB} MB",
        )

    with open(temp_path, "wb") as f:
        f.write(content)

    return temp_path


def _process_vehicle_image(
    input_path: Path,
    background_name: str,
) -> Path:
    """Process vehicle image and composite with new background."""
    original_image = Image.open(input_path).convert("RGBA")

    logger.info("Removing background using RMBG-2.0...")
    vehicle_cutout = remove_background(input_path)

    logger.info("Extracting shadow from original image...")
    shadow_mask = extract_shadow_mask(original_image, vehicle_cutout)

    logger.info(f"Loading background: {background_name}")
    bg_path = get_background_path(background_name, BACKGROUNDS_DIR)
    background = load_and_prepare_background(bg_path)

    logger.info("Preparing vehicle cutout...")
    resized_cutout, x_pos, y_pos = prepare_vehicle_cutout(
        vehicle_cutout, background.height
    )

    logger.info("Compositing final image...")
    final_image = composite_final_image(
        background, resized_cutout, shadow_mask, x_pos, y_pos
    )

    output_path = generate_temp_filepath(".png")
    final_image.save(output_path, "PNG")

    return output_path


@app.post("/replace-bg", response_class=FileResponse)
async def replace_background(
    image: UploadFile = File(..., description="Vehicle image to process"),
    background: str = Form(
        DEFAULT_BACKGROUND,
        description="Background option: studio, road, showroom, gradient",
    ),
):
    """Replace vehicle background with selected scene."""
    input_path = None
    output_path = None

    try:
        if background not in VALID_BACKGROUNDS:
            logger.warning(f"Invalid background '{background}', using default")
            background = DEFAULT_BACKGROUND

        input_path = await _save_upload_file(image)
        logger.info(f"Saved upload to {input_path}")

        output_path = _process_vehicle_image(input_path, background)
        logger.info(f"Generated output at {output_path}")

        cleanup_temp_files(input_path)

        return FileResponse(
            path=str(output_path),
            media_type="image/png",
            filename="vehicle_processed.png",
            background=None,
        )

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        cleanup_temp_files(input_path, output_path)
        raise HTTPException(status_code=404, detail=str(e))

    except ValueError as e:
        logger.error(f"Value error: {e}")
        cleanup_temp_files(input_path, output_path)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        cleanup_temp_files(input_path, output_path)
        raise HTTPException(status_code=500, detail="Image processing failed")


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "vehicle-bg-replacement"}


@app.get("/backgrounds")
async def list_backgrounds():
    """List available background options."""
    return {"backgrounds": VALID_BACKGROUNDS, "default": DEFAULT_BACKGROUND}
