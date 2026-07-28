import torch
import numpy as np
import os
import sys
# Add parent directory to path to allow importing models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.unet import UNet
import cv2

def segment_terrain(image_array):
    """
    Handles segmenting satellite imagery using the trained U-Net model.
    Input: image_array (BGR numpy array from OpenCV)
    Output: segmented mask (numpy array of predicted class indices 0-6)
    """
    # Check if the trained model exists
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "unet_loveda.pth")
    
    if os.path.exists(model_path):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = UNet(n_channels=3, n_classes=7).to(device)
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval()
        
        # Preprocess the image (BGR to RGB, scale to 0-1, reshape)
        img_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        img_tensor = torch.from_numpy(img_rgb).permute(2, 0, 1).float() / 255.0
        img_tensor = img_tensor.unsqueeze(0).to(device)
        
        # Inference
        with torch.no_grad():
            outputs = model(img_tensor)
            # Get class with highest probability
            _, predicted = torch.max(outputs, 1)
            
        mask = predicted.squeeze().cpu().numpy()
        return mask
    else:
        # Fallback to random mock mask for demonstration if model isn't trained yet
        # Mock mostly Barren (4) and Agriculture (6) for buildable zones, and some Water (3)
        print("Warning: unet_loveda.pth not found. Using simulated segmentation mask.")
        h, w = image_array.shape[:2]
        mock_mask = np.random.choice([0, 1, 2, 3, 4, 5, 6], size=(h, w), p=[0.05, 0.05, 0.05, 0.1, 0.35, 0.05, 0.35])
        return mock_mask
