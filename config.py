"""
Configuration and Constants
"""

# Hotel Names
HOTELS = [
    "Porto Greco Beach & Village",
    "Theros Resort",
    "Apollon Hotel",
    "Axel Crete Villaggio",
    "Axel Beach Mykonos",
    "KingScorpio Restaurant",
]

# User Roles
ROLES = {
    "admin": {"label": "Administrator", "permissions": ["view", "edit", "upload", "delete"], "description": "Full access, can upload files"},
    "group_director": {"label": "Group Director", "permissions": ["view", "compare", "export"], "description": "View all hotels"},
    "hotel_manager": {"label": "Hotel Manager", "permissions": ["view", "upload"], "description": "View own hotel only"},
    "accountant": {"label": "Accountant", "permissions": ["view", "export", "reports"], "description": "Financial reports only"},
    "viewer": {"label": "Viewer", "permissions": ["view"], "description": "Read-only access"},
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
