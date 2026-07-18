import torch
from torch.utils.data import Dataset
import zipfile
from PIL import Image
import io
import numpy as np
import os

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
        
        # Apply torchvision transforms if any
        if self.transform:
            augmented = self.transform(image=img, mask=mask)
            img = augmented['image']
            mask = augmented['mask']
        else:
            # Basic fallback conversion if no transforms provided
            img = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
            mask = torch.from_numpy(mask).long()
            
        return img, mask
