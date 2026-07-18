import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from core.dataset import ZipImageDataset
from models.unet import UNet
import os

def train():
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training on device: {device}")

    # Hyperparameters
    batch_size = 4
    learning_rate = 1e-4
    epochs = 10
    num_classes = 7 # LoveDA classes: Background, Building, Road, Water, Barren, Forest, Agriculture

    # Dataset Paths
    train_zip_path = os.path.join("data", "LoveDA", "Train.zip")
    val_zip_path = os.path.join("data", "LoveDA", "Val.zip")
    
    if not os.path.exists(train_zip_path):
        print(f"Error: {train_zip_path} not found.")
        return

    # Initialize Datasets and DataLoaders
    # Note: In a real scenario, you'd add Albumentations here for image transforms (Resize, RandomCrop, etc.)
    # For now, ZipImageDataset handles basic tensor conversion.
    print("Loading datasets directly from ZIP files...")
    train_dataset = ZipImageDataset(train_zip_path)
    val_dataset = ZipImageDataset(val_zip_path)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    print(f"Train images: {len(train_dataset)}, Validation images: {len(val_dataset)}")

    # Initialize Model
    model = UNet(n_channels=3, n_classes=num_classes).to(device)
    
    # Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Training Loop
    print("Starting training...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for i, (images, masks) in enumerate(train_loader):
            images = images.to(device)
            # CrossEntropyLoss expects masks of shape (N, H, W) without a channel dimension for class indices
            # Depending on how the masks are formatted in LoveDA, they might need adjustment here.
            # Assuming masks are single-channel label images:
            masks = masks.to(device)
            
            optimizer.zero_grad()
            
            outputs = model(images)
            loss = criterion(outputs, masks)
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
            if (i + 1) % 10 == 0:
                print(f"Epoch [{epoch+1}/{epochs}], Step [{i+1}/{len(train_loader)}], Loss: {loss.item():.4f}")

        epoch_loss = running_loss / len(train_loader)
        print(f"--- Epoch {epoch+1} completed. Average Loss: {epoch_loss:.4f} ---")
        
        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, masks in val_loader:
                images, masks = images.to(device), masks.to(device)
                outputs = model(images)
                loss = criterion(outputs, masks)
                val_loss += loss.item()
        
        avg_val_loss = val_loss / len(val_loader)
        print(f"Validation Loss: {avg_val_loss:.4f}\n")

    # Save the model
    save_path = "unet_loveda.pth"
    torch.save(model.state_dict(), save_path)
    print(f"Training complete! Model saved to {save_path}")

if __name__ == '__main__':
    train()
