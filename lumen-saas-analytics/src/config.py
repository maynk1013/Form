"""Scenario constants for Lumen Workspace.

Books are closed through September 2026. The trailing-twelve-month retention
window is October 2025 through September 2026.
"""

from datetime import date

SEED = 42
N_ACCOUNTS = 720

HISTORY_START = date(2023, 1, 1)
AS_OF_MONTH = date(2026, 9, 1)
SIGNUP_START = date(2023, 1, 1)
SIGNUP_END = date(2026, 9, 28)
DATE_DIM_START = date(2022, 1, 1)
DATE_DIM_END = date(2026, 12, 31)
TTM_START = date(2025, 10, 1)

# id, name, price per seat, tier rank, base monthly hazard, adoption baseline
PLANS = [
    (1, "Starter", 39, 1, 0.048, 46),
    (2, "Growth", 89, 2, 0.030, 58),
    (3, "Scale", 179, 3, 0.017, 66),
    (4, "Enterprise", 399, 4, 0.008, 74),
]

# id, name, group, base monthly spend, hazard multiplier
CHANNELS = [
    (1, "Organic", "Owned", 5_000, 0.82),
    (2, "Content", "Owned", 12_000, 0.94),
    (3, "Partner", "Partner", 9_000, 0.88),
    (4, "Paid Search", "Paid", 42_000, 1.28),
    (5, "Outbound", "Paid", 26_000, 1.06),
]

INDUSTRIES = [
    ("Software", 0.90, 18),
    ("Healthcare", 1.05, 12),
    ("Retail", 1.15, 14),
    ("Financial Services", 0.85, 14),
    ("Manufacturing", 1.00, 16),
    ("Education", 1.22, 12),
    ("Media", 1.10, 14),
]

REGIONS = [
    ("North America", 0.95, 55),
    ("EMEA", 1.05, 28),
    ("APAC", 1.08, 17),
]

# band, min seats, max seats, hazard multiplier, mix weight
BANDS = [
    ("1-20", 4, 12, 1.28, 30),
    ("21-100", 12, 35, 1.00, 35),
    ("101-500", 25, 70, 0.82, 22),
    ("501+", 40, 100, 0.68, 13),
]

PLAN_MIX = {
    "1-20": [("Starter", 62), ("Growth", 33), ("Scale", 5)],
    "21-100": [("Starter", 12), ("Growth", 48), ("Scale", 32), ("Enterprise", 8)],
    "101-500": [("Growth", 12), ("Scale", 52), ("Enterprise", 36)],
    "501+": [("Scale", 22), ("Enterprise", 78)],
}

PLAN_ORDER = ["Starter", "Growth", "Scale", "Enterprise"]

ADJECTIVES = [
    "Northline", "Copper", "Harbor", "Kindred", "Fieldnote", "Brightpath",
    "Cedar", "Halcyon", "Redwood", "Silverline", "Marlow", "Sable", "Vesper",
    "Arden", "Woven", "Pebble", "Lark", "Kinship", "Oak", "Fable",
]
PLACES = ["North", "West", "East", "River", "Bay", "Peak", "Grove", "Metro", "Coast", "Hill"]
NOUNS = [
    "Labs", "Health", "Goods", "Logistics", "Studio", "Collective", "Systems",
    "Supply", "Clinic", "Retail", "Media", "Works", "Foods", "Energy", "Transit",
]
