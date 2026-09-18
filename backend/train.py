import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from core.dataset import FolderImageDataset
from core.metrics import calculate_iou, calculate_dice
from models.unet import UNet
from models.deeplabv3 import DeepLabV3Plus
import os
import argparse
import json
import time

# ─────────────────────────────────────────────────────────────────────────────
# Research-informed class weights for LoveDA dataset
# Background (34.4%) dominates → downweight it, upweight rare classes
# Weights = inverse frequency, normalised to mean=1
# Distribution: Background=34.4%, Building=10.6%, Road=5.1%, Water=6.2%,
#               Barren=5.0%, Forest=15.5%, Agriculture=19.4%
# ─────────────────────────────────────────────────────────────────────────────
LOVEDA_CLASS_WEIGHTS = torch.tensor([
    0.29,   # 0: Background  (most common → lowest weight)
    0.94,   # 1: Building
    1.96,   # 2: Road
    1.61,   # 3: Water
    2.00,   # 4: Barren      (rarest → highest weight, critical for camp building)
    0.64,   # 5: Forest
    0.51,   # 6: Agriculture (buildable land)
], dtype=torch.float32)


class CombinedLoss(nn.Module):
    """
    Research best practice for LoveDA:
    Combines weighted Cross-Entropy (stable convergence) +
    Dice Loss (handles class imbalance, optimises IoU directly).
    
    References:
    - LoveDA benchmark paper (NeurIPS 2021)
    - "Focal Loss for Dense Object Detection" (Lin et al.)
    - Segmentation-models-pytorch best practices for remote sensing
    """
    def __init__(self, class_weights, ignore_index=-1, dice_weight=0.4):
        super().__init__()
        self.ignore_index = ignore_index
        self.dice_weight = dice_weight
        self.ce = nn.CrossEntropyLoss(
            weight=class_weights,
            ignore_index=ignore_index
        )

    def _dice_loss(self, logits, targets):
        """Soft Dice Loss over valid (non-ignored) pixels."""
        num_classes = logits.shape[1]
        probs = F.softmax(logits, dim=1)  # (N, C, H, W)

        valid = (targets != self.ignore_index)
        dice = 0.0
        count = 0
        for c in range(num_classes):
            gt_c = ((targets == c) & valid).float()
            if gt_c.sum() == 0:
                continue
            pred_c = probs[:, c, :, :]
            intersection = (pred_c * gt_c).sum()
            union = pred_c.sum() + gt_c.sum()
            dice += 1 - (2 * intersection + 1e-6) / (union + 1e-6)
            count += 1
        return dice / max(count, 1)

    def forward(self, logits, targets):
        ce_loss   = self.ce(logits, targets)
        dice_loss = self._dice_loss(logits, targets)
        return (1 - self.dice_weight) * ce_loss + self.dice_weight * dice_loss


def train():
    parser = argparse.ArgumentParser(
        description="Train Deep Learning Models for Terrain Segmentation on LoveDA"
    )
    parser.add_argument('--model',      type=str,   default='unet',
                        choices=['unet', 'deeplabv3'])
    parser.add_argument('--epochs',     type=int,   default=25,
                        help="Full training: 25 epochs on entire dataset")
    parser.add_argument('--lr',         type=float, default=1e-4)
    parser.add_argument('--batch_size', type=int,   default=8)
    parser.add_argument('--fast_demo',  action='store_true',
                        help="Run only 10 batches per epoch for quick smoke-test")

    # Regularisation (kept for faculty review compatibility)
    parser.add_argument('--l1_lambda', type=float, default=1e-5)
    parser.add_argument('--l2_lambda', type=float, default=1e-4)
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n" + "="*60)
    print(f"  Training {args.model.upper()} on {device}")
    print(f"  Epochs: {args.epochs}  |  Batch size: {args.batch_size}")
    print(f"  Fast demo: {args.fast_demo}")
    print("="*60 + "\n")

    num_classes = 7

    train_dir = os.path.join("data", "LoveDA", "Train_256")
    val_dir   = os.path.join("data", "LoveDA", "Val_256")
    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        print("ERROR: Dataset not found. Run preprocess_dataset.py first.")
        return

    print("Loading LoveDA dataset...")
    train_dataset = FolderImageDataset(train_dir, transform=True)
    val_dataset   = FolderImageDataset(val_dir,   transform=False)
    print(f"  Train: {len(train_dataset)} images | Val: {len(val_dataset)} images\n")

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size,
                              shuffle=True,  num_workers=0, pin_memory=False)
    val_loader   = DataLoader(val_dataset,   batch_size=args.batch_size,
                              shuffle=False, num_workers=0, pin_memory=False)

    # ── Model ─────────────────────────────────────────────────────────────────
    if args.model == 'unet':
        model = UNet(n_channels=3, n_classes=num_classes).to(device)
    else:
        model = DeepLabV3Plus(n_channels=3, n_classes=num_classes).to(device)

    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Model parameters: {total_params:,}\n")

    # ── Loss: Weighted CE + Dice (research best practice for LoveDA) ──────────
    criterion = CombinedLoss(
        class_weights=LOVEDA_CLASS_WEIGHTS.to(device),
        ignore_index=-1,
        dice_weight=0.4
    )

    # ── Optimiser: Adam + L2 weight decay ─────────────────────────────────────
    optimizer = optim.Adam(
        model.parameters(), lr=args.lr, weight_decay=args.l2_lambda
    )

    # ── LR Scheduler: reduce on plateau (standard for segmentation) ───────────
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=3, verbose=True
    )

    history = {"train_loss": [], "val_loss": [], "val_iou": [], "val_dice": []}
    best_iou = 0.0
    save_path = f"best_model_{args.model}.pth"

    batches_per_epoch = 10 if args.fast_demo else len(train_loader)
    val_batches       = 10 if args.fast_demo else len(val_loader)

    print(f"Starting training ({batches_per_epoch} batches/epoch)...\n")

    for epoch in range(args.epochs):
        epoch_start = time.time()

        # ── Training loop ─────────────────────────────────────────────────────
        model.train()
        running_loss = 0.0

        for i, (images, masks) in enumerate(train_loader):
            if i >= batches_per_epoch:
                break

            images, masks = images.to(device), masks.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, masks)

            # L1 regularisation (faculty review)
            if args.l1_lambda > 0:
                l1_penalty = sum(p.abs().sum() for p in model.parameters())
                loss = loss + args.l1_lambda * l1_penalty

            loss.backward()
            optimizer.step()
            running_loss += loss.item()

            # Progress print every 20 batches
            if (i + 1) % 20 == 0:
                print(f"  Epoch [{epoch+1}/{args.epochs}] "
                      f"Batch [{i+1}/{batches_per_epoch}] "
                      f"Loss: {loss.item():.4f}")

        epoch_loss = running_loss / batches_per_epoch
        history["train_loss"].append(epoch_loss)

        # ── Validation loop ───────────────────────────────────────────────────
        model.eval()
        val_loss  = 0.0
        val_ious  = []
        val_dices = []

        with torch.no_grad():
            for i, (images, masks) in enumerate(val_loader):
                if i >= val_batches:
                    break
                images, masks = images.to(device), masks.to(device)
                outputs = model(images)
                loss = criterion(outputs, masks)
                val_loss += loss.item()

                _, predicted = torch.max(outputs, 1)
                mean_iou, _  = calculate_iou(predicted, masks, num_classes)
                mean_dice    = calculate_dice(predicted, masks, num_classes)
                val_ious.append(mean_iou)
                val_dices.append(mean_dice)

        avg_val_loss = val_loss / val_batches
        avg_iou      = sum(val_ious)  / len(val_ious)  if val_ious  else 0
        avg_dice     = sum(val_dices) / len(val_dices) if val_dices else 0

        history["val_loss"].append(avg_val_loss)
        history["val_iou"].append(avg_iou)
        history["val_dice"].append(avg_dice)

        # LR scheduling based on validation IoU
        scheduler.step(avg_iou)

        elapsed = time.time() - epoch_start
        print(f"\n  --- Epoch {epoch+1}/{args.epochs} ({elapsed:.1f}s) ---")
        print(f"  Train Loss : {epoch_loss:.4f}")
        print(f"  Val   Loss : {avg_val_loss:.4f}")
        print(f"  Val   IoU  : {avg_iou:.4f}   Dice: {avg_dice:.4f}")
        print(f"  LR         : {optimizer.param_groups[0]['lr']:.2e}\n")

        # ── Model checkpointing ───────────────────────────────────────────────
        if avg_iou > best_iou:
            best_iou = avg_iou
            torch.save(model.state_dict(), save_path)
            print(f"  *** New best model saved -> {save_path} (IoU: {best_iou:.4f})\n")

    # ── Save training history ─────────────────────────────────────────────────
    history_path = f"history_{args.model}.json"
    with open(history_path, "w") as f:
        json.dump(history, f, indent=4)

    print("\n" + "="*60)
    print("  Training complete!")
    print(f"  Best Val IoU : {best_iou:.4f}")
    print(f"  Model saved  : {save_path}")
    print(f"  History saved: {history_path}")
    print("="*60 + "\n")


if __name__ == '__main__':
    train()
