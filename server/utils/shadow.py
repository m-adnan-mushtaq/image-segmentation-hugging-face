"""Shadow extraction from original vehicle images using OpenCV."""
import cv2
import numpy as np
from PIL import Image

from config import SHADOW_BLUR_RADIUS, SHADOW_OPACITY

MIN_SHADOW_AREA_RATIO = 0.00025
VEHICLE_ALPHA_THRESHOLD = 24


def _odd_kernel_size(value: float, minimum: int = 3) -> int:
    size = max(minimum, int(round(value)))
    return size if size % 2 == 1 else size + 1


def _vehicle_alpha_for_size(
    vehicle_cutout: Image.Image | None,
    target_size: tuple[int, int],
) -> np.ndarray | None:
    if vehicle_cutout is None or "A" not in vehicle_cutout.getbands():
        return None

    alpha = vehicle_cutout.convert("RGBA").getchannel("A")
    if alpha.size != target_size:
        alpha = alpha.resize(target_size, Image.Resampling.LANCZOS)

    alpha_array = np.array(alpha, dtype=np.uint8)
    has_transparency = np.count_nonzero(alpha_array < 250) > alpha_array.size * 0.01
    has_vehicle = np.count_nonzero(alpha_array > VEHICLE_ALPHA_THRESHOLD) > (
        alpha_array.size * 0.01
    )

    if not has_transparency or not has_vehicle:
        return None

    return alpha_array


def _mask_bbox(
    mask: np.ndarray,
    fallback_shape: tuple[int, int],
) -> tuple[int, int, int, int]:
    ys, xs = np.where(mask)
    if len(xs) == 0 or len(ys) == 0:
        height, width = fallback_shape
        return (
            int(width * 0.05),
            int(height * 0.35),
            int(width * 0.95),
            height,
        )

    return int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)


def _build_shadow_search_region(
    shape: tuple[int, int],
    vehicle_bbox: tuple[int, int, int, int],
) -> np.ndarray:
    height, width = shape
    x_min, y_min, x_max, y_max = vehicle_bbox
    vehicle_width = max(1, x_max - x_min)
    vehicle_height = max(1, y_max - y_min)

    x_padding = int(vehicle_width * 1.2)
    y_start = max(0, int(y_min + vehicle_height * 0.3))
    y_end = min(height, int(y_max + vehicle_height * 0.35))

    if y_end <= y_start:
        y_start = int(height * 0.55)
        y_end = height

    region = np.zeros((height, width), dtype=bool)
    region[
        y_start:y_end,
        max(0, x_min - x_padding) : min(width, x_max + x_padding),
    ] = True
    return region


def _keep_contact_shadow_components(
    candidate_mask: np.ndarray,
    vehicle_mask: np.ndarray | None,
    vehicle_bbox: tuple[int, int, int, int],
) -> np.ndarray:
    if not np.any(candidate_mask):
        return candidate_mask

    height, width = candidate_mask.shape
    min_area = max(12, int(height * width * MIN_SHADOW_AREA_RATIO))

    labels_count, labels, stats, _ = cv2.connectedComponentsWithStats(
        candidate_mask.astype(np.uint8), connectivity=8
    )

    if labels_count <= 1:
        return candidate_mask

    if vehicle_mask is None:
        component_ids = sorted(
            range(1, labels_count),
            key=lambda idx: stats[idx, cv2.CC_STAT_AREA],
            reverse=True,
        )[:3]
        keep = np.zeros_like(candidate_mask)
        for component_id in component_ids:
            if stats[component_id, cv2.CC_STAT_AREA] >= min_area:
                keep |= labels == component_id
        return keep

    _, y_min, _, y_max = vehicle_bbox
    vehicle_height = max(1, y_max - y_min)
    y_indices = np.indices(candidate_mask.shape)[0]
    lower_vehicle = vehicle_mask & (y_indices >= int(y_min + vehicle_height * 0.42))

    anchor_size = _odd_kernel_size(min(height, width) * 0.08, 9)
    anchor_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (anchor_size, anchor_size),
    )
    contact_anchor = cv2.dilate(
        lower_vehicle.astype(np.uint8),
        anchor_kernel,
        iterations=1,
    ).astype(bool)

    keep = np.zeros_like(candidate_mask)
    for component_id in range(1, labels_count):
        area = stats[component_id, cv2.CC_STAT_AREA]
        if area < min_area:
            continue

        component = labels == component_id
        if np.any(component & contact_anchor):
            keep |= component

    if np.any(keep):
        return keep

    component_ids = sorted(
        range(1, labels_count),
        key=lambda idx: stats[idx, cv2.CC_STAT_AREA],
        reverse=True,
    )[:2]
    for component_id in component_ids:
        if stats[component_id, cv2.CC_STAT_AREA] >= min_area:
            keep |= labels == component_id

    return keep


def _fallback_contact_shadow(
    shape: tuple[int, int],
    vehicle_bbox: tuple[int, int, int, int],
) -> np.ndarray:
    height, width = shape
    x_min, y_min, x_max, y_max = vehicle_bbox
    vehicle_width = max(1, x_max - x_min)
    vehicle_height = max(1, y_max - y_min)

    mask = np.zeros((height, width), dtype=np.uint8)
    center_x = int((x_min + x_max) / 2)
    ground_y = min(height - 1, int(y_max - vehicle_height * 0.02))

    primary_axes = (
        max(10, int(vehicle_width * 0.55)),
        max(6, int(vehicle_height * 0.12)),
    )
    cv2.ellipse(
        mask, (center_x, ground_y), primary_axes,
        0, 0, 360, int(255 * SHADOW_OPACITY * 0.7), -1,
    )

    soft_axes = (
        max(12, int(vehicle_width * 0.65)),
        max(8, int(vehicle_height * 0.18)),
    )
    cv2.ellipse(
        mask, (center_x, ground_y), soft_axes,
        0, 0, 360, int(255 * SHADOW_OPACITY * 0.3), -1,
    )

    blur_size = _odd_kernel_size(
        min(SHADOW_BLUR_RADIUS, min(height, width) * 0.1), 11,
    )
    return cv2.GaussianBlur(mask, (blur_size, blur_size), 0)


def _estimate_row_floor_lightness(
    lightness: np.ndarray,
    valid_floor_mask: np.ndarray,
) -> np.ndarray:
    height, width = lightness.shape
    row_estimates = np.full(height, np.nan, dtype=np.float32)
    min_row_samples = max(8, int(width * 0.04))

    for row in range(height):
        row_values = lightness[row][valid_floor_mask[row]]
        if row_values.size >= min_row_samples:
            row_estimates[row] = np.percentile(row_values, 85)

    known_rows = np.where(~np.isnan(row_estimates))[0]
    if known_rows.size == 0:
        return np.zeros_like(lightness, dtype=np.float32)

    if known_rows.size == 1:
        row_estimates[:] = row_estimates[known_rows[0]]
    else:
        missing_rows = np.where(np.isnan(row_estimates))[0]
        row_estimates[missing_rows] = np.interp(
            missing_rows,
            known_rows,
            row_estimates[known_rows],
        )

    smooth_size = _odd_kernel_size(height * 0.035, 5)
    row_estimates = cv2.GaussianBlur(
        row_estimates.reshape(height, 1),
        (1, smooth_size),
        0,
    ).reshape(height)

    return np.repeat(row_estimates[:, None], width, axis=1)


def extract_shadow_mask(
    original_image: Image.Image,
    vehicle_cutout: Image.Image | None = None,
) -> np.ndarray:
    """Extract the original vehicle drop shadow as a soft alpha mask."""
    img_array = np.array(original_image.convert("RGB"))
    height, width = img_array.shape[:2]

    vehicle_alpha = _vehicle_alpha_for_size(vehicle_cutout, (width, height))
    vehicle_mask = (
        vehicle_alpha > VEHICLE_ALPHA_THRESHOLD
        if vehicle_alpha is not None
        else None
    )
    vehicle_bbox = _mask_bbox(
        vehicle_mask if vehicle_mask is not None else np.zeros((height, width), bool),
        (height, width),
    )

    search_region = _build_shadow_search_region((height, width), vehicle_bbox)

    lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
    lightness = lab[:, :, 0].astype(np.uint8)

    if vehicle_mask is not None:
        inpaint_size = _odd_kernel_size(min(height, width) * 0.025, 5)
        inpaint_kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (inpaint_size, inpaint_size),
        )
        inpaint_mask = cv2.dilate(
            vehicle_mask.astype(np.uint8),
            inpaint_kernel,
            iterations=1,
        )
        background_lightness = cv2.inpaint(
            lightness,
            inpaint_mask,
            max(3, inpaint_size // 3),
            cv2.INPAINT_TELEA,
        )
    else:
        background_lightness = lightness

    close_size = _odd_kernel_size(min(height, width) * 0.11, 15)
    close_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (close_size, close_size),
    )
    local_floor_lightness = cv2.morphologyEx(
        background_lightness,
        cv2.MORPH_CLOSE,
        close_kernel,
    )
    blur_size = _odd_kernel_size(close_size * 0.45, 9)
    local_floor_lightness = cv2.GaussianBlur(
        local_floor_lightness,
        (blur_size, blur_size),
        0,
    )

    valid_floor_mask = search_region.copy()
    if vehicle_mask is not None:
        valid_floor_mask &= ~vehicle_mask

    row_floor_lightness = _estimate_row_floor_lightness(lightness, valid_floor_mask)

    local_delta = local_floor_lightness.astype(np.float32) - lightness.astype(np.float32)
    row_delta = row_floor_lightness - lightness.astype(np.float32)
    darkness_delta = np.maximum(local_delta, row_delta)
    shadow_strength = np.clip((darkness_delta - 2.0) / 32.0, 0.0, 1.0)

    candidate_mask = (shadow_strength > 0) & search_region
    if vehicle_mask is not None:
        candidate_mask &= ~vehicle_mask

    candidate_mask = _keep_contact_shadow_components(
        candidate_mask,
        vehicle_mask,
        vehicle_bbox,
    )

    strength_values = shadow_strength[candidate_mask]
    min_shadow_area = max(12, int(height * width * MIN_SHADOW_AREA_RATIO))
    if (
        strength_values.size < min_shadow_area
        or np.percentile(strength_values, 95) < 0.015
    ):
        return _fallback_contact_shadow((height, width), vehicle_bbox)

    shadow_alpha = np.zeros((height, width), dtype=np.float32)
    strength_normalizer = max(float(np.percentile(strength_values, 95)), 0.12)
    shadow_alpha[candidate_mask] = np.clip(
        shadow_strength[candidate_mask] / strength_normalizer,
        0.0,
        1.0,
    )

    max_alpha = 255 * SHADOW_OPACITY
    shadow_alpha = (shadow_alpha * max_alpha).astype(np.uint8)

    cleanup_size = _odd_kernel_size(min(height, width) * 0.012, 3)
    cleanup_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (cleanup_size, cleanup_size),
    )
    shadow_alpha = cv2.morphologyEx(
        shadow_alpha,
        cv2.MORPH_CLOSE,
        cleanup_kernel,
    )

    final_blur_size = _odd_kernel_size(
        min(SHADOW_BLUR_RADIUS, min(height, width) * 0.08), 9,
    )
    shadow_alpha = cv2.GaussianBlur(
        shadow_alpha,
        (final_blur_size, final_blur_size),
        0,
    )

    if vehicle_mask is not None:
        shadow_alpha[vehicle_mask] = 0

    return shadow_alpha
