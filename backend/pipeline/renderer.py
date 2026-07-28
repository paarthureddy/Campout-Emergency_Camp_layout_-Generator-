import cv2
import numpy as np

def render_blueprint(original_image, layout):
    """
    Blueprint Renderer Module.
    Overlays the generated layout grid on the original satellite image using OpenCV.
    Input: original_image (BGR NumPy array), layout dictionary containing 'layout_grid'.
    Output: Rendered image (BGR NumPy array).
    """
    layout_grid = layout["layout_grid"]
    
    # Ensure original_image is the same size as layout_grid
    # If not, resize it to match the grid
    h, w = layout_grid.shape
    if original_image.shape[:2] != (h, w):
        original_image = cv2.resize(original_image, (w, h))
        
    # Create an overlay image
    overlay = original_image.copy()
    
    # Define colors in BGR
    # 0: Unbuildable (Transparent), 1: Shelter (Blue), 2: Road (Gray), 3: Water (Cyan), 4: Medical (Red)
    colors = {
        1: (255, 0, 0),     # Shelter
        2: (150, 150, 150), # Road
        3: (255, 255, 0),   # Water
        4: (0, 0, 255)      # Medical
    }
    
    for class_id, color in colors.items():
        # Find where this class is located in the grid
        mask = (layout_grid == class_id)
        # Apply color to the overlay
        overlay[mask] = color
        
    # Blend the original image and the overlay (Alpha blending)
    alpha = 0.6 # Transparency factor
    rendered_image = cv2.addWeighted(overlay, alpha, original_image, 1 - alpha, 0)
    
    return rendered_image
