import cv2
import numpy as np
from pipeline.segmentation import segment_terrain
from pipeline.analysis import analyze_terrain
from pipeline.optimization import generate_layout
from pipeline.renderer import render_blueprint, create_semantic_overlay

test_paths = [
    'data/LoveDA/Train_256/images/0.png',
    'data/LoveDA/Train_256/images/1.png',
    'data/LoveDA/Train_256/images/10.png'
]

for path in test_paths:
    img = cv2.imread(path)
    mask = segment_terrain(img, model_name='deeplabv3')
    analysis = analyze_terrain(mask)
    analysis['segmented_mask'] = mask
    layout = generate_layout(analysis)

    m = layout['metrics']
    print(f"\n==========================================")
    print(f"Sample: {path}")
    print(f"Total Shelters: {m['total_shelters']} (Primary: {m['primary_blocks']}, Infill: {m['infill_blocks']})")
    print(f"Population Capacity: {m['estimated_capacity']} persons")
    print(f"Land Utilization: {m['land_utilization']}")
    print(f"Facilities: Hospital={m['medical_centers']} | Food Court={m['food_distribution']} | Water Tanks={m.get('water_tanks', 0)}")
    print(f"            Water Taps={m['water_points']} | Latrines={m['latrine_blocks']} | Boxes Planned={m.get('residential_boxes', 0)} | Admin Gate={m['admin_posts']}")
    print(f"Avg Walking Distance: {m['avg_walking_distance_m']} m | UNHCR Compliance: {m['unhcr_compliance']}")

    bp = render_blueprint(img, layout, mask, model_name='deeplabv3')
    ov = create_semantic_overlay(img, mask)

    name = path.split('/')[-1].replace('.png', '')
    cv2.imwrite(f'static/test_optimal_{name}_blueprint.png', bp)
    cv2.imwrite(f'static/test_optimal_{name}_overlay.png', ov)

print("\nAll optimal blueprints rendered and saved to static/")
