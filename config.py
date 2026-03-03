"""
Configuration and Constants for COSMHOTEL Group
"""

# COSMHOTEL GROUP STRUCTURE
COSMHOTEL_GROUP = {
    "name": "COSMHOTEL Group",
    "code": "COSMHOTEL",
    "description": "Multi-property hotel and restaurant group",
    "currency": "EUR",
}

# Hotel Properties (belong to COSMHOTEL Group)
HOTEL_PROPERTIES = {
    "porto_greco": {
        "name": "Porto Greco Beach & Village",
        "code": "PG",
        "group": "COSMHOTEL",
        "type": "Resort",
        "location": "Porto Greco, Greece",
        "rooms": 291,
        "capacity_guests": 585,
        "restaurants": ["White Rabbit", "El Mi Bar", "Black Pepper"],
        "opening_date": "2015",
    },
    "theros": {
        "name": "Theros Resort",
        "code": "TR",
        "group": "COSMHOTEL",
        "type": "Resort",
        "location": "Theros, Greece",
        "rooms": 250,
        "capacity_guests": 500,
        "restaurants": [],
        "opening_date": "2018",
    },
    "apollon": {
        "name": "Apollon Hotel",
        "code": "AH",
        "group": "COSMHOTEL",
        "type": "Hotel",
        "location": "Apollon, Greece",
        "rooms": 180,
        "capacity_guests": 360,
        "restaurants": [],
        "opening_date": "2016",
    },
    "axel_crete": {
        "name": "Axel Crete Villaggio",
        "code": "AC",
        "group": "COSMHOTEL",
        "type": "Villaggio",
        "location": "Crete, Greece",
        "rooms": 220,
        "capacity_guests": 440,
        "restaurants": [],
        "opening_date": "2017",
    },
    "axel_mykonos": {
        "name": "Axel Beach Mykonos",
        "code": "AM",
        "group": "COSMHOTEL",
        "type": "Beach Resort",
        "location": "Mykonos, Greece",
        "rooms": 200,
        "capacity_guests": 400,
        "restaurants": [],
        "opening_date": "2019",
    },
}

# Restaurant (standalone but part of COSMHOTEL ecosystem)
RESTAURANTS = {
    "kingscorpio": {
        "name": "KingScorpio Restaurant",
        "code": "KS",
        "group": "COSMHOTEL",
        "type": "Fine Dining Restaurant",
        "location": "Athens, Greece",
        "covers_capacity": 150,
        "opening_date": "2020",
    },
}

# All Hotels (for iteration)
HOTELS = list(HOTEL_PROPERTIES.values())

# All Venues (hotels + restaurants)
ALL_VENUES = list(HOTEL_PROPERTIES.values()) + list(RESTAURANTS.values())

# User Roles with Group awareness
ROLES = {
    "admin": {
        "label": "Administrator",
        "permissions": ["view", "edit", "upload", "delete", "group_view"],
        "description": "Full access across all properties",
        "group_access": "COSMHOTEL",
    },
    "group_director": {
        "label": "Group Director",
        "permissions": ["view", "compare", "export", "group_view", "group_analytics"],
        "description": "View all COSMHOTEL properties with consolidated analytics",
        "group_access": "COSMHOTEL",
    },
    "hotel_manager": {
        "label": "Hotel Manager",
        "permissions": ["view", "upload", "hotel_compare"],
        "description": "View and manage own hotel only",
        "group_access": "own_hotel",
    },
    "accountant": {
        "label": "Accountant",
        "permissions": ["view", "export", "reports", "group_view"],
        "description": "Financial reports across all properties",
        "group_access": "COSMHOTEL",
    },
    "viewer": {
        "label": "Viewer",
        "permissions": ["view"],
        "description": "Read-only access to own hotel",
        "group_access": "own_hotel",
    },
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
COLOR_GROUP = "#6C5CE7"  # Purple for group-level metrics
COLOR_HOTEL = "#00B894"  # Green for individual hotels

# Default pagination
ITEMS_PER_PAGE = 50

# GROUP REPORTING CONFIGURATION
GROUP_KPI_METRICS = [
    "total_revenue",
    "average_occupancy_rate",
    "revenue_per_available_room",  # RevPAR
    "total_guests",
    "average_check_value",
    "employee_cost_ratio",
]

# Revenue Categories (used across all properties)
REVENUE_CATEGORIES = [
    "ROOM-ΔΩMATIO",
    "ALL INCLUSIVE",
    "BREAKFAST-ΠΡΩΪNO",
    "LUNCH-ΓEYMA",
    "DINNER-ΔEIΠNO",
    "F&B OTHER",
    "MISC REVENUE",
]

# Hotel Codes Map (for data file mapping)
HOTEL_CODES = {
    "PG": "porto_greco",
    "TR": "theros",
    "AH": "apollon",
    "AC": "axel_crete",
    "AM": "axel_mykonos",
    "KS": "kingscorpio",
}

# Reverse mapping
HOTEL_CODE_FROM_KEY = {v: k for k, v in HOTEL_CODES.items()}
