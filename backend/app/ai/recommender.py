from __future__ import annotations

"""
Pro-level outfit recommendation engine.

Uses a weighted multi-dimensional scoring system across 6 axes:
  1. Occasion appropriateness  (weight: 3)
  2. Body type suitability     (weight: 2)
  3. Weather compatibility     (weight: 3)
  4. Color compatibility       (weight: 4)  ← most important
  5. Time of day               (weight: 1)
  6. Location type             (weight: 2)

Final score = Σ (dimension_score × weight) / Σ weights × 100

Supported:
  - 7 occasions: casual, formal, party, work, date, vacation, gym
  - 6 body types: slim, athletic, average, heavy, petite, tall
  - 4 weather types: hot, warm, cold, rainy
  - 4 time periods: morning, afternoon, evening, night
  - 2 location types: indoor, outdoor
"""

import itertools
import colorsys
from typing import Optional


# ═══════════════════════════════════════════════════════════════════
# CATEGORY DEFINITIONS
# ═══════════════════════════════════════════════════════════════════

TOPS = {"shirt", "t-shirt", "jacket"}
BOTTOMS = {"pants", "jeans", "shorts", "skirt"}
FOOTWEAR = {"shoes"}
ACCESSORIES_CAT = {"accessories"}
FULL_BODY = {"dress"}


# ═══════════════════════════════════════════════════════════════════
# 1. OCCASION RULES (Dictionary-based rule engine)
# ═══════════════════════════════════════════════════════════════════

OCCASION_RULES = {
    "casual": {
        "allowed_tops": {"t-shirt", "shirt", "jacket"},
        "allowed_bottoms": {"jeans", "pants", "shorts"},
        "avoid": set(),
        "preferred_colors": [],  # any color
        "boost": 0.05,
    },
    "formal": {
        "allowed_tops": {"shirt", "jacket"},
        "allowed_bottoms": {"pants"},
        "avoid": {"shorts", "t-shirt"},
        "preferred_colors": ["black", "navy", "grey", "white", "beige"],
        "boost": 0.15,
    },
    "party": {
        "allowed_tops": {"shirt", "t-shirt", "jacket"},
        "allowed_bottoms": {"jeans", "pants", "skirt"},
        "avoid": set(),
        "preferred_colors": ["black", "red", "metallic", "dark"],
        "boost": 0.10,
    },
    "work": {
        "allowed_tops": {"shirt"},
        "allowed_bottoms": {"pants", "jeans"},
        "avoid": {"shorts"},
        "preferred_colors": ["neutral", "pastel", "navy", "white", "grey"],
        "boost": 0.12,
    },
    "date": {
        "allowed_tops": {"shirt", "t-shirt"},
        "allowed_bottoms": {"jeans", "pants", "skirt"},
        "avoid": {"shorts"},
        "preferred_colors": ["dark", "navy", "beige", "red", "maroon"],
        "boost": 0.10,
    },
    "vacation": {
        "allowed_tops": {"t-shirt", "shirt"},
        "allowed_bottoms": {"shorts", "jeans", "pants"},
        "avoid": {"jacket"},
        "preferred_colors": ["light", "pastel", "tropical"],
        "boost": 0.08,
    },
    "gym": {
        "allowed_tops": {"t-shirt"},
        "allowed_bottoms": {"shorts", "pants"},
        "avoid": {"shirt", "jacket", "jeans", "skirt", "dress"},
        "preferred_colors": [],
        "boost": 0.05,
    },
}


def _occasion_score(items: list[dict], occasion: str) -> float:
    """Score outfit suitability for the occasion (0-1)."""
    rules = OCCASION_RULES.get(occasion, OCCASION_RULES["casual"])
    categories = {item["category"] for item in items}
    allowed = rules["allowed_tops"] | rules["allowed_bottoms"]

    score = 0.5  # Base

    # Bonus for items in allowed categories
    for cat in categories:
        if cat in allowed:
            score += rules["boost"]

    # Heavy penalty for avoided categories
    for cat in categories:
        if cat in rules["avoid"]:
            score -= 0.40

    # Color preference bonus
    if rules["preferred_colors"]:
        color_names = [item.get("color_name", "").lower() for item in items if item.get("color_name")]
        for cn in color_names:
            if any(pref in cn for pref in rules["preferred_colors"]):
                score += 0.05

    return max(0.0, min(score, 1.0))


# ═══════════════════════════════════════════════════════════════════
# 2. BODY TYPE LOGIC
# ═══════════════════════════════════════════════════════════════════

BODY_TYPE_RULES = {
    "slim": {
        "good_fits": {"jacket", "shirt", "pants", "jeans"},
        "boost": {"jacket": 0.10},   # Layering adds presence
        "prefer_colors": [],          # Light colors, horizontal patterns
        "avoid": set(),
    },
    "athletic": {
        "good_fits": {"t-shirt", "shirt", "jeans", "pants"},
        "boost": {"t-shirt": 0.10},   # Shows physique
        "prefer_colors": [],
        "avoid": set(),
    },
    "average": {
        "good_fits": {"shirt", "t-shirt", "pants", "jeans", "shorts"},
        "boost": {},
        "prefer_colors": [],
        "avoid": set(),
    },
    "heavy": {
        "good_fits": {"shirt", "jacket", "pants", "jeans"},
        "boost": {"jacket": 0.08, "shirt": 0.08},  # Structured tops
        "prefer_colors": ["black", "navy", "dark grey", "dark"],
        "avoid": set(),
    },
    "petite": {
        "good_fits": {"shirt", "t-shirt", "pants", "jeans", "skirt"},
        "boost": {"pants": 0.06},  # High-waist elongates
        "prefer_colors": [],       # Monochrome preferred
        "avoid": {"jacket"},       # Long oversized coats
    },
    "tall": {
        "good_fits": {"shirt", "t-shirt", "jacket", "pants", "jeans", "shorts"},
        "boost": {"jacket": 0.06},
        "prefer_colors": [],
        "avoid": set(),
    },
}


def _body_type_score(items: list[dict], body_type: str) -> float:
    """Score outfit based on body type compatibility (0-1)."""
    rules = BODY_TYPE_RULES.get(body_type, BODY_TYPE_RULES["average"])
    score = 0.5

    for item in items:
        cat = item["category"]

        # Good fit bonus
        if cat in rules["good_fits"]:
            score += 0.08

        # Category-specific boost
        score += rules.get("boost", {}).get(cat, 0)

        # Penalty for avoided categories
        if cat in rules.get("avoid", set()):
            score -= 0.15

    # Color preference for body type (e.g., heavy prefers dark)
    if rules["prefer_colors"]:
        color_names = [item.get("color_name", "").lower() for item in items if item.get("color_name")]
        for cn in color_names:
            if any(pref in cn for pref in rules["prefer_colors"]):
                score += 0.05

    return max(0.0, min(score, 1.0))


# ═══════════════════════════════════════════════════════════════════
# 3. WEATHER SCORING
# ═══════════════════════════════════════════════════════════════════

WEATHER_RULES = {
    "hot": {
        "preferred": {"t-shirt", "shorts"},
        "avoid": {"jacket"},
        "prefer_colors": ["light", "white", "beige", "pastel"],
    },
    "warm": {
        "preferred": {"t-shirt", "shirt", "shorts", "jeans"},
        "avoid": set(),
        "prefer_colors": [],
    },
    "cold": {
        "preferred": {"jacket", "shirt", "pants", "jeans"},
        "avoid": {"shorts"},
        "require_layer": True,
        "prefer_colors": ["dark", "black", "navy"],
    },
    "rainy": {
        "preferred": {"jacket", "pants", "jeans"},
        "avoid": {"shorts"},
        "prefer_colors": ["dark"],
    },
}


def _weather_score(items: list[dict], weather: str) -> float:
    """Score outfit for weather suitability (0-1)."""
    if not weather or weather not in WEATHER_RULES:
        return 0.6  # Neutral default

    rules = WEATHER_RULES[weather]
    categories = {item["category"] for item in items}
    score = 0.5

    # Preferred categories
    for cat in categories:
        if cat in rules["preferred"]:
            score += 0.10

    # Avoided categories
    for cat in categories:
        if cat in rules.get("avoid", set()):
            score -= 0.25

    # Cold requires layering — bonus for jacket
    if rules.get("require_layer") and "jacket" in categories:
        score += 0.15

    # Color preference
    if rules.get("prefer_colors"):
        color_names = [item.get("color_name", "").lower() for item in items if item.get("color_name")]
        for cn in color_names:
            if any(pref in cn for pref in rules["prefer_colors"]):
                score += 0.04

    return max(0.0, min(score, 1.0))


# ═══════════════════════════════════════════════════════════════════
# 4. COLOR COMPATIBILITY SCORE (most heavily weighted)
# ═══════════════════════════════════════════════════════════════════

NEUTRAL_COLORS = {"black", "white", "grey", "gray", "beige", "cream", "navy",
                  "charcoal", "tan", "khaki", "light gray", "dark gray"}

COMPLEMENTARY_PAIRS = [
    ("blue", "orange"),
    ("red", "green"),
    ("yellow", "purple"),
    ("navy", "beige"),
    ("black", "white"),
    ("maroon", "beige"),
    ("teal", "coral"),
]


def _named_color_score(color1: str, color2: str) -> float:
    """
    Score color compatibility using named colors (0-1).
    Uses rules: neutral+any=10, same=8, complementary=9, clash=-10.
    """
    c1 = color1.lower().strip()
    c2 = color2.lower().strip()

    # Neutral + anything = great
    if c1 in NEUTRAL_COLORS or c2 in NEUTRAL_COLORS:
        return 1.0

    # Same color family
    if c1 == c2:
        return 0.8

    # Complementary pairs
    for pair in COMPLEMENTARY_PAIRS:
        if (c1 in pair[0] and c2 in pair[1]) or (c2 in pair[0] and c1 in pair[1]):
            return 0.9
        # Partial match (e.g. "dark blue" contains "blue")
        if (pair[0] in c1 and pair[1] in c2) or (pair[1] in c1 and pair[0] in c2):
            return 0.85

    # Both bright/neon = clash
    neon = {"neon", "fluorescent", "bright"}
    if any(n in c1 for n in neon) and any(n in c2 for n in neon):
        return 0.1

    # Default: moderate compatibility
    return 0.5


def _hex_to_hsl(hex_color: str) -> tuple:
    """Convert hex color to HSL."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return (0, 0, 0.5)
    r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h * 360, s, l)


def _color_harmony_score(items: list[dict]) -> float:
    """
    Combined color scoring: uses named colors when available,
    falls back to hex-based HSL harmony analysis.
    """
    # First try named color matching (more accurate)
    color_names = [item.get("color_name", "") for item in items if item.get("color_name")]
    if len(color_names) >= 2:
        scores = []
        for i in range(len(color_names)):
            for j in range(i + 1, len(color_names)):
                scores.append(_named_color_score(color_names[i], color_names[j]))

        named_score = sum(scores) / len(scores) if scores else 0.5

        # Penalty for 3+ bright colors together
        bright_count = sum(1 for c in color_names if any(b in c.lower() for b in ["red", "orange", "yellow", "pink", "neon"]))
        if bright_count >= 3:
            named_score -= 0.15

        return max(0.0, min(named_score, 1.0))

    # Fallback to hex color harmony
    hex_colors = [item["primary_color"] for item in items if item.get("primary_color")]
    if len(hex_colors) < 2:
        return 0.5

    hsls = [_hex_to_hsl(c) for c in hex_colors]
    hues = [h for h, s, l in hsls]
    best_score = 0.0

    for i in range(len(hues)):
        for j in range(i + 1, len(hues)):
            diff = abs(hues[i] - hues[j]) % 360
            if diff > 180:
                diff = 360 - diff

            if diff < 15:          # Monochrome
                score = 0.85
            elif 15 <= diff <= 45: # Analogous
                score = 0.80
            elif 150 <= diff <= 180:  # Complementary
                score = 0.90
            elif 100 <= diff <= 140:  # Triadic
                score = 0.75
            elif 60 <= diff <= 90:    # Split-complementary
                score = 0.70
            else:
                score = 0.4

            best_score = max(best_score, score)

    # Neutral detection by HSL
    for h, s, l in hsls:
        if s < 0.1 or l < 0.15 or l > 0.9:
            best_score = max(best_score, 0.80)

    return best_score


# ═══════════════════════════════════════════════════════════════════
# 5. TIME OF DAY SCORING
# ═══════════════════════════════════════════════════════════════════

TIME_RULES = {
    "morning": {
        "prefer_colors": ["light", "white", "pastel", "beige", "cream"],
        "avoid_colors": ["black"],
    },
    "afternoon": {
        "prefer_colors": [],  # flexible
        "avoid_colors": [],
    },
    "evening": {
        "prefer_colors": ["dark", "navy", "black", "maroon", "grey"],
        "avoid_colors": ["neon"],
    },
    "night": {
        "prefer_colors": ["black", "dark", "bold", "red", "navy"],
        "avoid_colors": ["pastel", "light"],
    },
}


def _time_of_day_score(items: list[dict], time_of_day: str) -> float:
    """Score outfit for time of day (0-1)."""
    if not time_of_day or time_of_day not in TIME_RULES:
        return 0.6  # Neutral default

    rules = TIME_RULES[time_of_day]
    color_names = [item.get("color_name", "").lower() for item in items if item.get("color_name")]

    if not color_names:
        return 0.5

    score = 0.5

    for cn in color_names:
        # Preferred color bonus
        if any(pref in cn for pref in rules.get("prefer_colors", [])):
            score += 0.08
        # Avoided color penalty
        if any(avoid in cn for avoid in rules.get("avoid_colors", [])):
            score -= 0.10

    return max(0.0, min(score, 1.0))


# ═══════════════════════════════════════════════════════════════════
# 6. LOCATION SCORING
# ═══════════════════════════════════════════════════════════════════

def _location_score(items: list[dict], location: str) -> float:
    """Score outfit for location type (0-1)."""
    if not location:
        return 0.6

    categories = {item["category"] for item in items}

    if location == "outdoor":
        score = 0.5
        # Comfort and durability preferred
        if "shoes" in categories:
            score += 0.10
        if "jacket" in categories:
            score += 0.10  # Protection
        if "shorts" in categories or "t-shirt" in categories:
            score += 0.05  # Comfortable
        return min(score, 1.0)

    elif location == "indoor":
        score = 0.5
        # Style-focused, less weather dependency
        if "shirt" in categories:
            score += 0.10
        if "jacket" in categories:
            score += 0.05  # Can layer indoors
        return min(score, 1.0)

    return 0.6


# ═══════════════════════════════════════════════════════════════════
# GENDER SCORE
# ═══════════════════════════════════════════════════════════════════

def _gender_score(items: list[dict], gender: str) -> float:
    """Basic gender compatibility."""
    categories = {item["category"] for item in items}
    if gender == "male" and "skirt" in categories:
        return 0.4
    if gender == "male" and "dress" in categories:
        return 0.3
    return 0.7


# ═══════════════════════════════════════════════════════════════════
# COMBINATION GENERATOR
# ═══════════════════════════════════════════════════════════════════

def _generate_combinations(clothes: list[dict]) -> list[list[dict]]:
    """
    Generate valid outfit combinations.
    Each outfit: top + bottom (+ optional shoes).
    Also generates layered combos (jacket + inner top + bottom).
    """
    tops = [c for c in clothes if c["category"] in TOPS]
    bottoms = [c for c in clothes if c["category"] in BOTTOMS]
    shoes = [c for c in clothes if c["category"] in FOOTWEAR]
    dresses = [c for c in clothes if c["category"] in FULL_BODY]

    combos = []

    # Top + Bottom combinations
    for top in tops:
        for bottom in bottoms:
            combo = [top, bottom]
            if shoes:
                combo.append(shoes[0])
            combos.append(combo)

    # Dress combinations
    for dress in dresses:
        combo = [dress]
        if shoes:
            combo.append(shoes[0])
        combos.append(combo)

    # Layered combos: jacket + inner top + bottom
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


# ═══════════════════════════════════════════════════════════════════
# QUICK TIPS GENERATOR
# ═══════════════════════════════════════════════════════════════════

def _generate_quick_tips(items: list[dict], occasion: str, weather: str = "", time_of_day: str = "") -> list[str]:
    """Generate 2-3 context-aware styling tips."""
    tips = []
    categories = {item["category"] for item in items}

    # Occasion tips
    if occasion == "formal" and "shirt" in categories:
        tips.append("Tuck in your shirt for a polished formal look")
    if occasion == "casual" and "jeans" in categories:
        tips.append("Roll up the cuffs for a relaxed casual vibe")
    if occasion == "date":
        tips.append("Add a subtle fragrance to complete the look")
    if occasion == "party":
        tips.append("Statement accessories can make this outfit stand out")
    if occasion == "work" and "shirt" in categories:
        tips.append("A tucked-in shirt with a belt creates a professional silhouette")
    if occasion == "vacation":
        tips.append("Pack light — this outfit works for multiple occasions")
    if occasion == "gym":
        tips.append("Choose moisture-wicking fabrics for maximum comfort")

    # Weather tips
    if weather == "hot":
        tips.append("Light fabrics will keep you cool in the heat")
    if weather == "cold" and "jacket" in categories:
        tips.append("Layer up — a well-fitted jacket is essential in cold weather")
    if weather == "rainy":
        tips.append("Avoid suede shoes in rainy weather")

    # Time tips
    if time_of_day in ("evening", "night"):
        tips.append("Dark tones create a sophisticated evening look")
    if time_of_day == "morning":
        tips.append("Fresh, light colors set a positive tone for the day")

    # Jacket tip
    if "jacket" in categories and not any("jacket" in t or "layer" in t for t in tips):
        tips.append("A well-fitted jacket elevates any outfit instantly")

    # Color tips
    colors = [item.get("color_name", "") for item in items]
    if any("Dark" in c for c in colors if c):
        tips.append("Dark tones create a sleek, slimming silhouette")

    return tips[:3] if tips else ["This combination has great color balance!"]


# ═══════════════════════════════════════════════════════════════════
# MAIN SCORING ENGINE
# ═══════════════════════════════════════════════════════════════════

# Scoring weights (from user's spec)
WEIGHTS = {
    "occasion": 3,
    "body_type": 2,
    "weather": 3,
    "color": 4,     # Most important
    "time": 1,
    "location": 2,
    "gender": 1,
}
TOTAL_WEIGHT = sum(WEIGHTS.values())


def generate_outfit_recommendations(
    clothes: list[dict],
    user_profile: dict,
    occasion: str = "casual",
    weather: str = "",
    time_of_day: str = "",
    location: str = "",
    top_n: int = 3,
) -> list[dict]:
    """
    Main recommendation function — pro-level weighted scoring.

    Args:
        clothes: List of clothing dicts with id, category, primary_color, color_name, image_url
        user_profile: Dict with gender, body_type, style_preference
        occasion: Target occasion (casual, formal, party, work, date, vacation, gym)
        weather: Weather condition (hot, warm, cold, rainy)
        time_of_day: Time period (morning, afternoon, evening, night)
        location: Location type (indoor, outdoor)
        top_n: Number of top outfits to return

    Returns:
        List of dicts: { "items": [...], "score": float, "tips": [...] }
    """
    if len(clothes) < 2:
        return []

    combos = _generate_combinations(clothes)

    if not combos:
        combos = [clothes[:2]]

    gender = user_profile.get("gender", "unspecified")
    body_type = user_profile.get("body_type", "average")

    scored_outfits = []

    for combo in combos:
        # Calculate all 6 dimension scores + gender
        s_occasion = _occasion_score(combo, occasion)
        s_body = _body_type_score(combo, body_type)
        s_weather = _weather_score(combo, weather)
        s_color = _color_harmony_score(combo)
        s_time = _time_of_day_score(combo, time_of_day)
        s_location = _location_score(combo, location)
        s_gender = _gender_score(combo, gender)

        # Weighted score (0-100)
        raw = (
            s_occasion * WEIGHTS["occasion"]
            + s_body * WEIGHTS["body_type"]
            + s_weather * WEIGHTS["weather"]
            + s_color * WEIGHTS["color"]
            + s_time * WEIGHTS["time"]
            + s_location * WEIGHTS["location"]
            + s_gender * WEIGHTS["gender"]
        )
        overall = (raw / TOTAL_WEIGHT) * 100

        # Generate context-aware tips
        tips = _generate_quick_tips(combo, occasion, weather, time_of_day)

        scored_outfits.append({
            "items": combo,
            "score": round(overall, 1),
            "tips": tips,
            "breakdown": {
                "color": round(s_color * 100, 1),
                "occasion": round(s_occasion * 100, 1),
                "body_type": round(s_body * 100, 1),
                "weather": round(s_weather * 100, 1),
                "time": round(s_time * 100, 1),
                "location": round(s_location * 100, 1),
                "gender": round(s_gender * 100, 1),
            },
        })

    # Sort by score descending, return top N
    scored_outfits.sort(key=lambda x: x["score"], reverse=True)
    return scored_outfits[:top_n]
