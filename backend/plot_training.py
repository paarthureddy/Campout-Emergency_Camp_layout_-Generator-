import matplotlib.pyplot as plt
import json
import os
import argparse

def plot_history(model_name):
    history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'history_{model_name}.json')
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'learning_curves_{model_name}.png')
    
    if not os.path.exists(history_file):
        print(f"Error: {history_file} not found. Train the model first.")
        return
        
    with open(history_file, 'r') as f:
        history = json.load(f)
        
    epochs = range(1, len(history['train_loss']) + 1)
    
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f'Training Learning Curves - {model_name.upper()}', fontsize=16)
    
    # Plot 1: Loss
    axs[0].plot(epochs, history['train_loss'], 'b-', label='Training Loss', marker='o')
    axs[0].plot(epochs, history['val_loss'], 'r-', label='Validation Loss', marker='o')
    axs[0].set_title('Cross Entropy Loss')
    axs[0].set_xlabel('Epochs')
    axs[0].set_ylabel('Loss')
    axs[0].legend()
    axs[0].grid(True)
    
    # Plot 2: Metrics (IoU & Dice)
    axs[1].plot(epochs, history['val_iou'], 'g-', label='Validation Mean IoU', marker='s')
    axs[1].plot(epochs, history['val_dice'], 'm-', label='Validation Dice Coeff', marker='^')
    axs[1].set_title('Segmentation Metrics')
    axs[1].set_xlabel('Epochs')
    axs[1].set_ylabel('Score (0 to 1)')
    axs[1].set_ylim(0, 1.0)
    axs[1].legend()
    axs[1].grid(True)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Successfully generated learning curves at {output_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Plot Training Curves")
    parser.add_argument('--model', type=str, default='unet', help="Model name to plot history for")
    args = parser.parse_args()
    plot_history(args.model)
