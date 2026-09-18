import os
import sys
import cv2
import torch
import numpy as np

# Add parent directory to path to allow importing models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Module-level model cache so weights are only loaded once ──────────────────
_model_cache = {}

# LoveDA class labels (0-indexed)
CLASS_NAMES = {
    0: "Background",
    1: "Building",
    2: "Road",
    3: "Water",
    4: "Barren",
    5: "Forest",
    6: "Agriculture",
}

NUM_CLASSES = 7
INPUT_SIZE  = 256   # The models are evaluated at 256x256 images


def _clean_mask_postprocessing(raw_mask: np.ndarray) -> np.ndarray:
    """
    Cleans salt-and-pepper noise and false-positive shadow specks:
    1. 5x5 median blur to remove single isolated pixel noise.
    2. Water bodies (class 3) must be at least 45 connected pixels; isolated
       small shadow specks inside forests or fields are filtered out.
    """
    clean = cv2.medianBlur(raw_mask, 5)

    # Filter isolated water specks (< 45 pixels)
    water_mask = (clean == 3).astype(np.uint8)
    num_w, w_labels, w_stats, _ = cv2.connectedComponentsWithStats(water_mask)
    for i in range(1, num_w):
        if w_stats[i, cv2.CC_STAT_AREA] < 45:
            # Reassign false shadow noise to Forest (5) or Agriculture (6)
            clean[w_labels == i] = 5

    # Filter isolated building specks (< 25 pixels)
    bldg_mask = (clean == 1).astype(np.uint8)
    num_b, b_labels, b_stats, _ = cv2.connectedComponentsWithStats(bldg_mask)
    for i in range(1, num_b):
        if b_stats[i, cv2.CC_STAT_AREA] < 25:
            clean[b_labels == i] = 0

    return clean


def _load_model(model_name: str, device: torch.device):
    """Load model weights once and cache in `_model_cache`."""
    if model_name in _model_cache:
        return _model_cache[model_name]

    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    weights_path = os.path.join(backend_dir, f"best_model_{model_name}.pth")

    if not os.path.exists(weights_path):
        print(f"[segmentation] Weights not found at {weights_path}")
        return None

    try:
        state = torch.load(weights_path, map_location=device)

        if model_name == "deeplabv3":
            # Check if saved with torchvision format or custom format
            has_backbone_prefix = any(k.startswith("backbone.") for k in state.keys())
            if has_backbone_prefix:
                import torchvision.models.segmentation as sm
                model = sm.deeplabv3_mobilenet_v3_large(weights=None, num_classes=NUM_CLASSES)
            else:
                from models.deeplabv3 import DeepLabV3Plus
                model = DeepLabV3Plus(n_channels=3, n_classes=NUM_CLASSES)
        else:
            from models.unet import UNet
            model = UNet(n_channels=3, n_classes=NUM_CLASSES)

        model.load_state_dict(state)
        model.to(device)
        model.eval()

        _model_cache[model_name] = model
        print(f"[segmentation] Successfully loaded {model_name.upper()} weights from {weights_path}")
        return model

    except Exception as exc:
        print(f"[segmentation] Failed to load model {model_name}: {exc}")
        return None


def _preprocess(image_bgr: np.ndarray) -> torch.Tensor:
    """
    BGR uint8 image -> float32 tensor (1, 3, H, W) matching training preprocessing.
    """
    img = cv2.resize(image_bgr, (INPUT_SIZE, INPUT_SIZE))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))                  # HWC -> CHW
    return torch.from_numpy(img).unsqueeze(0)            # -> (1, 3, H, W)


def _color_heuristic_fallback(image_bgr: np.ndarray) -> np.ndarray:
    """Fallback if weights fail to load."""
    orig_h, orig_w = image_bgr.shape[:2]
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, np.array([30, 40, 40]),   np.array([90, 255, 255]))
    blue_mask  = cv2.inRange(hsv, np.array([90, 50, 50]),   np.array([130, 255, 255]))
    mask = np.full((orig_h, orig_w), 4, dtype=np.uint8)  # default: Barren
    mask[green_mask > 0] = 6   # Agriculture
    mask[blue_mask  > 0] = 3   # Water
    return mask


def segment_terrain(image_array: np.ndarray, model_name: str = "unet") -> np.ndarray:
    """
    Segment a satellite image using the trained neural network.

    Parameters
    ----------
    image_array : np.ndarray  (H, W, 3) BGR uint8
    model_name  : "unet" | "deeplabv3"

    Returns
    -------
    mask : np.ndarray  (H, W)  uint8, values 0-6 (LoveDA class IDs)
    """
    orig_h, orig_w = image_array.shape[:2]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = _load_model(model_name, device)

    if model is None:
        # If requested model isn't available, try the other trained model
        alt_name = "deeplabv3" if model_name == "unet" else "unet"
        model = _load_model(alt_name, device)
        if model is None:
            print("[segmentation] Falling back to colour-heuristic segmentation.")
            return _color_heuristic_fallback(image_array)

    # ── Neural-network inference ──────────────────────────────────────────────
    with torch.no_grad():
        tensor = _preprocess(image_array).to(device)    # (1, 3, 256, 256)
        out = model(tensor)
        if isinstance(out, dict):
            logits = out["out"]
        else:
            logits = out
        pred = torch.argmax(logits, dim=1)             # (1, 256, 256)
        raw_mask = pred.squeeze(0).cpu().numpy().astype(np.uint8)

    # Post-process to eliminate false water shadow noise and isolated specks
    cleaned_mask = _clean_mask_postprocessing(raw_mask)

    # Resize mask back to original image dimensions
    if (orig_h, orig_w) != (INPUT_SIZE, INPUT_SIZE):
        cleaned_mask = cv2.resize(cleaned_mask, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)

    print(f"[segmentation] {model_name.upper()} inference complete. "
          f"Unique classes: {np.unique(cleaned_mask).tolist()}")
    return cleaned_mask
