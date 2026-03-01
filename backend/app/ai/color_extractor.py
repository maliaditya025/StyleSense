"""
Color extraction from clothing images using OpenCV and KMeans clustering.
Extracts the dominant (primary) and secondary colors, returns them as hex
values along with human-readable color names.
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from pathlib import Path


# Named color mapping — maps RGB centroids to human-readable names
NAMED_COLORS = {
    "Black":       (0, 0, 0),
    "White":       (255, 255, 255),
    "Red":         (220, 50, 50),
    "Dark Red":    (139, 0, 0),
    "Blue":        (50, 50, 220),
    "Navy":        (0, 0, 128),
    "Sky Blue":    (135, 206, 235),
    "Green":       (50, 180, 50),
    "Dark Green":  (0, 100, 0),
    "Olive":       (128, 128, 0),
    "Yellow":      (240, 240, 50),
    "Orange":      (255, 165, 0),
    "Purple":      (128, 0, 128),
    "Pink":        (255, 192, 203),
    "Brown":       (139, 90, 43),
    "Tan":         (210, 180, 140),
    "Beige":       (245, 245, 220),
    "Gray":        (128, 128, 128),
    "Light Gray":  (192, 192, 192),
    "Dark Gray":   (64, 64, 64),
    "Maroon":      (128, 0, 0),
    "Coral":       (255, 127, 80),
    "Teal":        (0, 128, 128),
    "Burgundy":    (128, 0, 32),
    "Lavender":    (200, 162, 200),
    "Khaki":       (195, 176, 145),
    "Cream":       (255, 253, 208),
    "Charcoal":    (54, 69, 79),
    "Denim Blue":  (21, 96, 189),
}


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex color string."""
    return f"#{r:02x}{g:02x}{b:02x}"


def _closest_color_name(rgb: tuple) -> str:
    """Find the closest named color to the given RGB value using Euclidean distance."""
    min_dist = float("inf")
    closest = "Unknown"

    for name, color_rgb in NAMED_COLORS.items():
        dist = sum((a - b) ** 2 for a, b in zip(rgb, color_rgb)) ** 0.5
        if dist < min_dist:
            min_dist = dist
            closest = name

    return closest


def _remove_background(image: np.ndarray) -> np.ndarray:
    """
    Simple background removal by masking very bright/very dark uniform regions.
    This helps the KMeans focus on the actual clothing colors.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Mask out very white backgrounds (V > 240, S < 30)
    white_mask = (hsv[:, :, 2] > 240) & (hsv[:, :, 1] < 30)
    # Mask out very black backgrounds (V < 15)
    black_mask = hsv[:, :, 2] < 15

    combined_mask = ~(white_mask | black_mask)

    # Apply mask — keep only non-background pixels
    foreground_pixels = image[combined_mask]

    if len(foreground_pixels) < 100:
        # If too few pixels remain, use full image
        return image.reshape(-1, 3)

    return foreground_pixels


def extract_colors(image_path: str, n_colors: int = 3) -> dict:
    """
    Extract dominant colors from a clothing image.

    Returns:
        {
            "primary": "#hex_color",
            "secondary": "#hex_color" or None,
            "name": "Color Name",
            "all_colors": [{"hex": "#...", "name": "...", "percentage": 0.XX}, ...]
        }
    """
    if not Path(image_path).exists():
        return {
            "primary": "#6b7280",
            "secondary": None,
            "name": "Gray",
            "all_colors": [],
        }

    # Read and resize image for faster processing
    img = cv2.imread(image_path)
    if img is None:
        return {"primary": "#6b7280", "secondary": None, "name": "Gray", "all_colors": []}

    # Resize to max 300px for performance
    h, w = img.shape[:2]
    scale = min(300 / max(h, w), 1.0)
    img = cv2.resize(img, (int(w * scale), int(h * scale)))

    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Remove background to focus on clothing
    pixels = _remove_background(img_rgb)
    if pixels.ndim != 2:
        pixels = pixels.reshape(-1, 3)

    # Run KMeans clustering
    n_colors = min(n_colors, len(pixels))
    kmeans = KMeans(n_clusters=n_colors, n_init=10, max_iter=200, random_state=42)
    kmeans.fit(pixels)

    # Get cluster centers and their proportions
    centers = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_
    counts = np.bincount(labels)
    percentages = counts / len(labels)

    # Sort by frequency (most dominant first)
    sorted_indices = np.argsort(-percentages)

    all_colors = []
    for idx in sorted_indices:
        r, g, b = centers[idx]
        hex_color = _rgb_to_hex(r, g, b)
        color_name = _closest_color_name((r, g, b))
        all_colors.append({
            "hex": hex_color,
            "name": color_name,
            "percentage": round(float(percentages[idx]), 3),
        })

    primary = all_colors[0] if all_colors else {"hex": "#6b7280", "name": "Gray"}
    secondary = all_colors[1] if len(all_colors) > 1 else None

    return {
        "primary": primary["hex"],
        "secondary": secondary["hex"] if secondary else None,
        "name": primary["name"],
        "all_colors": all_colors,
    }
