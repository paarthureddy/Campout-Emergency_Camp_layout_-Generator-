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
    layout_colors = {
        1: (128, 0, 0), 2: (50, 50, 50), 3: (255, 255, 0), 4: (0, 0, 128)
    }
    for class_id, color in layout_colors.items():
        mask = (layout_grid == class_id)
        layout_overlay[mask] = color
    layout_alpha = 0.8
    return cv2.addWeighted(layout_overlay, layout_alpha, base_image, 1 - layout_alpha, 0)

def render_blueprint(original_image, layout, segmented_mask):
    """
    Blueprint Renderer Module.
    Overlays the semantic segmentation mask and the generated layout grid.
    Input: original_image (BGR), layout (dict), segmented_mask (numpy array)
    Output: Rendered image (BGR NumPy array).
    """
    layout_grid = layout["layout_grid"]
    h, w = layout_grid.shape
    
    if original_image.shape[:2] != (h, w):
        original_image = cv2.resize(original_image, (w, h))
        
    if segmented_mask.shape[:2] != (h, w):
        segmented_mask = cv2.resize(segmented_mask, (w, h), interpolation=cv2.INTER_NEAREST)

    base_image = create_semantic_overlay(original_image, segmented_mask)
    rendered_image = create_layout_overlay(base_image, layout_grid)
    
    return rendered_image
