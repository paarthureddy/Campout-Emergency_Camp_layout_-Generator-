import matplotlib.pyplot as plt
import json
import os
import numpy as np

def generate_graphs():
    input_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiling_results.json')
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results_comparison.png')
    
    with open(input_path, 'r') as f:
        data = json.load(f)
        
    models = [d["Model"].replace(" ", "\n") for d in data]
    iou = [d["Simulated Mean IoU (%)"] for d in data]
    accuracy = [d["Simulated Accuracy (%)"] for d in data]
    inference_time = [d["Inference Time (ms)"] for d in data]
    params = [d["Parameters"] / 1e6 for d in data] # in Millions

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Model Comparison: U-Net vs DeepLabV3+', fontsize=16)

    # 1. Mean IoU Plot
    bars = axs[0, 0].bar(models, iou, color=['skyblue', 'lightgreen'])
    axs[0, 0].set_title('Mean IoU (%) - Higher is better')
    axs[0, 0].set_ylim(0, 100)
    axs[0, 0].bar_label(bars, fmt='%.1f')

    # 2. Accuracy Plot
    bars = axs[0, 1].bar(models, accuracy, color=['skyblue', 'lightgreen'])
    axs[0, 1].set_title('Accuracy (%) - Higher is better')
    axs[0, 1].set_ylim(0, 100)
    axs[0, 1].bar_label(bars, fmt='%.1f')

    # 3. Inference Time Plot
    bars = axs[1, 0].bar(models, inference_time, color=['lightcoral', 'salmon'])
    axs[1, 0].set_title('Inference Time (ms) - Lower is better')
    axs[1, 0].bar_label(bars, fmt='%.1f')

    # 4. Parameters Plot
    bars = axs[1, 1].bar(models, params, color=['gold', 'khaki'])
    axs[1, 1].set_title('Parameters (Millions)')
    axs[1, 1].bar_label(bars, fmt='%.2f')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Graphs successfully generated and saved to {output_path}")

if __name__ == '__main__':
    generate_graphs()
