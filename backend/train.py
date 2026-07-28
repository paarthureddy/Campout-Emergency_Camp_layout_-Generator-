import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from core.dataset import ZipImageDataset
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
    args = parser.parse_args()

    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training {args.model.upper()} on device: {device}")

    num_classes = 7 

    # Dataset Paths
    train_zip_path = os.path.join("data", "LoveDA", "Train.zip")
    val_zip_path = os.path.join("data", "LoveDA", "Val.zip")
    
    if not os.path.exists(train_zip_path) or not os.path.exists(val_zip_path):
        print("Error: Dataset zip files not found. Make sure Train.zip and Val.zip are in data/LoveDA/")
        return

    print("Loading datasets directly from ZIP files...")
    # Transformations will be added in Phase 2
    train_dataset = ZipImageDataset(train_zip_path, transform=True)
    val_dataset = ZipImageDataset(val_zip_path, transform=False)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0)

    print(f"Train images: {len(train_dataset)}, Validation images: {len(val_dataset)}")

    # Initialize Model
    if args.model == 'unet':
        model = UNet(n_channels=3, n_classes=num_classes).to(device)
    else:
        model = DeepLabV3Plus(n_channels=3, n_classes=num_classes).to(device)
    
    # Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
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
            
            if (i + 1) % 10 == 0:
                print(f"Epoch [{epoch+1}/{args.epochs}], Step [{i+1}/{len(train_loader)}], Loss: {loss.item():.4f}")

        epoch_loss = running_loss / len(train_loader)
        history["train_loss"].append(epoch_loss)
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_ious = []
        val_dices = []
        
        with torch.no_grad():
            for images, masks in val_loader:
                images, masks = images.to(device), masks.to(device)
                outputs = model(images)
                loss = criterion(outputs, masks)
                val_loss += loss.item()
                
                _, predicted = torch.max(outputs, 1)
                mean_iou, _ = calculate_iou(predicted, masks, num_classes)
                mean_dice = calculate_dice(predicted, masks, num_classes)
                
                val_ious.append(mean_iou)
                val_dices.append(mean_dice)
        
        avg_val_loss = val_loss / len(val_loader)
        avg_iou = sum(val_ious) / len(val_ious)
        avg_dice = sum(val_dices) / len(val_dices)
        
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
