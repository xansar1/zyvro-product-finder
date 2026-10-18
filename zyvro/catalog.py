"""Deterministic fictional catalog for public demonstrations — NO real Amazon listings."""
from __future__ import annotations
from random import Random

CATALOG = {
    "Desk & Office": ["Foldable laptop riser", "Magnetic cable organizer", "Desk drawer organizer", "Laptop sleeve", "Wireless mouse pad", "Felt desk mat", "USB cable holder", "Adjustable reading lamp", "Sticky note dispenser", "Noise dampening desk pad"],
    "Kitchen & Home": ["Reusable food storage bags", "Silicone spatula set", "Collapsible colander", "Spice storage jars", "Compact sink organizer", "Mini handheld whisk", "Non-slip drawer liner", "Reusable produce bags", "Bamboo utensil tray", "Dish drying mat"],
    "Fitness": ["Resistance band set", "Yoga stretch strap", "Grip strength trainer", "Travel yoga mat", "Foam massage roller", "Exercise sliders", "Workout towel", "Insulated shaker bottle", "Jump rope", "Adjustable ankle weights"],
    "Pet Care": ["Pet grooming glove", "Travel water bowl", "Reusable lint remover", "Pet brush", "Paw cleaning cup", "Cat enrichment ball", "Pet travel mat", "Slow feeder bowl", "Leash organizer", "Pet food scoop"],
    "Travel": ["Packing cube set", "Passport wallet", "Luggage tag pack", "Travel cable pouch", "Foldable wash bag", "Compact toiletries case", "Neck support pillow", "Shoe storage pouch", "Reusable bottle carrier", "Travel laundry bag"],
    "Beauty & Care": ["Makeup brush holder", "Silicone face scrubber", "Reusable cotton pads", "Travel cosmetic bag", "Headband set", "Skincare fridge organizer", "Hair styling clips", "Nail care kit", "Mirror compact", "Makeup sponge holder"],
    "Electronics": ["USB-C cable sleeve", "Phone stand", "Portable device pouch", "Magnetic phone holder", "Screen cleaning kit", "Charging dock mat", "Cable labeling kit", "Laptop webcam cover", "Tablet sleeve", "Foldable headphones stand"],
}

def demo_catalog() -> list[dict]:
    """Stable synthetic records; never return real product URLs or claim market observations."""
    rng = Random(20261018)
    records = []
    for category, names in CATALOG.items():
        for i, name in enumerate(names):
            records.append({
                "id": f"DEMO-{len(records)+1:03}", "title": name,
                "category": category, "price": float(rng.randrange(199, 4299, 50)),
                "currency": "INR", "rating": round(rng.uniform(3.4, 4.9), 1),
                "reviews": rng.randint(15, 4200), "url": None,
                "source": "Fictional sample", "sponsored": False,
            })
    return records

def select_demo(keyword: str = "", category: str = "All") -> list[dict]:
    """Searches existing fictional records only; doesn't fabricate keyword-based listings."""
    keywords = keyword.strip().lower().split()
    return [r for r in demo_catalog()
            if (category == "All" or r["category"] == category)
            and (not keywords or all(token in (r['title']+' '+r['category']).lower() for token in keywords))]
