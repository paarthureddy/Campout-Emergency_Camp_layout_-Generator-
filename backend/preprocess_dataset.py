import os
import zipfile
import io
from PIL import Image
from tqdm import tqdm

def process_zip(zip_path, output_dir, size=(256, 256)):
    print(f"Processing {zip_path}...")
    
    if not os.path.exists(zip_path):
        print(f"Error: {zip_path} not found.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    images_out_dir = os.path.join(output_dir, "images")
    masks_out_dir = os.path.join(output_dir, "masks")
    os.makedirs(images_out_dir, exist_ok=True)
    os.makedirs(masks_out_dir, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        # Get all image and mask files
        file_list = z.namelist()
        images = [f for f in file_list if 'images_png/' in f and f.endswith('.png')]
        
        print(f"Found {len(images)} images to process.")
        
        for img_path in tqdm(images, desc="Resizing"):
            # Construct corresponding mask path
            # LoveDA structure: Train/Rural/images_png/1000.png -> Train/Rural/masks_png/1000.png
            mask_path = img_path.replace('images_png', 'masks_png')
            filename = os.path.basename(img_path)
            
            try:
                # Process Image
                img_bytes = z.read(img_path)
                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                img_resized = img.resize(size, Image.Resampling.BILINEAR)
                img_resized.save(os.path.join(images_out_dir, filename))
                
                # Process Mask
                mask_bytes = z.read(mask_path)
                mask = Image.open(io.BytesIO(mask_bytes))
                # Use NEAREST for masks to avoid interpolating class values!
                mask_resized = mask.resize(size, Image.Resampling.NEAREST)
                mask_resized.save(os.path.join(masks_out_dir, filename))
                
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "data", "LoveDA")
    
    train_zip = os.path.join(base_dir, "Train.zip")
    train_out = os.path.join(base_dir, "Train_256")
    
    val_zip = os.path.join(base_dir, "Val.zip")
    val_out = os.path.join(base_dir, "Val_256")
    
    process_zip(train_zip, train_out)
    process_zip(val_zip, val_out)
    
    print("Offline preprocessing complete! All images resized to 256x256.")
