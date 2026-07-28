import numpy as np

def analyze_terrain(segmented_mask):
    """
    Processes the segmented mask (NumPy array) from the U-Net model 
    and identifies the buildable area.
    
    Assuming LoveDA classes (0-indexed or 1-indexed):
    We define 'Barren' and 'Agriculture' as buildable.
    For standard LoveDA: 
    Background=0, Building=1, Road=2, Water=3, Barren=4, Forest=5, Agriculture=6
    So buildable_classes = [4, 6]
    """
    buildable_classes = [4, 6]
    
    # Create a binary mask where 1 is buildable and 0 is unbuildable
    buildable_mask = np.isin(segmented_mask, buildable_classes).astype(np.uint8)
    
    # Compute total buildable area in pixels
    # (In a real system, we would convert this to square meters using satellite resolution)
    buildable_pixels = np.sum(buildable_mask)
    
    return {
        "buildable_mask": buildable_mask,
        "buildable_area_pixels": int(buildable_pixels),
        "unsuitable_zones_detected": int(segmented_mask.size - buildable_pixels)
    }
