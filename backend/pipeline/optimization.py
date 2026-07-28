import numpy as np

def generate_layout(terrain_analysis):
    """
    Constraint-based Layout Optimization Engine.
    Positions tent blocks, roads, and facilities satisfying humanitarian standards.
    Input: terrain_analysis dictionary containing 'buildable_mask'.
    Output: layout_grid and calculated metrics.
    """
    buildable_mask = terrain_analysis["buildable_mask"]
    
    # 0: Unbuildable, 1: Shelter, 2: Road, 3: Water, 4: Medical
    layout_grid = np.zeros_like(buildable_mask, dtype=np.uint8)
    
    h, w = buildable_mask.shape
    
    # Heuristic constraints
    block_size = 10 # Assuming 10x10 pixels per grid block
    
    shelters_placed = 0
    water_points = 0
    medical_centers = 0
    
    # Main Road Generation (Cross across the center of buildable mass)
    center_y, center_x = h // 2, w // 2
    for y in range(h):
        for x in range(w):
            if buildable_mask[y, x] == 1:
                # If near horizontal or vertical center line, mark as Road
                if abs(y - center_y) < 3 or abs(x - center_x) < 3:
                    layout_grid[y, x] = 2
    
    # Place Facilities and Shelters in blocks
    for y in range(0, h, block_size):
        for x in range(0, w, block_size):
            block = buildable_mask[y:y+block_size, x:x+block_size]
            layout_block = layout_grid[y:y+block_size, x:x+block_size]
            
            # If the block is completely buildable and not a road
            if np.mean(block) > 0.8 and np.all(layout_block != 2):
                # Place Medical Center (roughly center)
                if medical_centers < 1 and abs(y - center_y) < 50 and abs(x - center_x) < 50:
                    layout_grid[y:y+block_size, x:x+block_size] = 4
                    medical_centers += 1
                # Place Water points (regular intervals)
                elif (y // block_size) % 5 == 0 and (x // block_size) % 5 == 0:
                    layout_grid[y:y+block_size, x:x+block_size] = 3
                    water_points += 1
                # Otherwise Place Shelter
                else:
                    layout_grid[y:y+block_size, x:x+block_size] = 1
                    shelters_placed += 1
    
    # Calculate Metrics
    # Assuming 1 pixel = 1 m^2. Block = 100m^2. A shelter block can hold ~2 tents (45m^2 each)
    total_shelters = shelters_placed * 2
    total_placed_area = (shelters_placed + water_points + medical_centers) * (block_size**2)
    buildable_area = terrain_analysis["buildable_area_pixels"]
    
    land_utilization = (total_placed_area / buildable_area * 100) if buildable_area > 0 else 0
    
    return {
        "layout_grid": layout_grid,
        "metrics": {
            "land_utilization_percent": round(land_utilization, 2),
            "total_shelters": total_shelters,
            "avg_walking_distance_m": 35, # Mock heuristic calculation
            "facilities": {
                "medical_centers": medical_centers,
                "water_points": water_points,
                "latrines": total_shelters // 20  # 1 latrine per 20 people (assume 1 person per shelter for simplicity)
            }
        }
    }
