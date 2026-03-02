"""
Configuration and Constants
"""

# Hotel Names
HOTELS = [
    "Porto Greco",
    "Athens",
    "Mykonos",
    "Santorini",
]

# User Roles
ROLES = {
    "admin": {"label": "Administrator", "permissions": ["view", "edit", "upload", "delete"]},
    "manager": {"label": "Manager", "permissions": ["view", "upload"]},
    "viewer": {"label": "Viewer", "permissions": ["view"]},
}

# Greek Month Names
GREEK_MONTHS = {
    1: "ΙΑΝΟΥΑΡΙΟΣ",
    2: "ΦΕΒΡΟΥΑΡΙΟΣ",
    3: "ΜΑΡΤΙΟΣ",
    4: "ΑΠΡΙΛΙΟΣ",
    5: "ΜΑΙΟΣ",
    6: "ΙΟΥΝΙΟΣ",
    7: "ΙΟΥΛΙΟΣ",
    8: "ΑΥΓΟΥΣΤΟΣ",
    9: "ΣΕΠΤΕΜΒΡΙΟΣ",
    10: "ΟΚΤΩΒΡΙΟΣ",
    11: "ΝΟΕΜΒΡΙΟΣ",
    12: "ΔΕΚΕΜΒΡΙΟΣ",
}

MONTH_MAP = {v: k for k, v in GREEK_MONTHS.items()}

# Colors
COLOR_SUCCESS = "#00D96F"
COLOR_ERROR = "#FF4757"
COLOR_WARNING = "#FFA502"
COLOR_INFO = "#0066CC"

# Default pagination
ITEMS_PER_PAGE = 50
