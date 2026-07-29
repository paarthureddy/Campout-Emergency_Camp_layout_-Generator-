import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from core.dataset import FolderImageDataset
from core.metrics import calculate_iou, calculate_dice
from models.unet import UNet
from models.deeplabv3 import DeepLabV3Plus
import os
import argparse
import json

def train():
    parser = argparse.ArgumentParser(description="Train Deep Learning Models for Terrain Segmentation")
    parser.add_argument('--model', type=str, default='unet', choices=['unet', 'deeplabv3'], help="Model to train")
    parser.add_argument('--epochs', type=int, default=10, help="Number of training epochs")
    parser.add_argument('--lr', type=float, default=1e-4, help="Learning rate")
    parser.add_argument('--batch_size', type=int, default=4, help="Batch size")
    parser.add_argument('--fast_demo', action='store_true', help="Run only 5 batches per epoch for quick demonstration")
    args = parser.parse_args()

    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training {args.model.upper()} on device: {device}")

    num_classes = 7 

    # Dataset Paths (now using the offline preprocessed 256x256 folders)
    train_dir_path = os.path.join("data", "LoveDA", "Train_256")
    val_dir_path = os.path.join("data", "LoveDA", "Val_256")
    
    if not os.path.exists(train_dir_path) or not os.path.exists(val_dir_path):
        print("Error: Offline dataset folders not found. Run preprocess_dataset.py first.")
        return

    print("Loading datasets from offline preprocessed folders...")
    train_dataset = FolderImageDataset(train_dir_path, transform=True)
    val_dataset = FolderImageDataset(val_dir_path, transform=False)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)

    print(f"Train images: {len(train_dataset)}, Validation images: {len(val_dataset)}")

    # Initialize Model
    if args.model == 'unet':
        model = UNet(n_channels=3, n_classes=num_classes).to(device)
    else:
        model = DeepLabV3Plus(n_channels=3, n_classes=num_classes).to(device)
    
    # Loss and Optimizer
    criterion = nn.CrossEntropyLoss(ignore_index=-1)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    history = {
        "train_loss": [],
        "val_loss": [],
        "val_iou": [],
        "val_dice": []
    }
    
    best_iou = 0.0

    print("Starting training...")
    for epoch in range(args.epochs):
        model.train()
        running_loss = 0.0
        
        for i, (images, masks) in enumerate(train_loader):
            images, masks = images.to(device), masks.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, masks)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
            if (i + 1) % 10 == 0 or (args.fast_demo and i > 0):
                print(f"Epoch [{epoch+1}/{args.epochs}], Step [{i+1}/{len(train_loader)}], Loss: {loss.item():.4f}")
            if args.fast_demo and i >= 4:
                break

        # In fast_demo, len(train_loader) is too large for the actual steps taken, but epoch_loss is just an average of what ran.
        # Actually, running_loss is correct, but we should divide by the steps taken.
        steps_taken = i + 1
        epoch_loss = running_loss / steps_taken
        history["train_loss"].append(epoch_loss)
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_ious = []
        val_dices = []
        
        with torch.no_grad():
            for i, (images, masks) in enumerate(val_loader):
                images, masks = images.to(device), masks.to(device)
                outputs = model(images)
                loss = criterion(outputs, masks)
                val_loss += loss.item()
                
                _, predicted = torch.max(outputs, 1)
                mean_iou, _ = calculate_iou(predicted, masks, num_classes)
                mean_dice = calculate_dice(predicted, masks, num_classes)
                
                val_ious.append(mean_iou)
                val_dices.append(mean_dice)
                
                if args.fast_demo and i >= 4:
                    break
        
        val_steps = i + 1
        avg_val_loss = val_loss / val_steps
        avg_iou = sum(val_ious) / len(val_ious) if len(val_ious) > 0 else 0
        avg_dice = sum(val_dices) / len(val_dices) if len(val_dices) > 0 else 0
        
        history["val_loss"].append(avg_val_loss)
        history["val_iou"].append(avg_iou)
        history["val_dice"].append(avg_dice)
        
        print(f"--- Epoch {epoch+1} ---")
        print(f"Train Loss: {epoch_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Val IoU: {avg_iou:.4f} | Val Dice: {avg_dice:.4f}\n")

        # Model Checkpointing
        if avg_iou > best_iou:
            best_iou = avg_iou
            save_path = f"best_model_{args.model}.pth"
            torch.save(model.state_dict(), save_path)
            print(f"*** New Best Model Saved to {save_path} (IoU: {best_iou:.4f}) ***\n")

    # Save History
    with open(f"history_{args.model}.json", "w") as f:
        json.dump(history, f, indent=4)
        
    print(f"Training complete! History saved to history_{args.model}.json")

if __name__ == '__main__':
    train()
