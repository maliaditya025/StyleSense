from __future__ import annotations

"""
Styling tips generator.
Produces detailed, dynamic styling advice based on outfit composition,
occasion, and user profile. Uses rule-based text templates.
"""


# ─── Accessory Suggestions ────────────────────────────────────────

ACCESSORY_TEMPLATES = {
    "formal": {
        "male": [
            "A classic silver or leather watch adds sophistication",
            "Consider a silk pocket square to add a touch of personality",
            "Minimalist cufflinks in silver or gold finish",
            "A leather belt matching your shoe color ties the look together",
        ],
        "female": [
            "Elegant pearl or diamond stud earrings complement formal attire",
            "A delicate gold necklace adds subtle elegance",
            "A structured clutch in a neutral tone completes the look",
            "Simple bangles or a tennis bracelet add refined sparkle",
        ],
        "unspecified": [
            "A classic watch is a timeless formal accessory",
            "Keep jewelry minimal and elegant for formal occasions",
            "A quality leather belt pulls the outfit together",
        ],
    },
    "casual": {
        "male": [
            "Layer with a casual beaded bracelet or leather band",
            "Sunglasses with UV protection add both style and function",
            "A canvas or braided belt keeps it relaxed",
            "A minimalist backpack or messenger bag for everyday carry",
        ],
        "female": [
            "Layered necklaces create a trendy bohemian vibe",
            "Oversized sunglasses are both chic and practical",
            "A crossbody bag keeps the look easy and hands-free",
            "Hoop earrings add effortless style to any casual outfit",
        ],
        "unspecified": [
            "Sunglasses are a versatile casual accessory",
            "A comfortable watch suits any casual look",
            "A canvas tote or messenger bag is practical and stylish",
        ],
    },
    "party": {
        "male": [
            "A bold statement watch elevates your party look",
            "Consider a chain necklace for some edge",
            "A stylish ring adds personality without overdoing it",
        ],
        "female": [
            "Statement earrings are the perfect party conversation starter",
            "A sparkling clutch bag catches the light beautifully",
            "Layered rings create an eye-catching detail",
        ],
        "unspecified": [
            "One bold statement piece can transform your entire look",
            "Metallic accessories catch the light at evening events",
        ],
    },
    "work": {
        "male": [
            "A professional watch signals attention to detail",
            "A quality leather briefcase completes the professional image",
            "Minimalist tie clip in silver or gold",
        ],
        "female": [
            "Structured tote bag in a neutral color is office-appropriate",
            "Small stud earrings maintain professionalism",
            "A quality silk scarf can add color to a neutral outfit",
        ],
        "unspecified": [
            "Keep accessories professional and understated for the workplace",
            "A quality bag or briefcase shows attention to detail",
        ],
    },
    "date": {
        "male": [
            "A scented cologne (applied sparingly) adds allure",
            "A quality watch shows sophistication",
            "Consider a subtle bracelet for a modern touch",
        ],
        "female": [
            "A signature perfume creates a memorable impression",
            "Delicate jewelry that catches candlelight is perfect for dates",
            "A chic small handbag keeps you looking put-together",
        ],
        "unspecified": [
            "A subtle fragrance adds a personal touch for dates",
            "Keep accessories elegant and not distracting",
        ],
    },
}

# ─── Footwear Suggestions ─────────────────────────────────────────

FOOTWEAR_TEMPLATES = {
    "formal": {
        "male": ["Classic Oxford shoes in brown or black", "Polished Derby shoes", "Loafers for a slightly relaxed formal look"],
        "female": ["Pointed-toe pumps in nude or black", "Elegant stiletto heels", "Classic ballet flats for comfort with style"],
        "unspecified": ["Classic leather shoes in a neutral color", "Polished dress shoes"],
    },
    "casual": {
        "male": ["Clean white sneakers are versatile and modern", "Canvas slip-ons for a laid-back vibe", "Leather boots add rugged charm"],
        "female": ["White sneakers pair with almost anything", "Ankle boots add edge to casual outfits", "Strappy sandals for warm weather"],
        "unspecified": ["White sneakers are the ultimate casual shoe", "Canvas shoes for relaxed comfort"],
    },
    "party": {
        "male": ["Chelsea boots give a sleek party-ready look", "Suede loafers for a refined touch"],
        "female": ["Strappy heels make a statement", "Metallic shoes catch the light on the dance floor"],
        "unspecified": ["Statement shoes can elevate your party outfit"],
    },
    "work": {
        "male": ["Oxford or Derby shoes in brown or black", "Monk strap shoes for a modern professional look"],
        "female": ["Block heels are both professional and comfortable", "Loafers offer elegance with all-day comfort"],
        "unspecified": ["Professional leather shoes in neutral tones"],
    },
    "date": {
        "male": ["Clean Chelsea boots show effort and style", "Polished loafers for a smart-casual date"],
        "female": ["Heeled boots add confidence and height", "Elegant sandals for a dinner date"],
        "unspecified": ["Well-maintained shoes show you pay attention to details"],
    },
}

# ─── Do's and Don'ts ──────────────────────────────────────────────

DOS_TEMPLATES = {
    "formal": [
        "Ensure your clothes are well-pressed and wrinkle-free",
        "Match your belt color with your shoe color",
        "Keep patterns subtle — pin stripes or solid colors work best",
        "Ensure proper fit — tailoring makes all the difference",
    ],
    "casual": [
        "Mix textures (denim + cotton, leather + knit) for visual interest",
        "Don't be afraid to experiment with color combinations",
        "Roll sleeves for a relaxed, put-together vibe",
        "Layer pieces to add depth to simple outfits",
    ],
    "party": [
        "One statement piece is enough — don't overdo it",
        "Ensure your outfit allows comfortable movement for dancing",
        "Add a pop of color or metallic for visual impact",
    ],
    "work": [
        "Keep it professional but express personality through accessories",
        "Ensure clothes are clean, pressed, and well-fitted",
        "Neutral colors are always safe for the office",
    ],
    "date": [
        "Wear something that makes you feel confident",
        "Pay attention to grooming details",
        "Choose clothes that represent your personal style authentically",
    ],
}

DONTS_TEMPLATES = {
    "formal": [
        "Avoid overly bright or neon colors for formal events",
        "Don't mix too many patterns in one outfit",
        "Avoid wearing sneakers with formal attire",
        "Don't forget to check for loose threads or missing buttons",
    ],
    "casual": [
        "Avoid wearing wrinkled or stained clothing even casually",
        "Don't wear too many logos or branded items at once",
        "Avoid flip-flops outside of beach settings",
    ],
    "party": [
        "Don't overdress for a casual gathering",
        "Avoid wearing uncomfortable shoes you can't dance in",
        "Don't wear overpowering cologne or perfume",
    ],
    "work": [
        "Avoid casual wear like joggers or graphic tees",
        "Don't wear overly revealing or distracting clothing",
        "Avoid strong fragrances in office settings",
    ],
    "date": [
        "Don't try too hard — authenticity is attractive",
        "Avoid wearing brand new shoes that might cause discomfort",
        "Don't wear too much cologne or perfume",
    ],
}

# ─── Grooming Tips ────────────────────────────────────────────────

GROOMING_TEMPLATES = {
    "male": [
        "Keep facial hair well-groomed or cleanly shaved",
        "Use a quality moisturizer for healthy-looking skin",
        "Keep nails trimmed and clean",
        "A subtle, quality cologne applied to pulse points",
        "Ensure hair is styled and neat",
    ],
    "female": [
        "A natural-looking makeup palette complements most outfits",
        "Keep nails manicured — they're noticed more than you think",
        "Light, moisturized skin creates a healthy glow",
        "A signature scent creates lasting impressions",
        "Style hair to complement your outfit's neckline",
    ],
    "unspecified": [
        "Good hygiene is the foundation of any great outfit",
        "Keep nails clean and well-maintained",
        "Moisturized skin looks healthy under any lighting",
        "A subtle fragrance adds a personal finishing touch",
        "Ensure your hair is styled and well-maintained",
    ],
}


def generate_styling_tips(
    outfit_items: list[dict],
    occasion: str = "casual",
    user_profile: dict | None = None,
) -> dict:
    """
    Generate comprehensive styling tips for an outfit.

    Returns:
        {
            "tips": [...],
            "accessories": [...],
            "footwear": [...],
            "dos": [...],
            "donts": [...],
            "grooming": [...],
        }
    """
    gender = (user_profile or {}).get("gender", "unspecified")
    if gender not in ("male", "female"):
        gender = "unspecified"

    # Ensure occasion is valid
    if occasion not in ACCESSORY_TEMPLATES:
        occasion = "casual"

    # Gather tips from each category
    accessories = ACCESSORY_TEMPLATES.get(occasion, {}).get(gender, [])[:3]
    footwear = FOOTWEAR_TEMPLATES.get(occasion, {}).get(gender, [])[:2]
    dos = DOS_TEMPLATES.get(occasion, [])[:3]
    donts = DONTS_TEMPLATES.get(occasion, [])[:3]
    grooming = GROOMING_TEMPLATES.get(gender, [])[:3]

    # Generate color-specific tips
    color_tips = []
    colors = [item.get("color_name", "") for item in outfit_items]
    categories = [item.get("category", "") for item in outfit_items]

    dark_colors = [c for c in colors if c and "Dark" in c or c in ("Black", "Navy", "Charcoal", "Burgundy", "Maroon")]
    light_colors = [c for c in colors if c and c in ("White", "Cream", "Beige", "Light Gray")]

    if dark_colors and light_colors:
        color_tips.append("Great contrast between light and dark pieces — this creates visual balance")
    elif len(dark_colors) == len(colors):
        color_tips.append("All-dark outfits look sleek — add a pop of color with accessories")
    elif len(light_colors) == len(colors):
        color_tips.append("An all-light palette feels fresh — a dark belt or shoes ground the look")

    # Combine all tips
    general_tips = color_tips

    # Category-specific tips
    if "jacket" in categories:
        general_tips.append("Make sure the jacket fits well in the shoulders for a sharp silhouette")
    if "jeans" in categories and occasion != "formal":
        general_tips.append("Dark wash jeans are more versatile and dress up better than light wash")

    return {
        "tips": general_tips[:3] if general_tips else ["This is a well-balanced outfit combination!"],
        "accessories": accessories,
        "footwear": footwear,
        "dos": dos,
        "donts": donts,
        "grooming": grooming,
    }
