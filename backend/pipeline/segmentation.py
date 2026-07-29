import torch
import numpy as np
import os
import sys
# Add parent directory to path to allow importing models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.unet import UNet
from models.deeplabv3 import DeepLabV3Plus
import cv2

def segment_terrain(image_array, model_name="unet"):
    """
    Handles segmenting satellite imagery using the trained DL model.
    Input: image_array (BGR numpy array from OpenCV), model_name (unet | deeplabv3)
    Output: segmented mask (numpy array of predicted class indices 0-6 at original resolution)
    """
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(backend_dir, f"best_model_{model_name}.pth")
    
    if os.path.exists(model_path):
        print(f"Loading trained weights from {model_path}...")
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load architecture
        if model_name == "deeplabv3":
            model = DeepLabV3Plus(n_classes=7).to(device)
        else:
            model = UNet(n_channels=3, n_classes=7).to(device)
            
        model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
        model.eval()
        
        # Original dimensions for upscaling back later
        orig_h, orig_w = image_array.shape[:2]
        
        # Preprocess the image: resize to 256x256 (the size we trained on), BGR to RGB, scale to 0-1
        img_resized = cv2.resize(image_array, (256, 256))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        img_tensor = torch.from_numpy(img_rgb).permute(2, 0, 1).float() / 255.0
        img_tensor = img_tensor.unsqueeze(0).to(device)
        
        # Inference
        with torch.no_grad():
            outputs = model(img_tensor)
            # Get class with highest probability
            _, predicted = torch.max(outputs, 1)
            
        mask_256 = predicted.squeeze().cpu().numpy().astype(np.uint8)
        
        # Upscale the mask back to the original image resolution using Nearest Neighbor
        # We MUST use NEAREST so we don't interpolate class indices (e.g. 1.5)
        final_mask = cv2.resize(mask_256, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)
        return final_mask
    else:
        # Fallback to random mock mask for demonstration if model isn't trained yet
        print(f"Warning: {model_path} not found. Using simulated segmentation mask.")
        h, w = image_array.shape[:2]
        
        # Generate a small low-res grid so we get contiguous, realistic blobs when upscaled
        small_h, small_w = max(1, h // 32), max(1, w // 32)
        # Probabilities adjusted to create more buildable land (classes 4 and 6)
        small_mask = np.random.choice(
            [0, 1, 2, 3, 4, 5, 6], 
            size=(small_h, small_w), 
            p=[0.05, 0.05, 0.10, 0.10, 0.35, 0.10, 0.25]
        )
        
        # Upscale to original resolution using Nearest Neighbor to keep class IDs integers
        mock_mask = cv2.resize(small_mask.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST)
        return mock_mask
