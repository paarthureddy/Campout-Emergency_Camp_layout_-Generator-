import torch
import time
import json
import os
import sys

# Ensure backend directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.unet import UNet
from models.deeplabv3 import DeepLabV3Plus

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def profile_inference(model, input_tensor, num_iterations=50):
    model.eval()
    # Warmup
    with torch.no_grad():
        for _ in range(5):
            _ = model(input_tensor)
            
    # Timed runs
    start_time = time.time()
    with torch.no_grad():
        for _ in range(num_iterations):
            _ = model(input_tensor)
    end_time = time.time()
    
    avg_time_ms = ((end_time - start_time) / num_iterations) * 1000
    return avg_time_ms

def main():
    print("Initializing models...")
    # Using 3 channels (RGB) and 7 classes based on the UNet defaults
    unet = UNet(n_channels=3, n_classes=7)
    deeplab = DeepLabV3Plus(n_channels=3, n_classes=7)

    # Dummy input of size (Batch, Channels, Height, Width) - e.g. 512x512 image
    dummy_input = torch.randn(1, 3, 512, 512)

    print("Profiling U-Net...")
    unet_params = count_parameters(unet)
    unet_time = profile_inference(unet, dummy_input)

    print("Profiling DeepLabV3+...")
    deeplab_params = count_parameters(deeplab)
    deeplab_time = profile_inference(deeplab, dummy_input)

    results = [
        {
            "Model": "U-Net (Baseline)",
            "Parameters": unet_params,
            "Inference Time (ms)": round(unet_time, 2),
            "Simulated Mean IoU (%)": 74.2,  # Simulated metric for comparison
            "Simulated Accuracy (%)": 88.5
        },
        {
            "Model": "DeepLabV3+ (Proposed)",
            "Parameters": deeplab_params,
            "Inference Time (ms)": round(deeplab_time, 2),
            "Simulated Mean IoU (%)": 78.6,
            "Simulated Accuracy (%)": 91.3
        }
    ]

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiling_results.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"Profiling complete. Results saved to {output_path}")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
