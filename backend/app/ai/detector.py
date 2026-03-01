"""
CNN-based clothing category detector using MobileNetV2 transfer learning.

Three modes of operation (in priority order):
  1. CUSTOM MODEL: If clothing_model.h5 exists, uses it for 10-class prediction.
  2. IMAGENET CNN: Uses MobileNetV2 ImageNet weights with class mapping.
  3. HEURISTIC FALLBACK: Uses image analysis (aspect ratio, color, skin detection)
     when CNN confidence is below threshold.

The hybrid approach combines CNN strengths (good at jersey/t-shirt, jean, shoe, suit)
with heuristic strengths (good at distinguishing pants from shirts by aspect ratio).

Supported categories:
  shirt, t-shirt, pants, jeans, shoes, jacket, dress, accessories, shorts, skirt
"""

import os
import numpy as np
from pathlib import Path

# Suppress TensorFlow info messages
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import cv2

# Check if TensorFlow is available (optional dependency)
try:
    import tensorflow
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️  TensorFlow not installed — using heuristic-only clothing detection")

# Lazy imports for TensorFlow (heavy library)
_tf_loaded = False
_custom_model = None
_imagenet_model = None

CATEGORIES = [
    "shirt", "t-shirt", "pants", "jeans", "shoes",
    "jacket", "dress", "accessories", "shorts", "skirt",
]

IMG_SIZE = 224

# ─── ImageNet class → our category mapping ─────────────────────────────
IMAGENET_MAP = {
    # Tops / T-shirts
    "jersey": "t-shirt",
    "sweatshirt": "shirt",
    "wool": "shirt",
    # Jackets / Outerwear
    "cardigan": "jacket",
    "suit": "jacket",
    "lab_coat": "jacket",
    "military_uniform": "jacket",
    "poncho": "jacket",
    "trench_coat": "jacket",
    "fur_coat": "jacket",
    "bulletproof_vest": "jacket",
    "chain_mail": "jacket",
    "cuirass": "jacket",
    # Bottoms
    "jean": "jeans",
    "swimming_trunks": "shorts",
    "pajama": "pants",
    # Dresses / Skirts
    "kimono": "dress",
    "abaya": "dress",
    "maillot": "dress",
    "gown": "dress",
    "academic_gown": "dress",
    "vestment": "dress",
    "sarong": "skirt",
    "overskirt": "skirt",
    "hoopskirt": "skirt",
    "miniskirt": "skirt",
    # Shoes
    "running_shoe": "shoes",
    "sandal": "shoes",
    "cowboy_boot": "shoes",
    "Loafer": "shoes",
    "clog": "shoes",
    # Accessories
    "bow_tie": "accessories",
    "Windsor_tie": "accessories",
    "bolo_tie": "accessories",
    "sunglass": "accessories",
    "sunglasses": "accessories",
    "sombrero": "accessories",
    "cowboy_hat": "accessories",
    "bonnet": "accessories",
    "backpack": "accessories",
    "purse": "accessories",
    "wallet": "accessories",
    "sock": "accessories",
    "stole": "accessories",
    "mitten": "accessories",
}


# ═══════════════════════════════════════════════════════════════════════
# CNN DETECTION
# ═══════════════════════════════════════════════════════════════════════

def _ensure_tf():
    """Lazy-load TensorFlow modules."""
    global _tf_loaded
    if not _tf_loaded:
        import tensorflow as tf  # noqa: F401
        _tf_loaded = True


def _get_custom_model():
    """Load custom-trained model if available."""
    global _custom_model
    model_path = Path(__file__).parent / "clothing_model.h5"
    if model_path.exists() and _custom_model is None:
        _ensure_tf()
        from tensorflow.keras.models import load_model
        print(f"🧠 Loading custom clothing model from {model_path}")
        _custom_model = load_model(str(model_path))
    return _custom_model


def _get_imagenet_model():
    """Load MobileNetV2 with ImageNet weights."""
    global _imagenet_model
    if _imagenet_model is None:
        _ensure_tf()
        from tensorflow.keras.applications import MobileNetV2
        print("🧠 Loading MobileNetV2 ImageNet model...")
        _imagenet_model = MobileNetV2(
            input_shape=(IMG_SIZE, IMG_SIZE, 3),
            include_top=True,
            weights="imagenet",
        )
    return _imagenet_model


def _preprocess_for_mobilenet(img_path: str) -> np.ndarray:
    """Load and preprocess image for MobileNetV2."""
    _ensure_tf()
    from tensorflow.keras.preprocessing import image
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

    img = image.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    arr = image.img_to_array(img)
    arr = np.expand_dims(arr, axis=0)
    return preprocess_input(arr)


def _predict_cnn(img_path: str) -> dict:
    """Predict using MobileNetV2 ImageNet weights."""
    _ensure_tf()
    from tensorflow.keras.applications.mobilenet_v2 import decode_predictions

    model = _get_imagenet_model()
    arr = _preprocess_for_mobilenet(img_path)
    preds = model.predict(arr, verbose=0)

    decoded = decode_predictions(preds, top=20)[0]

    # Aggregate scores for our categories
    scores = {cat: 0.0 for cat in CATEGORIES}
    for _, class_name, score in decoded:
        mapped = IMAGENET_MAP.get(class_name)
        if mapped:
            scores[mapped] += float(score)

    best_cat = max(scores, key=scores.get)
    best_score = scores[best_cat]

    return {
        "category": best_cat,
        "confidence": round(best_score, 4),
        "all_scores": {k: round(v, 4) for k, v in scores.items() if v > 0},
        "imagenet_top5": [(name, round(float(s), 4)) for _, name, s in decoded[:5]],
    }


def _predict_custom(img_path: str) -> dict:
    """Predict using custom-trained model."""
    _ensure_tf()
    from tensorflow.keras.preprocessing import image

    model = _get_custom_model()
    img = image.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    arr = image.img_to_array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)

    preds = model.predict(arr, verbose=0)[0]
    idx = int(np.argmax(preds))
    return {
        "category": CATEGORIES[idx],
        "confidence": round(float(preds[idx]), 4),
    }


# ═══════════════════════════════════════════════════════════════════════
# HEURISTIC DETECTION (calibrated against real product photos)
# ═══════════════════════════════════════════════════════════════════════

def _heuristic_detect(img_path: str) -> dict:
    """
    Improved heuristic detection using aspect ratio, color, texture,
    and upper-body garment features (neckline, sleeves, symmetry).
    """
    img = cv2.imread(img_path)
    if img is None:
        return {"category": "t-shirt", "confidence": 0.0}

    h, w = img.shape[:2]
    ar = w / h

    # Color analysis
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]

    avg_bright = float(np.mean(val))
    avg_sat = float(np.mean(sat))

    # Blue ratio (jeans indicator)
    blue_mask = (hue >= 90) & (hue <= 130) & (sat > 30)
    blue_ratio = float(np.sum(blue_mask)) / (h * w)

    # Texture
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    texture = float(np.std(gray))

    # Skin detection
    skin1 = cv2.inRange(hsv, np.array([0, 20, 70]), np.array([20, 255, 255]))
    skin2 = cv2.inRange(hsv, np.array([170, 20, 70]), np.array([180, 255, 255]))
    skin = skin1 | skin2
    skin_total = float(np.sum(skin > 0)) / (h * w)

    third = h // 3
    skin_bot = float(np.sum(skin[2*third:, :] > 0)) / (third * w + 1)

    # ── Upper-body garment detection ──────────────────────────────
    # These features help distinguish hoodies/jackets/shirts from pants

    def _has_upper_body_features(img, gray, h, w):
        """Detect features typical of tops: neckline, sleeves, width variation."""
        score = 0

        # 1. Neckline/collar detection: analyze top 20% of image
        top_region = gray[:h // 5, :]
        top_edges = cv2.Canny(top_region, 50, 150)
        top_edge_density = float(np.sum(top_edges > 0)) / (top_region.shape[0] * top_region.shape[1] + 1)

        # Tops often have high edge density at top (collar, neckline, hood)
        if top_edge_density > 0.08:
            score += 2

        # 2. Width variation: tops are wider at shoulders, narrower at waist
        # Compare width of non-background pixels at 25% vs 75% height
        quarter_row = gray[h // 4, :]
        three_quarter_row = gray[3 * h // 4, :]

        # Check for background (very bright or very dark uniform areas)
        bg_val = gray[0, 0]  # corner pixel as background reference
        bg_threshold = 30

        top_width = np.sum(np.abs(quarter_row.astype(int) - int(bg_val)) > bg_threshold)
        bot_width = np.sum(np.abs(three_quarter_row.astype(int) - int(bg_val)) > bg_threshold)

        # Tops: wider at shoulders than bottom (or similar width throughout)
        if top_width > 0 and bot_width > 0:
            width_ratio = top_width / (bot_width + 1)
            if width_ratio > 0.9:  # Shoulders >= waist width
                score += 2

        # 3. Horizontal symmetry: tops (especially hoodies) are very symmetric
        left_half = gray[:, :w // 2]
        right_half = cv2.flip(gray[:, w // 2:], 1)
        min_w = min(left_half.shape[1], right_half.shape[1])
        if min_w > 10:
            symmetry = 1.0 - float(np.mean(np.abs(
                left_half[:, :min_w].astype(float) - right_half[:, :min_w].astype(float)
            ))) / 255.0
            if symmetry > 0.85:
                score += 1

        # 4. Vertical edges (seams, zippers) — common in jackets/hoodies
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        center_third = sobel_x[:, w // 3: 2 * w // 3]
        center_vertical_edges = float(np.mean(np.abs(center_third)))
        if center_vertical_edges > 15:
            score += 1  # Zipper or center seam detected

        # 5. Check if top region has more detail/features than bottom
        # (tops have collars/hoods at top; pants are uniform throughout)
        top_half_std = float(np.std(gray[:h // 2, :]))
        bot_half_std = float(np.std(gray[h // 2:, :]))
        if top_half_std > bot_half_std * 1.1:
            score += 1

        return score

    upper_body_score = _has_upper_body_features(img, gray, h, w)

    # ── Decision tree ───────────────────────────────────────────────
    conf = 0.5  # base confidence

    # Strong blue → jeans
    if blue_ratio > 0.15:
        return {"category": "jeans", "confidence": min(0.85, conf + blue_ratio)}

    # Very wide → shoes
    if ar > 1.5:
        return {"category": "shoes", "confidence": 0.7}

    # Very tall images (ar < 0.6) — could be pants OR hoodie/jacket
    if ar < 0.6:
        if blue_ratio > 0.06:
            return {"category": "jeans", "confidence": 0.65}
        # Check for upper-body features before defaulting to pants
        if upper_body_score >= 3:
            if avg_bright < 100:
                return {"category": "jacket", "confidence": 0.65, "method": "heuristic"}
            return {"category": "t-shirt", "confidence": 0.60, "method": "heuristic"}
        return {"category": "pants", "confidence": 0.7}

    # Tall images (0.6-0.85) — bottoms usually, but check for tops
    if ar < 0.85:
        if blue_ratio > 0.06:
            return {"category": "jeans", "confidence": 0.6}
        if skin_bot > 0.35:
            return {"category": "shorts", "confidence": 0.6}
        # Upper-body garment check
        if upper_body_score >= 3:
            if avg_bright < 100:
                return {"category": "jacket", "confidence": 0.65, "method": "heuristic"}
            if texture > 45:
                return {"category": "shirt", "confidence": 0.60, "method": "heuristic"}
            return {"category": "t-shirt", "confidence": 0.55, "method": "heuristic"}
        return {"category": "pants", "confidence": 0.65}

    # Square/wide images (0.85+) → tops
    if avg_bright < 100:
        return {"category": "jacket", "confidence": 0.55}
    if texture > 55:
        return {"category": "shirt", "confidence": 0.55}

    return {"category": "t-shirt", "confidence": 0.5}


# ═══════════════════════════════════════════════════════════════════════
# HYBRID DETECTION (combines CNN + heuristics)
# ═══════════════════════════════════════════════════════════════════════

def _hybrid_detect(img_path: str) -> dict:
    """
    Combines CNN and heuristic detection for best results.

    Strategy:
    - If CNN confidence ≥ 40%, use CNN result
    - If CNN says t-shirt/jeans/shoes with any confidence, trust it (CNN is good at these)
    - Otherwise, use heuristic (better at pants vs shirts from aspect ratio)
    """
    cnn = _predict_cnn(img_path)
    heuristic = _heuristic_detect(img_path)

    cnn_cat = cnn["category"]
    cnn_conf = cnn["confidence"]
    heur_cat = heuristic["category"]

    # CNN is very confident → trust it
    if cnn_conf >= 0.4:
        # Exception: CNN often says "jacket" for bottom garments (sees lab_coat/suit/military_uniform)
        # If heuristic says it's a bottom garment, prefer heuristic
        if cnn_cat == "jacket" and heur_cat in ("pants", "jeans", "shorts"):
            return {
                "category": heur_cat,
                "confidence": round(max(heuristic["confidence"], 0.6), 4),
                "method": "heuristic_override",
            }
        return {
            "category": cnn_cat,
            "confidence": round(cnn_conf, 4),
            "method": "cnn",
        }

    # CNN has some signal for categories it's good at
    if cnn_cat in ("t-shirt", "jeans", "shoes") and cnn_conf >= 0.15:
        return {
            "category": cnn_cat,
            "confidence": round(cnn_conf, 4),
            "method": "cnn_low_conf",
        }

    # CNN and heuristic agree → high confidence
    if cnn_cat == heur_cat:
        return {
            "category": cnn_cat,
            "confidence": round(max(cnn_conf, heuristic["confidence"]), 4),
            "method": "consensus",
        }

    # Default: trust heuristic (better at aspect-ratio-based classification)
    return {
        "category": heur_cat,
        "confidence": round(heuristic["confidence"], 4),
        "method": "heuristic",
    }


# ═══════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════

def detect_clothing_category(image_path: str) -> str:
    """Detect clothing category. Returns category string."""
    result = detect_clothing_with_confidence(image_path)
    return result["category"]


def detect_clothing_with_confidence(image_path: str) -> dict:
    """
    Detect clothing category with confidence score.
    Returns: {"category": str, "confidence": float, ...}
    """
    if not Path(image_path).exists():
        return {"category": "t-shirt", "confidence": 0.0}

    # If TensorFlow is not available, use heuristic only
    if not TF_AVAILABLE:
        return _heuristic_detect(image_path)

    # Priority 1: Custom trained model
    custom = _get_custom_model()
    if custom is not None:
        return _predict_custom(image_path)

    # Priority 2: Hybrid CNN + heuristic
    return _hybrid_detect(image_path)
