import sys, os
sys.path.insert(0, '.')
from pipeline.segmentation import segment_terrain
from pipeline.analysis import analyze_terrain
from pipeline.optimization import generate_layout
from pipeline.renderer import render_blueprint, create_semantic_overlay
import numpy as np

print("=== Import test: OK ===")
img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

print("Segmenting with UNet...")
mask = segment_terrain(img, "unet")
print(f"  mask shape: {mask.shape}, unique classes: {list(map(int, set(mask.flatten())))}")

analysis = analyze_terrain(mask)
buildable = analysis["buildable_area_pixels"]
breakdown = analysis["class_breakdown"]
print(f"  buildable_pixels: {buildable}")
for k, v in breakdown.items():
    print(f"    {k}: {v['percent']}%")

layout = generate_layout(analysis)
block = layout["block_size"]
metrics = layout["metrics"]
print(f"  block_size: {block}")
print(f"  metrics: {metrics}")

blueprint = render_blueprint(img, layout, mask, model_name="unet")
print(f"  blueprint shape: {blueprint.shape}")

seg_map = create_semantic_overlay(img, mask)
print(f"  segmentation map shape: {seg_map.shape}")

print("=== ALL PIPELINE STEPS PASSED ===")
