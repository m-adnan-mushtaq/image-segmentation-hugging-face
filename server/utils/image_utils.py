"""Image compositing and vehicle preparation utilities."""
from pathlib import Path

import numpy as np
from PIL import Image

from config import (
    OUTPUT_HEIGHT,
    OUTPUT_WIDTH,
    VEHICLE_GROUND_OFFSET,
    VEHICLE_HEIGHT_RATIO,
)


def load_and_prepare_background(bg_path: Path) -> Image.Image:
    """Load background image and resize to output dimensions."""
    bg = Image.open(bg_path).convert("RGBA")
    return bg.resize((OUTPUT_WIDTH, OUTPUT_HEIGHT), Image.Resampling.LANCZOS)


def prepare_vehicle_cutout(
    cutout: Image.Image, target_height: int
) -> tuple[Image.Image, int, int]:
    """Resize vehicle cutout and calculate positioning."""
    cutout = cutout.convert("RGBA")

    aspect_ratio = cutout.width / cutout.height
    new_height = int(target_height * VEHICLE_HEIGHT_RATIO)
    new_width = int(new_height * aspect_ratio)

    if new_width > OUTPUT_WIDTH * 0.95:
        new_width = int(OUTPUT_WIDTH * 0.95)
        new_height = int(new_width / aspect_ratio)

    resized_cutout = cutout.resize((new_width, new_height), Image.Resampling.LANCZOS)

    x_pos = (OUTPUT_WIDTH - new_width) // 2
    y_pos = OUTPUT_HEIGHT - new_height - VEHICLE_GROUND_OFFSET

    return resized_cutout, x_pos, y_pos


def _create_shadow_layer(
    shadow_mask: np.ndarray,
    vehicle_width: int,
    vehicle_height: int,
    x_pos: int,
    y_pos: int,
) -> Image.Image:
    """Create shadow layer from extracted mask, positioned under vehicle."""
    shadow_img = Image.fromarray(shadow_mask).convert("L")
    shadow_resized = shadow_img.resize(
        (vehicle_width, vehicle_height), Image.Resampling.LANCZOS
    )

    shadow_layer = Image.new("RGBA", (OUTPUT_WIDTH, OUTPUT_HEIGHT), (0, 0, 0, 0))

    shadow_rgba = Image.new("RGBA", shadow_resized.size, (0, 0, 0, 0))
    shadow_rgba.putalpha(shadow_resized)
    shadow_layer.paste(shadow_rgba, (x_pos, y_pos), shadow_rgba)

    return shadow_layer


def composite_final_image(
    background: Image.Image,
    vehicle_cutout: Image.Image,
    shadow_mask: np.ndarray,
    x_pos: int,
    y_pos: int,
) -> Image.Image:
    """Composite background, original shadow, and vehicle cutout."""
    final_image = background.copy()

    shadow_layer = _create_shadow_layer(
        shadow_mask,
        vehicle_cutout.width,
        vehicle_cutout.height,
        x_pos,
        y_pos,
    )
    final_image = Image.alpha_composite(final_image, shadow_layer)

    vehicle_layer = Image.new("RGBA", (OUTPUT_WIDTH, OUTPUT_HEIGHT), (0, 0, 0, 0))
    vehicle_layer.paste(vehicle_cutout, (x_pos, y_pos), vehicle_cutout)
    final_image = Image.alpha_composite(final_image, vehicle_layer)

    return final_image
