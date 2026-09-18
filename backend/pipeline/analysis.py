import numpy as np

# LoveDA class labels (must match segmentation.py)
CLASS_NAMES = {
    0: "Background",
    1: "Building",
    2: "Road",
    3: "Water",
    4: "Barren",
    5: "Forest",
    6: "Agriculture",
}

# Classes where camp structures CAN be placed
BUILDABLE_CLASSES = {4, 6}   # Barren + Agriculture

# Classes that are strict no-build zones
EXCLUSION_CLASSES  = {3, 5}  # Water + Forest


def analyze_terrain(segmented_mask: np.ndarray) -> dict:
    """
    Processes the segmented mask and returns:
      - buildable_mask        : binary uint8 array (1 = buildable)
      - buildable_area_pixels : int
      - unsuitable_zones_detected : int
      - class_breakdown       : {class_name: {"pixels": int, "percent": float}}
    """
    total_pixels = segmented_mask.size

    # ── Per-class breakdown ───────────────────────────────────────────────────
    class_breakdown = {}
    for cid, name in CLASS_NAMES.items():
        px = int(np.sum(segmented_mask == cid))
        class_breakdown[name] = {
            "pixels":  px,
            "percent": round(px / total_pixels * 100, 2),
            "buildable": cid in BUILDABLE_CLASSES,
        }

    # ── Buildable mask ────────────────────────────────────────────────────────
    buildable_mask   = np.isin(segmented_mask, list(BUILDABLE_CLASSES)).astype(np.uint8)
    buildable_pixels = int(np.sum(buildable_mask))

    return {
        "buildable_mask":            buildable_mask,
        "buildable_area_pixels":     buildable_pixels,
        "unsuitable_zones_detected": int(total_pixels - buildable_pixels),
        "class_breakdown":           class_breakdown,
        "total_pixels":              total_pixels,
    }
