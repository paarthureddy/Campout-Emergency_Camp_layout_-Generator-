import torch
import numpy as np
from typing import Tuple, List

def calculate_iou(preds: torch.Tensor, labels: torch.Tensor, num_classes: int) -> Tuple[float, List[float]]:
    """
    Calculates the Intersection over Union (IoU) per class and Mean IoU.
    
    Args:
        preds (torch.Tensor): Predictions tensor of shape (N, H, W)
        labels (torch.Tensor): Ground truth labels tensor of shape (N, H, W)
        num_classes (int): Number of semantic classes
        
    Returns:
        Tuple[float, List[float]]: The mean IoU and the list of per-class IoU values.
    """
    ious = []
    preds = preds.view(-1)
    labels = labels.view(-1)
    
    # Ignore index -1 if it exists in LoveDA
    valid_mask = labels != -1
    preds = preds[valid_mask]
    labels = labels[valid_mask]

    for cls in range(num_classes):
        pred_inds = preds == cls
        target_inds = labels == cls
        intersection = (pred_inds[target_inds]).long().sum().item()
        union = pred_inds.long().sum().item() + target_inds.long().sum().item() - intersection
        
        if union == 0:
            ious.append(float('nan'))  # If there is no ground truth, do not include in mean IoU
        else:
            ious.append(float(intersection) / float(max(union, 1)))
            
    # Calculate Mean IoU ignoring NaNs
    valid_ious = [iou for iou in ious if not np.isnan(iou)]
    mean_iou = sum(valid_ious) / len(valid_ious) if len(valid_ious) > 0 else 0.0
    return mean_iou, ious

def calculate_dice(preds: torch.Tensor, labels: torch.Tensor, num_classes: int) -> float:
    """
    Calculates the Dice Coefficient.
    
    Args:
        preds (torch.Tensor): Predictions tensor of shape (N, H, W)
        labels (torch.Tensor): Ground truth labels tensor of shape (N, H, W)
        num_classes (int): Number of semantic classes
        
    Returns:
        float: The mean Dice coefficient across valid classes.
    """
    dices = []
    preds = preds.view(-1)
    labels = labels.view(-1)
    
    valid_mask = labels != -1
    preds = preds[valid_mask]
    labels = labels[valid_mask]

    for cls in range(num_classes):
        pred_inds = preds == cls
        target_inds = labels == cls
        intersection = (pred_inds[target_inds]).long().sum().item()
        denominator = pred_inds.long().sum().item() + target_inds.long().sum().item()
        
        if denominator == 0:
            dices.append(float('nan'))
        else:
            dices.append((2.0 * intersection) / float(max(denominator, 1)))
            
    valid_dices = [dice for dice in dices if not np.isnan(dice)]
    mean_dice = sum(valid_dices) / len(valid_dices) if len(valid_dices) > 0 else 0.0
    return mean_dice
