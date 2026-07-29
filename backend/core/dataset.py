import torch
from torch.utils.data import Dataset
from PIL import Image
import numpy as np
import os
import torchvision.transforms as transforms

class FolderImageDataset(Dataset):
    """
    Custom Dataset for LoveDA Semantic Segmentation reading from preprocessed folders.
    Expects directory structure:
    base_dir/
      images/
        1000.png
      masks/
        1000.png
    """
    def __init__(self, base_dir, transform=None):
        self.base_dir = base_dir
        self.images_dir = os.path.join(base_dir, "images")
        self.masks_dir = os.path.join(base_dir, "masks")
        
        # Get list of all images
        if not os.path.exists(self.images_dir):
            self.image_files = []
        else:
            self.image_files = sorted([f for f in os.listdir(self.images_dir) if f.endswith('.png')])
            
        self.transform = transform

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        filename = self.image_files[idx]
        img_path = os.path.join(self.images_dir, filename)
        mask_path = os.path.join(self.masks_dir, filename)

        # Read image
        img = Image.open(img_path).convert("RGB")
        # Read mask
        mask = Image.open(mask_path)
        
        # Apply joint data augmentation if requested (Phase 2)
        if self.transform:
            import torchvision.transforms.functional as TF
            import random
            
            # Random horizontal flipping
            if random.random() > 0.5:
                img = TF.hflip(img)
                mask = TF.hflip(mask)
                
            # Random vertical flipping
            if random.random() > 0.5:
                img = TF.vflip(img)
                mask = TF.vflip(mask)
                
            # Random Crop (not needed if already resized to 256x256 offline, but kept for safety if larger)
            w, h = img.size
            if w > 256 and h > 256:
                i, j, h, w = transforms.RandomCrop.get_params(img, output_size=(256, 256))
                img = TF.crop(img, i, j, h, w)
                mask = TF.crop(mask, i, j, h, w)
                
            # Color jitter for the image only
            if random.random() > 0.5:
                img = TF.adjust_brightness(img, brightness_factor=random.uniform(0.8, 1.2))
                img = TF.adjust_contrast(img, contrast_factor=random.uniform(0.8, 1.2))

        # Convert to numpy then tensor
        img_np = np.array(img)
        mask_np = np.array(mask)

        # Convert to Tensors
        img_tensor = torch.from_numpy(img_np).permute(2, 0, 1).float() / 255.0
        mask_tensor = torch.from_numpy(mask_np).long()
        
        # LoveDA masks are 1-indexed (1-7). Subtract 1 to make them 0-indexed (0-6) for CrossEntropyLoss
        mask_tensor = mask_tensor - 1
            
        return img_tensor, mask_tensor
