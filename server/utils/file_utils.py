"""File handling utilities."""
import os
import uuid
from pathlib import Path

from config import TEMP_DIR


def generate_temp_filepath(extension: str = ".png") -> Path:
    """Generate a unique temporary file path."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}{extension}"
    return TEMP_DIR / filename


def cleanup_temp_files(*file_paths: Path) -> None:
    """Remove temporary files safely."""
    for file_path in file_paths:
        try:
            if file_path and file_path.exists():
                os.remove(file_path)
        except OSError:
            pass


def get_background_path(background_name: str, backgrounds_dir: Path) -> Path:
    """Get background image path with fallback to studio.jpg."""
    extensions = [".jpg", ".jpeg", ".png"]
    
    for ext in extensions:
        bg_path = backgrounds_dir / f"{background_name}{ext}"
        if bg_path.exists():
            return bg_path
    
    for ext in extensions:
        fallback_path = backgrounds_dir / f"studio{ext}"
        if fallback_path.exists():
            return fallback_path
    
    raise FileNotFoundError("No background images found in backgrounds folder")
