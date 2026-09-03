import cv2
import numpy as np

def create_semantic_overlay(original_image, segmented_mask):
    semantic_overlay = np.zeros_like(original_image)
    semantic_colors = {
        0: (255, 255, 255), 1: (0, 0, 255), 2: (0, 255, 255),
        3: (255, 0, 0), 4: (211, 0, 148), 5: (0, 255, 0), 6: (179, 204, 255)
    }
    for class_id, color in semantic_colors.items():
        mask = (segmented_mask == class_id)
        semantic_overlay[mask] = color
    alpha = 0.4
    return cv2.addWeighted(semantic_overlay, alpha, original_image, 1 - alpha, 0)

def create_layout_overlay(base_image, layout_grid):
    layout_overlay = base_image.copy()
    # Use bright, highly visible BGR colors for the camp layout
    layout_colors = {
        1: (0, 165, 255),    # Tents: Bright Orange
        2: (255, 255, 255),  # Roads: White
        3: (0, 0, 255),      # Medical: Bright Red
        4: (255, 255, 0)     # Water Points: Cyan
    }
    for class_id, color in layout_colors.items():
        mask = (layout_grid == class_id)
        layout_overlay[mask] = color
    layout_alpha = 0.85
    return cv2.addWeighted(layout_overlay, layout_alpha, base_image, 1 - layout_alpha, 0)

def render_blueprint(original_image, layout, segmented_mask):
    """
    Blueprint Renderer Module.
    Overlays the generated rehabilitation layout strictly on top of the original uploaded image.
    Input: original_image (BGR), layout (dict), segmented_mask (numpy array)
    Output: Rendered image (BGR NumPy array).
    """
    layout_grid = layout["layout_grid"]
    h, w = layout_grid.shape
    
    if original_image.shape[:2] != (h, w):
        original_image = cv2.resize(original_image, (w, h))
        
    # We deliberately DO NOT overlay the semantic segmentation mask anymore, 
    # so the user sees the original pristine satellite image as the base.
    base_image = original_image.copy()
    
    # Draw the rehabilitation camp layout on top of the base image
    rendered_image = create_layout_overlay(base_image, layout_grid)
    
    return rendered_image
