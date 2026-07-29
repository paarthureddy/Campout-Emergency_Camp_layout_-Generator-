import torch
from torch.utils.data import Dataset
import zipfile
from PIL import Image
import io
import numpy as np
import os
import torchvision.transforms as transforms

class ZipImageDataset(Dataset):
    """
    Reads images directly from a zip file to save disk space.
    Assumes the zip file has pairs of images and masks with identical names in different directories.
    """
    def __init__(self, zip_path, transform=None):
        self.zip_path = zip_path
        self.transform = transform
        
        # We don't keep the zipfile open because of multiprocessing in DataLoaders.
        # We just read the file list once.
        with zipfile.ZipFile(self.zip_path, 'r') as zf:
            # Filter to find actual image files inside any 'images_png' directory
            self.image_files = [f for f in zf.namelist() if 'images_png/' in f and f.endswith('.png')]
            
    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_path = self.image_files[idx]
        
        # Derive mask path from image path by swapping the directory name
        mask_path = img_path.replace('images_png/', 'masks_png/')
        
        # Open zipfile on the fly for thread safety
        with zipfile.ZipFile(self.zip_path, 'r') as zf:
            # Read Image
            img_bytes = zf.read(img_path)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            
            # Read Mask
            mask_bytes = zf.read(mask_path)
            mask = Image.open(io.BytesIO(mask_bytes))
            
        # Convert to numpy arrays
        img = np.array(img)
        mask = np.array(mask)
        
        # Apply joint data augmentation if requested (Phase 2)
        if self.transform:
            # For simplicity, if transform is True, apply random crop and flip
            import torchvision.transforms.functional as TF
            import random
            
            # Convert to PIL Image for torchvision transforms
            img = Image.fromarray(img)
            mask = Image.fromarray(mask)
            
            # Random horizontal flipping
            if random.random() > 0.5:
                img = TF.hflip(img)
                mask = TF.hflip(mask)
                
            # Random vertical flipping
            if random.random() > 0.5:
                img = TF.vflip(img)
                mask = TF.vflip(mask)
                
            # Random Crop (e.g., 256x256 if images are larger)
            # Assuming we want to crop to a standard size
            w, h = img.size
            if w > 256 and h > 256:
                i, j, h, w = transforms.RandomCrop.get_params(img, output_size=(256, 256))
                img = TF.crop(img, i, j, h, w)
                mask = TF.crop(mask, i, j, h, w)
                
            # Color jitter for the image only
            if random.random() > 0.5:
                img = TF.adjust_brightness(img, brightness_factor=random.uniform(0.8, 1.2))
                img = TF.adjust_contrast(img, contrast_factor=random.uniform(0.8, 1.2))
                
            # Convert back to numpy for final tensor conversion
            img = np.array(img)
            mask = np.array(mask)

        # Convert to Tensors
        img_tensor = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
        mask_tensor = torch.from_numpy(mask).long()
        
        # LoveDA masks are 1-indexed (1-7). Subtract 1 to make them 0-indexed (0-6) for CrossEntropyLoss
        mask_tensor = mask_tensor - 1
            
        return img_tensor, mask_tensor
