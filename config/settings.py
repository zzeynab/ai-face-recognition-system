"""Application-wide configuration values."""

FACE_POSES = [
    {
        "name": "front",
        "title": "روبرو",
        "instruction": "مستقیم به دوربین نگاه کنید.",
    },
    {
        "name": "left",
        "title": "سمت چپ",
        "instruction": "سر خود را کمی به سمت چپ بچرخانید.",
    },
    {
        "name": "right",
        "title": "سمت راست",
        "instruction": "سر خود را کمی به سمت راست بچرخانید.",
    },
    {
        "name": "up",
        "title": "بالا",
        "instruction": "سر خود را کمی به سمت بالا بگیرید.",
    },
    {
        "name": "down",
        "title": "پایین",
        "instruction": "سر خود را کمی به سمت پایین بگیرید.",
    },
]

POSE_NAMES = [pose["name"] for pose in FACE_POSES]
POSE_DETAILS = {pose["name"]: pose for pose in FACE_POSES}

# Similarity at or above this value means the face is probably already known.
DUPLICATE_THRESHOLD = 0.70
RECOGNITION_THRESHOLD = 0.60

# Landmark-based head-pose thresholds. They can be tuned after camera testing.
YAW_THRESHOLD = 0.22
PITCH_UP_THRESHOLD = 0.38
PITCH_DOWN_THRESHOLD = 0.64

# Thresholds used when InsightFace exposes pose values in degrees.
POSE_YAW_DEGREES = 18
POSE_PITCH_DEGREES = 12

# If the labels for left/right are reversed during camera testing, set this True.
REVERSE_YAW_DIRECTION = False

MIN_FACE_SIZE = 110
MIN_DETECTION_CONFIDENCE = 0.75
POSE_STABLE_FRAMES = 8

FACE_DATASET_PATH = "dataset"

# Backward-compatible alias for older imports.
FACE_ANGLES = FACE_POSES
