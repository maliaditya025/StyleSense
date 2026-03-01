from __future__ import annotations

"""
Outfit recommendation engine.
Uses a hybrid rule-based approach with scoring across multiple dimensions:
  1. Color harmony (complementary, analogous, triadic, monochrome)
  2. Gender compatibility
  3. Body type suitability
  4. Occasion appropriateness

Generates all valid combinations of tops + bottoms (+ optional shoes/accessories),
scores each, and returns the top N outfits.
"""

import itertools
import colorsys
from typing import Optional


# ─── Color Harmony Rules ───────────────────────────────────────────

def _hex_to_hsl(hex_color: str) -> tuple:
    """Convert hex color to HSL (hue in degrees, saturation, lightness)."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return (0, 0, 0.5)
    r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360, s, l)


def _color_harmony_score(colors: list[str]) -> float:
    """
    Score the color harmony of a set of hex colors.
    Higher score = better harmony (0 to 1).
    """
    if not colors or len(colors) < 2:
        return 0.5

    hsls = [_hex_to_hsl(c) for c in colors if c]
    hues = [h for h, s, l in hsls]

    if len(hues) < 2:
        return 0.5

    best_score = 0.0

    for i in range(len(hues)):
        for j in range(i + 1, len(hues)):
            h1, h2 = hues[i], hues[j]
            diff = abs(h1 - h2) % 360
            if diff > 180:
                diff = 360 - diff

            # Monochrome: same hue family (diff < 15°)
            if diff < 15:
                score = 0.85

            # Analogous: adjacent hues (15-45°)
            elif 15 <= diff <= 45:
                score = 0.80

            # Complementary: opposite hues (150-180°)
            elif 150 <= diff <= 180:
                score = 0.90

            # Triadic: 120° apart (100-140°)
            elif 100 <= diff <= 140:
                score = 0.75

            # Split-complementary (60-90°)
            elif 60 <= diff <= 90:
                score = 0.70

            else:
                score = 0.4  # Clashing colors

            best_score = max(best_score, score)

    # Neutral colors always go well
    neutrals = {"Black", "White", "Gray", "Beige", "Cream", "Charcoal", "Light Gray", "Dark Gray", "Tan", "Khaki"}
    # Check lightness — very dark or very bright colors are often neutrals
    for h, s, l in hsls:
        if s < 0.1 or l < 0.15 or l > 0.9:
            best_score = max(best_score, 0.80)

    return best_score


# ─── Category Rules ────────────────────────────────────────────────

TOPS = {"shirt", "t-shirt", "jacket"}
BOTTOMS = {"pants", "jeans", "shorts", "skirt"}
FOOTWEAR = {"shoes"}
ACCESSORIES_CAT = {"accessories"}
FULL_BODY = {"dress"}

# Occasion-appropriate categories
OCCASION_RULES = {
    "formal": {
        "preferred_tops": {"shirt"},
        "preferred_bottoms": {"pants"},
        "avoid": {"shorts", "t-shirt"},
        "boost": 0.15,
    },
    "casual": {
        "preferred_tops": {"t-shirt", "shirt"},
        "preferred_bottoms": {"jeans", "pants", "shorts"},
        "avoid": set(),
        "boost": 0.05,
    },
    "party": {
        "preferred_tops": {"shirt", "t-shirt"},
        "preferred_bottoms": {"jeans", "pants", "skirt"},
        "avoid": set(),
        "boost": 0.10,
    },
    "work": {
        "preferred_tops": {"shirt"},
        "preferred_bottoms": {"pants"},
        "avoid": {"shorts"},
        "boost": 0.12,
    },
    "date": {
        "preferred_tops": {"shirt", "t-shirt"},
        "preferred_bottoms": {"jeans", "pants", "skirt"},
        "avoid": {"shorts"},
        "boost": 0.10,
    },
}

# ─── Body Type Rules ──────────────────────────────────────────────

BODY_TYPE_RULES = {
    "slim": {
        "good_fits": {"jacket", "shirt", "pants", "jeans"},
        "boost": {"jacket": 0.08},  # Layers add presence
    },
    "athletic": {
        "good_fits": {"t-shirt", "shirt", "jeans", "pants"},
        "boost": {"t-shirt": 0.08},  # Shows physique
    },
    "average": {
        "good_fits": {"shirt", "t-shirt", "pants", "jeans"},
        "boost": {},
    },
    "plus-size": {
        "good_fits": {"shirt", "jacket", "pants", "jeans"},
        "boost": {"jacket": 0.06, "shirt": 0.06},  # Structured pieces
    },
}


def _occasion_score(items: list[dict], occasion: str) -> float:
    """Score the outfit's suitability for a given occasion."""
    rules = OCCASION_RULES.get(occasion, OCCASION_RULES["casual"])
    categories = {item["category"] for item in items}

    score = 0.5  # Base

    # Bonus for preferred categories
    for cat in categories:
        if cat in rules["preferred_tops"] or cat in rules["preferred_bottoms"]:
            score += rules["boost"]

    # Penalty for avoided categories
    for cat in categories:
        if cat in rules["avoid"]:
            score -= 0.40  # Increased penalty for avoided items

    return max(0, min(score, 1.0))


def _body_type_score(items: list[dict], body_type: str) -> float:
    """Score the outfit based on body type compatibility."""
    rules = BODY_TYPE_RULES.get(body_type, BODY_TYPE_RULES["average"])

    score = 0.5
    for item in items:
        cat = item["category"]
        if cat in rules["good_fits"]:
            score += 0.10
        score += rules.get("boost", {}).get(cat, 0)

    return max(0, min(score, 1.0))


def _gender_score(items: list[dict], gender: str) -> float:
    """Basic gender compatibility — all items are gender-neutral by default."""
    # In a production system, clothing items would have a gender tag
    # For now, skirts get a small penalty for male profiles
    categories = {item["category"] for item in items}

    if gender == "male" and "skirt" in categories:
        return 0.4
    if gender == "male" and "dress" in categories:
        return 0.3

    return 0.7  # Neutral base


def _generate_combinations(clothes: list[dict]) -> list[list[dict]]:
    """
    Generate valid outfit combinations.
    Each outfit must have at least one top + one bottom, OR one full-body item.
    Optionally includes shoes and accessories.
    """
    tops = [c for c in clothes if c["category"] in TOPS]
    bottoms = [c for c in clothes if c["category"] in BOTTOMS]
    shoes = [c for c in clothes if c["category"] in FOOTWEAR]
    accessories = [c for c in clothes if c["category"] in ACCESSORIES_CAT]
    dresses = [c for c in clothes if c["category"] in FULL_BODY]

    combos = []

    # Top + Bottom combinations
    for top in tops:
        for bottom in bottoms:
            combo = [top, bottom]

            # Optionally add shoes (pick best color match)
            if shoes:
                combo.append(shoes[0])  # Just pick the first for now

            combos.append(combo)

    # Dress combinations
    for dress in dresses:
        combo = [dress]
        if shoes:
            combo.append(shoes[0])
        combos.append(combo)

    # If we have jackets, create layered combos too
    jackets = [c for c in clothes if c["category"] == "jacket"]
    non_jacket_tops = [c for c in tops if c["category"] != "jacket"]

    for jacket in jackets:
        for inner in non_jacket_tops:
            for bottom in bottoms:
                combo = [jacket, inner, bottom]
                if shoes:
                    combo.append(shoes[0])
                combos.append(combo)

    return combos


def generate_outfit_recommendations(
    clothes: list[dict],
    user_profile: dict,
    occasion: str = "casual",
    top_n: int = 3,
) -> list[dict]:
    """
    Main recommendation function.
    Generates outfit combinations, scores each one, and returns the top N.

    Args:
        clothes: List of clothing item dicts with id, category, primary_color, etc.
        user_profile: Dict with gender, body_type, style_preference
        occasion: Target occasion (casual, formal, party, work, date)
        top_n: Number of top outfits to return

    Returns:
        List of dicts: { "items": [...], "score": float, "tips": [...] }
    """
    if len(clothes) < 2:
        return []

    combos = _generate_combinations(clothes)

    if not combos:
        # Fallback: just pair first two items
        combos = [clothes[:2]]

    scored_outfits = []

    for combo in combos:
        # Extract colors for harmony scoring
        colors = [item["primary_color"] for item in combo if item.get("primary_color")]

        # Calculate sub-scores
        harmony = _color_harmony_score(colors)
        occasion_s = _occasion_score(combo, occasion)
        body_s = _body_type_score(combo, user_profile.get("body_type", "average"))
        gender_s = _gender_score(combo, user_profile.get("gender", "unspecified"))

        # Weighted overall score (0-100)
        overall = (
            harmony * 0.35 +
            occasion_s * 0.25 +
            body_s * 0.20 +
            gender_s * 0.20
        ) * 100

        # Generate quick tips based on the outfit
        tips = _generate_quick_tips(combo, occasion)

        scored_outfits.append({
            "items": combo,
            "score": round(overall, 1),
            "tips": tips,
            "breakdown": {
                "color_harmony": round(harmony * 100, 1),
                "occasion": round(occasion_s * 100, 1),
                "body_type": round(body_s * 100, 1),
                "gender": round(gender_s * 100, 1),
            },
        })

    # Sort by score descending and return top N
    scored_outfits.sort(key=lambda x: x["score"], reverse=True)
    return scored_outfits[:top_n]


def _generate_quick_tips(items: list[dict], occasion: str) -> list[str]:
    """Generate 2-3 quick styling tips for the outfit."""
    tips = []
    categories = {item["category"] for item in items}

    if occasion == "formal" and "shirt" in categories:
        tips.append("Tuck in your shirt for a polished formal look")
    if occasion == "casual" and "jeans" in categories:
        tips.append("Roll up the cuffs for a relaxed casual vibe")
    if "jacket" in categories:
        tips.append("A well-fitted jacket elevates any outfit instantly")
    if occasion == "date":
        tips.append("Add a subtle fragrance to complete the look")
    if occasion == "party":
        tips.append("Statement accessories can make this outfit stand out")

    # Color-based tips
    colors = [item.get("color_name", "") for item in items]
    if any("Dark" in c for c in colors if c):
        tips.append("Dark tones create a sleek, slimming silhouette")
    if any(c in ("White", "Cream", "Beige") for c in colors if c):
        tips.append("Light colors keep the look fresh and approachable")

    return tips[:3] if tips else ["This combination has great color balance!"]
