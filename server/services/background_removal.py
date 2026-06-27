"""Background removal service using Hugging Face InferenceClient."""
import io
from pathlib import Path

from huggingface_hub import InferenceClient
from PIL import Image

from config import HF_TOKEN


def _get_inference_client() -> InferenceClient:
    """Initialize Hugging Face InferenceClient."""
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN environment variable is not set")
    
    return InferenceClient(token=HF_TOKEN)


def _process_segmentation_result(result) -> Image.Image:
    """Process segmentation result which may be PIL Image, bytes, or file-like."""
    if isinstance(result, Image.Image):
        return result.convert("RGBA")
    
    if isinstance(result, bytes):
        return Image.open(io.BytesIO(result)).convert("RGBA")
    
    if hasattr(result, "read"):
        return Image.open(result).convert("RGBA")
    
    if isinstance(result, list) and len(result) > 0:
        first_item = result[0]
        if hasattr(first_item, "mask"):
            mask = first_item.mask
            if isinstance(mask, Image.Image):
                return mask.convert("RGBA")
            if isinstance(mask, bytes):
                return Image.open(io.BytesIO(mask)).convert("RGBA")
    
    raise TypeError(f"Unexpected result type from segmentation: {type(result)}")


def remove_background(image_path: Path) -> Image.Image:
    """Remove background from vehicle image using RMBG-2.0 model."""
    client = _get_inference_client()
    
    result = client.image_segmentation(
        str(image_path),
        model="briaai/RMBG-2.0"
    )
    
    return _process_segmentation_result(result)
