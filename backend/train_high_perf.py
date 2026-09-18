import os
import time
import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import torchvision.models.segmentation as sm

from core.dataset import FolderImageDataset
from core.metrics import calculate_iou, calculate_dice
from models.unet import UNet

# 7 Semantic Classes in LoveDA (0-indexed after subtracting 1 for ignore):
# 0: Background, 1: Building, 2: Road, 3: Water, 4: Barren, 5: Forest, 6: Agriculture
# Balanced class weights (close to 1.0, slightly mitigating background dominance)
BALANCED_WEIGHTS = torch.tensor([
    0.6,   # 0: Background
    1.2,   # 1: Building
    1.4,   # 2: Road
    1.0,   # 3: Water (keep at 1.0 so shadows are NOT falsely classified as water)
    1.2,   # 4: Barren
    1.0,   # 5: Forest
    1.0,   # 6: Agriculture
], dtype=torch.float32)

def get_model(model_name: str, num_classes: int = 7, device: str = "cuda"):
    if model_name == "deeplabv3":
        # Pretrained MobileNetV3-Large backbone
        model = sm.deeplabv3_mobilenet_v3_large(weights=None, num_classes=num_classes)
        cache_path = os.path.expanduser(r"~\.cache\torch\hub\checkpoints\mobilenet_v3_large-8738ca79.pth")
        if os.path.exists(cache_path):
            bb_weights = torch.load(cache_path, map_location="cpu")
            model.backbone.load_state_dict(bb_weights, strict=False)
            print("[train] Loaded pretrained MobileNetV3 backbone!")
    else:
        model = UNet(n_channels=3, n_classes=num_classes)
    return model.to(device)

def train_model(model_name="deeplabv3", epochs=10, batch_size=16, lr=0.0005):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n============================================================")
    print(f"  Training {model_name.upper()} on {device}")
    print(f"  Epochs: {epochs} | Batch size: {batch_size} | LR: {lr}")
    print(f"============================================================")

    train_ds = FolderImageDataset("data/LoveDA/Train_256")
    val_ds   = FolderImageDataset("data/LoveDA/Val_256")
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0, pin_memory=True)
    val_loader   = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0, pin_memory=True)

    model = get_model(model_name, num_classes=7, device=device)
    class_weights = BALANCED_WEIGHTS.to(device)
    ce_loss = nn.CrossEntropyLoss(weight=class_weights, ignore_index=-1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)
    scaler = torch.cuda.amp.GradScaler()

    best_iou = 0.0
    history = {"train_loss": [], "val_loss": [], "val_iou": [], "val_dice": []}
    save_path = f"best_model_{model_name}.pth"

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        n_batches = 0
        t0 = time.time()

        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            with torch.cuda.amp.autocast():
                out = model(x)
                if isinstance(out, dict):
                    out = out["out"]
                loss = ce_loss(out, y)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            total_loss += loss.item()
            n_batches += 1

        scheduler.step()
        train_loss = total_loss / max(1, n_batches)

        # Validation
        model.eval()
        val_loss_tot = 0.0
        val_batches = 0
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                with torch.cuda.amp.autocast():
                    out = model(x)
                    if isinstance(out, dict):
                        out = out["out"]
                    vloss = ce_loss(out, y)
                val_loss_tot += vloss.item()
                val_batches += 1
                pred = out.argmax(dim=1)
                all_preds.append(pred.cpu())
                all_labels.append(y.cpu())

        val_loss = val_loss_tot / max(1, val_batches)
        preds_cat = torch.cat(all_preds, dim=0)
        labels_cat = torch.cat(all_labels, dim=0)
        val_iou, class_ious = calculate_iou(preds_cat, labels_cat, 7)
        val_dice = calculate_dice(preds_cat, labels_cat, 7)
        elapsed = time.time() - t0

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_iou"].append(val_iou)
        history["val_dice"].append(val_dice)

        print(f"--- Epoch {epoch+1}/{epochs} ({elapsed:.1f}s) ---")
        print(f"  Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
        print(f"  Val IoU   : {val_iou:.4f} | Val Dice: {val_dice:.4f}")
        print(f"  Per-class IoU: {[round(c, 3) for c in class_ious]}")

        if val_iou > best_iou:
            best_iou = val_iou
            torch.save(model.state_dict(), save_path)
            print(f"  *** New best model saved -> {save_path} (IoU: {best_iou:.4f})")

    with open(f"history_{model_name}.json", "w") as f:
        json.dump(history, f, indent=2)

    print(f"\n============================================================")
    print(f"  Training complete! Best Val IoU: {best_iou:.4f}")
    print(f"  Saved to {save_path} and history_{model_name}.json")
    print(f"============================================================\n")

if __name__ == "__main__":
    import sys
    model_choice = sys.argv[1] if len(sys.argv) > 1 else "deeplabv3"
    epochs_choice = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    train_model(model_name=model_choice, epochs=epochs_choice)
