"""Scenario constants for Aurora Home & Living.

The sales window stops at the latest closed month. January–September is the
comparable year-to-date period used for 2025 vs 2026.
"""

from datetime import date

SEED = 42
N_ORDERS = 24_000
N_CUSTOMERS = 4_500

SALES_START = date(2025, 1, 1)
SALES_END = date(2026, 9, 30)
DATE_DIM_START = date(2024, 1, 1)
DATE_DIM_END = date(2026, 12, 31)

# Independent monthly revenue plan for an average store-mix month before
# seasonality and trend. Tuned so company-wide attainment lands near the plan,
# while individual stores miss or beat it because their plan share differs
# from their demand share.
COMPANY_MONTHLY_BASE = 650_000

# Demand weights drive where shoppers actually buy.
# Target shares are the annual real-estate plan and sum to 1.
# Miami and Minneapolis are over-planned relative to demand.
# Austin and Los Angeles are under-planned relative to demand.
STORES = [
    # id, name, city, state, region, opened, sq_ft, demand_weight, target_share
    (1, "Pike Place Home", "Seattle", "WA", "West", "2014-04-12", 16200, 1.25, 0.090),
    (2, "Mission Atelier", "San Francisco", "CA", "West", "2015-08-01", 14800, 1.15, 0.085),
    (3, "Abbot Kinney Home", "Los Angeles", "CA", "West", "2016-02-20", 17100, 1.35, 0.095),
    (4, "LoHi Living", "Denver", "CO", "West", "2018-06-15", 13900, 0.95, 0.080),
    (5, "South Congress House", "Austin", "TX", "South", "2017-03-09", 15100, 1.20, 0.070),
    (6, "Knox Henderson", "Dallas", "TX", "South", "2015-11-02", 16800, 1.05, 0.085),
    (7, "Inman Park Home", "Atlanta", "GA", "South", "2016-09-18", 14400, 0.90, 0.075),
    (8, "Design District", "Miami", "FL", "South", "2019-01-25", 15800, 0.72, 0.090),
    (9, "SoHo Residence", "New York", "NY", "Northeast", "2013-05-06", 12400, 1.40, 0.110),
    (10, "Newbury Home", "Boston", "MA", "Northeast", "2014-10-11", 11800, 1.05, 0.080),
    (11, "Lincoln Park Living", "Chicago", "IL", "Midwest", "2015-04-04", 17600, 1.15, 0.085),
    (12, "North Loop Goods", "Minneapolis", "MN", "Midwest", "2018-08-30", 14900, 0.62, 0.055),
]

# sku, name, category, subcategory, cost_ratio, list_price, relative weight inside category
PRODUCTS = [
    ("FUR-100", "Linen Sectional Sofa", "Furniture", "Seating", 0.58, 1899, 1.2),
    ("FUR-110", "Oak Dining Table", "Furniture", "Tables", 0.56, 1499, 1.0),
    ("FUR-120", "Walnut Writing Desk", "Furniture", "Tables", 0.55, 899, 1.1),
    ("FUR-130", "Boucle Lounge Chair", "Furniture", "Seating", 0.57, 749, 1.3),
    ("FUR-140", "Upholstered Queen Bed", "Furniture", "Bedroom", 0.60, 1299, 0.9),
    ("FUR-150", "Oak Media Console", "Furniture", "Storage", 0.54, 679, 1.0),
    ("LGT-200", "Arc Floor Lamp", "Lighting", "Floor", 0.42, 329, 1.2),
    ("LGT-210", "Opal Glass Pendant", "Lighting", "Ceiling", 0.44, 189, 1.3),
    ("LGT-220", "Brass Table Lamp", "Lighting", "Table", 0.40, 149, 1.4),
    ("LGT-230", "Linen Wall Sconce", "Lighting", "Wall", 0.41, 119, 1.0),
    ("LGT-240", "Outdoor Lantern Pair", "Lighting", "Outdoor", 0.46, 159, 0.8),
    ("TEX-300", "Stonewashed Linen Duvet", "Textiles", "Bedding", 0.38, 189, 1.3),
    ("TEX-310", "Wool Throw Blanket", "Textiles", "Throws", 0.36, 129, 1.2),
    ("TEX-320", "Performance Velvet Pillow", "Textiles", "Pillows", 0.34, 49, 1.5),
    ("TEX-330", "Percale Sheet Set", "Textiles", "Bedding", 0.37, 159, 1.2),
    ("TEX-340", "Jute Area Rug 8x10", "Textiles", "Rugs", 0.48, 499, 0.8),
    ("TEX-350", "Flatweave Hall Runner", "Textiles", "Rugs", 0.45, 179, 1.0),
    ("TEX-360", "Blackout Curtain Panel", "Textiles", "Window", 0.40, 89, 1.1),
    ("DEC-400", "Ceramic Table Vase", "Decor", "Accents", 0.42, 42, 1.4),
    ("DEC-410", "Framed Abstract Print", "Decor", "Art", 0.40, 129, 1.1),
    ("DEC-420", "Handwoven Basket Set", "Decor", "Storage", 0.44, 79, 1.0),
    ("DEC-430", "Marble Bookends", "Decor", "Accents", 0.46, 59, 0.9),
    ("DEC-440", "Scented Candle Trio", "Decor", "Fragrance", 0.32, 48, 1.6),
    ("DEC-450", "Oak Picture Frame Set", "Decor", "Art", 0.43, 39, 1.2),
    ("KIT-500", "Stoneware Dinner Set", "Kitchen", "Dining", 0.50, 169, 1.2),
    ("KIT-510", "Cast Iron Dutch Oven", "Kitchen", "Cookware", 0.52, 149, 1.1),
    ("KIT-520", "Linen Napkin Set", "Kitchen", "Linens", 0.36, 36, 1.3),
    ("KIT-530", "Acacia Serving Board", "Kitchen", "Serve", 0.48, 58, 1.0),
    ("KIT-540", "Glass Storage Canisters", "Kitchen", "Storage", 0.47, 44, 1.1),
    ("KIT-550", "Matte Cutlery Set", "Kitchen", "Dining", 0.51, 89, 1.0),
]

CATEGORY_WEIGHT = {
    "Furniture": 0.14,
    "Lighting": 0.16,
    "Textiles": 0.28,
    "Decor": 0.22,
    "Kitchen": 0.20,
}

DISCOUNT_OPTIONS = {
    "Furniture": [(0.00, 18), (0.10, 22), (0.15, 24), (0.20, 20), (0.30, 16)],
    "Lighting": [(0.00, 45), (0.10, 35), (0.15, 15), (0.20, 5)],
    "Textiles": [(0.00, 30), (0.10, 30), (0.15, 22), (0.20, 12), (0.30, 6)],
    "Decor": [(0.00, 40), (0.10, 35), (0.15, 15), (0.20, 10)],
    "Kitchen": [(0.00, 50), (0.10, 30), (0.15, 15), (0.20, 5)],
}

RETURN_P = {
    "Furniture": 0.11,
    "Lighting": 0.040,
    "Textiles": 0.055,
    "Decor": 0.045,
    "Kitchen": 0.025,
}

SEGMENT_RETURN_MULT = {
    "Consumer": 1.20,
    "Corporate": 0.50,
    "Home Office": 0.95,
}

SEGMENTS = [("Consumer", 55), ("Corporate", 30), ("Home Office", 15)]

FIRST_NAMES = [
    "Ava", "Noah", "Mia", "Liam", "Sofia", "Ethan", "Amelia", "Lucas", "Chloe",
    "Owen", "Priya", "Mateo", "Hannah", "Julian", "Nora", "Adrian", "Leila",
    "Gabriel", "Elena", "Isaac", "Fatima", "Leo", "Maya", "Caleb", "Aisha",
    "Nina", "Omar", "Ruby", "Seth", "Grace", "Jonah", "Hana", "Felix", "Imani",
]
LAST_NAMES = [
    "Bennett", "Shah", "Nguyen", "Patel", "Garcia", "Kim", "Cohen", "Silva",
    "Rossi", "Andersen", "Ibrahim", "Kowalski", "Sato", "Dubois", "Okeke",
    "Murphy", "Hassan", "Berg", "Almeida", "Chen", "Wright", "Diallo", "Novak",
]


def season_factor(month: int) -> float:
    """Multiplicative seasonal index. November and December are the peak."""
    return {
        1: 0.84,
        2: 0.90,
        6: 0.94,
        7: 0.93,
        8: 0.96,
        11: 1.50,
        12: 1.62,
    }.get(month, 1.0)


def trend_factor(day: date) -> float:
    """About 0.8% compound growth per month from January 2025."""
    months = (day.year - 2025) * 12 + (day.month - 1)
    return 1 + 0.008 * months
