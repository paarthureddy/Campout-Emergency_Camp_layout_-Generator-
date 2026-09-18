import cv2
import numpy as np

# ─────────────────────────────────────────────────────────
# Colour palette (BGR for OpenCV)
# ─────────────────────────────────────────────────────────
TENT_FILL       = (35,  165, 230)   # warm amber / gold (BGR)
TENT_STROKE     = (15,   90, 145)   # deep amber outline
TENT_STRUCT     = (20,  125, 185)

ROAD_COL        = (190, 195, 200)   # clean gravel/asphalt road
ROAD_DASH_COL   = (30,  220, 245)   # bright yellow/gold centreline

WATER_FILL      = (200, 100,  20)   # deep vibrant blue (BGR)
WATER_STROKE    = (255, 255, 255)

MEDICAL_FILL    = (40,   40, 220)   # bold humanitarian red (BGR)
MEDICAL_STROKE  = (255, 255, 255)

LATRINE_FILL    = (45,  150,  55)   # clean forest green (BGR)
LATRINE_STROKE  = (255, 255, 255)

FOOD_FILL       = (30,  140, 240)   # vibrant gold / amber (BGR)
FOOD_STROKE     = (255, 255, 255)

COMMUNITY_FILL  = (180,  50, 140)   # royal violet / purple (BGR)
COMMUNITY_STROKE= (255, 255, 255)

ADMIN_FILL      = (210, 160,  30)   # deep cyan / teal (BGR)
ADMIN_STROKE    = (255, 255, 255)

# Semantic segmentation class colours (BGR) - All 7 LoveDA classes
SEMANTIC_COLORS = {
    0: (75,   75,  75),    # Background  — dark neutral grey
    1: (30,   30, 210),    # Building    — crimson red
    2: (160, 160, 160),    # Road        — light grey
    3: (215,  95,  15),    # Water       — clear deep blue
    4: (50,  170, 245),    # Barren      — amber sand
    5: (35,  135,  35),    # Forest      — dark green
    6: (45,  215, 125),    # Agriculture — lush green
}

SEMANTIC_LABELS = {
    0: "Background",
    1: "Building",
    2: "Road",
    3: "Water",
    4: "Barren Land",
    5: "Forest / Trees",
    6: "Agriculture",
}

CANVAS_SIZE = 1024  # High-definition rendering canvas


# ─────────────────────────────────────────────────────────
# Internal drawing helpers on HD Canvas
# ─────────────────────────────────────────────────────────

def _blend_rect(canvas, x1, y1, x2, y2, color, alpha):
    x1, y1 = max(0, int(x1)), max(0, int(y1))
    x2, y2 = min(canvas.shape[1], int(x2)), min(canvas.shape[0], int(y2))
    if x2 <= x1 or y2 <= y1:
        return
    sub = canvas[y1:y2, x1:x2]
    overlay = np.full_like(sub, color, dtype=np.uint8)
    cv2.addWeighted(overlay, alpha, sub, 1.0 - alpha, 0, sub)
    canvas[y1:y2, x1:x2] = sub


def _draw_tent_units(canvas, x1, y1, x2, y2):
    """Renders realistic gabled tent units inside a shelter block."""
    w = x2 - x1
    h = y2 - y1
    pad = max(1, w // 8)
    tw = (w - 3 * pad) // 2
    th = (h - 3 * pad) // 2

    if tw <= 3 or th <= 3:
        cv2.rectangle(canvas, (x1, y1), (x2, y2), TENT_FILL, -1)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), TENT_STROKE, 1)
        return

    # Draw 2x2 grid of family tents
    for r in range(2):
        for c in range(2):
            tx = x1 + pad + c * (tw + pad)
            ty = y1 + pad + r * (th + pad)
            cv2.rectangle(canvas, (tx, ty + th // 3), (tx + tw, ty + th), TENT_STRUCT, -1)
            pts = np.array([
                [tx, ty + th // 3],
                [tx + tw, ty + th // 3],
                [tx + tw // 2, ty]
            ], np.int32)
            cv2.fillPoly(canvas, [pts], TENT_FILL)
            cv2.polylines(canvas, [pts], True, TENT_STROKE, 1, cv2.LINE_AA)


def _draw_badge_with_label(canvas, cx, cy, radius, fill_color, stroke_color, label):
    """Draws a crisp circular facility badge with high-contrast text."""
    cv2.circle(canvas, (cx, cy), radius, fill_color, -1, cv2.LINE_AA)
    cv2.circle(canvas, (cx, cy), radius, stroke_color, 2, cv2.LINE_AA)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.40 if radius < 14 else 0.55
    (tw, th), _ = cv2.getTextSize(label, font, scale, 2)
    cv2.putText(canvas, label, (cx - tw // 2, cy + th // 2), font, scale, (255, 255, 255), 2, cv2.LINE_AA)


def _draw_medical_badge(canvas, cx, cy, radius):
    cv2.circle(canvas, (cx, cy), radius, MEDICAL_FILL, -1, cv2.LINE_AA)
    cv2.circle(canvas, (cx, cy), radius, MEDICAL_STROKE, 2, cv2.LINE_AA)
    arm = max(4, radius // 2)
    thick = max(2, radius // 3)
    cv2.line(canvas, (cx - arm, cy), (cx + arm, cy), (255, 255, 255), thick, cv2.LINE_AA)
    cv2.line(canvas, (cx, cy - arm), (cx, cy + arm), (255, 255, 255), thick, cv2.LINE_AA)


def _draw_water_badge(canvas, cx, cy, radius):
    cv2.circle(canvas, (cx, cy), radius, WATER_FILL, -1, cv2.LINE_AA)
    cv2.circle(canvas, (cx, cy), radius, WATER_STROKE, 2, cv2.LINE_AA)
    top_y = cy - int(radius * 0.55)
    r_sub = max(2, int(radius * 0.45))
    cv2.circle(canvas, (cx, cy + 2), r_sub, (255, 255, 255), -1, cv2.LINE_AA)
    pts = np.array([[cx, top_y], [cx - r_sub, cy + 2], [cx + r_sub, cy + 2]], np.int32)
    cv2.fillPoly(canvas, [pts], (255, 255, 255))


def _draw_blueprint_hud(canvas, h, w, metrics):
    """Draws a compact, professional HUD legend in the bottom-right corner."""
    items = [
        (TENT_FILL,       "Shelter Units",    f"{metrics.get('total_shelters', 0)} tents ({metrics.get('estimated_capacity', 0)} cap)"),
        (ROAD_COL,        "Access Roads",     "Arterial & Pedestrian Network"),
        (MEDICAL_FILL,    "Medical Triage",   f"{metrics.get('medical_centers', 0)} hospital clinic"),
        (FOOD_FILL,       "Food Depot",       f"{metrics.get('food_distribution', 0)} ration center"),
        (COMMUNITY_FILL,  "Community/School", f"{metrics.get('community_centers', 0)} child-safe spaces"),
        (WATER_FILL,      "Water Tap Stand",  f"{metrics.get('water_points', 0)} stations (<100m)"),
        (LATRINE_FILL,    "Sanitation Latrine",f"{metrics.get('latrine_blocks', 0)} blocks (offset)"),
        (ADMIN_FILL,      "Camp Gate / Admin",f"{metrics.get('admin_posts', 0)} security post"),
    ]

    item_h = 22
    box_w  = 290
    box_h  = len(items) * item_h + 38
    bx = w - box_w - 18
    by = h - box_h - 18

    # Sleek dark frosted glass panel
    _blend_rect(canvas, bx, by, bx + box_w, by + box_h, (16, 20, 26), 0.88)
    cv2.rectangle(canvas, (bx, by), (bx + box_w, by + box_h), (80, 95, 120), 1, cv2.LINE_AA)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(canvas, "UNHCR CAMP BLUEPRINT LEGEND", (bx + 12, by + 20),
                font, 0.42, (180, 220, 255), 1, cv2.LINE_AA)
    cv2.line(canvas, (bx + 12, by + 26), (bx + box_w - 12, by + 26), (60, 75, 95), 1)

    for i, (color, label, sub) in enumerate(items):
        iy = by + 36 + i * item_h
        cv2.rectangle(canvas, (bx + 12, iy + 2), (bx + 26, iy + 16), color, -1)
        cv2.rectangle(canvas, (bx + 12, iy + 2), (bx + 26, iy + 16), (220, 220, 220), 1)
        cv2.putText(canvas, label, (bx + 32, iy + 13), font, 0.38, (240, 240, 240), 1, cv2.LINE_AA)
        cv2.putText(canvas, sub, (bx + 152, iy + 13), font, 0.33, (165, 185, 205), 1, cv2.LINE_AA)


def _draw_cartographic_annotations(canvas, h, w, title="ReliefPlan AI | Optimal Camp Blueprint", model_name=""):
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Title header banner
    bar_h = 42
    _blend_rect(canvas, 0, 0, w, bar_h, (14, 18, 24), 0.90)
    cv2.line(canvas, (0, bar_h), (w, bar_h), (65, 80, 100), 1)

    full_title = title
    if model_name:
        full_title += f"  [{model_name.upper()}]"
    cv2.putText(canvas, full_title, (18, 27), font, 0.62, (220, 235, 255), 2, cv2.LINE_AA)

    # North arrow in top right
    nx, ny = w - 50, 65
    cv2.arrowedLine(canvas, (nx, ny + 24), (nx, ny - 18), (255, 255, 255), 2, cv2.LINE_AA, tipLength=0.35)
    cv2.putText(canvas, "N", (nx - 6, ny - 24), font, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    # Metric scale bar (bottom-left)
    bar_len = 120
    sx, sy = 24, h - 28
    cv2.line(canvas, (sx, sy), (sx + bar_len, sy), (255, 255, 255), 2, cv2.LINE_AA)
    cv2.line(canvas, (sx, sy - 6), (sx, sy + 6), (255, 255, 255), 2, cv2.LINE_AA)
    cv2.line(canvas, (sx + bar_len, sy - 6), (sx + bar_len, sy + 6), (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(canvas, "~100 m Scale", (sx + 15, sy - 10), font, 0.44, (225, 225, 225), 1, cv2.LINE_AA)


# ─────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────

def create_semantic_overlay(original_image: np.ndarray,
                            segmented_mask: np.ndarray) -> np.ndarray:
    """
    Renders the terrain segmentation map with all 7 LoveDA classes distinctly mapped,
    with an attached right-hand HUD sidebar showing full class labels without clipping.
    """
    hd_img = cv2.resize(original_image, (CANVAS_SIZE, CANVAS_SIZE), interpolation=cv2.INTER_CUBIC)
    hd_mask = cv2.resize(segmented_mask, (CANVAS_SIZE, CANVAS_SIZE), interpolation=cv2.INTER_NEAREST)

    h, w = hd_img.shape[:2]

    # Build coloured semantic mask
    colour_mask = np.zeros((h, w, 3), dtype=np.uint8)
    for cid, color in SEMANTIC_COLORS.items():
        colour_mask[hd_mask == cid] = color

    # Semi-transparent overlay over satellite image
    blended_map = cv2.addWeighted(colour_mask, 0.52, hd_img, 0.48, 0)

    # Side panel legend for terrain classes
    legend_w = 230
    legend_bg = np.full((h, legend_w, 3), (16, 20, 26), dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX

    cv2.putText(legend_bg, "TERRAIN CLASSES", (16, 34),
                font, 0.52, (180, 220, 255), 1, cv2.LINE_AA)
    cv2.line(legend_bg, (16, 44), (legend_w - 16, 44), (70, 85, 105), 1)

    item_h = 50
    for i, (cid, name) in enumerate(SEMANTIC_LABELS.items()):
        color = SEMANTIC_COLORS[cid]
        iy = 65 + i * item_h

        # Class colour swatch
        cv2.rectangle(legend_bg, (16, iy), (42, iy + 24), color, -1)
        cv2.rectangle(legend_bg, (16, iy), (42, iy + 24), (200, 200, 200), 1)

        # Class Name
        cv2.putText(legend_bg, name, (52, iy + 17),
                    font, 0.48, (240, 240, 240), 1, cv2.LINE_AA)

        # Buildable / Exclusion tag
        tag = "Buildable" if cid in (4, 6) else ("Hazard Zone" if cid in (3, 5) else "Reference")
        tag_col = (100, 220, 100) if cid in (4, 6) else ((80, 120, 240) if cid in (3, 5) else (140, 140, 140))
        cv2.putText(legend_bg, tag, (52, iy + 34),
                    font, 0.35, tag_col, 1, cv2.LINE_AA)

    combined = np.concatenate([blended_map, legend_bg], axis=1)

    bar_h = 42
    _blend_rect(combined, 0, 0, combined.shape[1], bar_h, (14, 18, 24), 0.88)
    cv2.line(combined, (0, bar_h), (combined.shape[1], bar_h), (65, 80, 100), 1)
    cv2.putText(combined, "ReliefPlan AI  |  Terrain Semantic Segmentation Map",
                (18, 28), font, 0.62, (220, 235, 255), 2, cv2.LINE_AA)

    return combined


def render_blueprint(original_image: np.ndarray,
                      layout: dict,
                      segmented_mask: np.ndarray,
                      model_name: str = "") -> np.ndarray:
    """
    Renders the GIS-grade emergency camp blueprint at 1024x1024 resolution,
    depicting all 8 facility types with custom badges and zero HUD obstruction.
    """
    canvas = cv2.resize(original_image, (CANVAS_SIZE, CANVAS_SIZE), interpolation=cv2.INTER_CUBIC)
    h, w = CANVAS_SIZE, CANVAS_SIZE

    grid_raw = layout["layout_grid"]
    grid_hd  = cv2.resize(grid_raw, (w, h), interpolation=cv2.INTER_NEAREST)
    seg_hd   = cv2.resize(segmented_mask, (w, h), interpolation=cv2.INTER_NEAREST)

    # 1. Subtle terrain base tint (12% opacity)
    seg_tint = np.zeros_like(canvas)
    for cid, color in SEMANTIC_COLORS.items():
        seg_tint[seg_hd == cid] = color
    canvas = cv2.addWeighted(seg_tint, 0.12, canvas, 0.88, 0)

    # 2. Highlight buildable parcel boundaries with a thin cyan boundary line
    buildable_hd = np.isin(seg_hd, [4, 6]).astype(np.uint8)
    contours, _ = cv2.findContours(buildable_hd, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(canvas, contours, -1, (240, 210, 50), 1, cv2.LINE_AA)

    # 3. Draw Roads (Class 2)
    road_mask = (grid_hd == 2).astype(np.uint8)
    road_dil  = cv2.dilate(road_mask, np.ones((5, 5), np.uint8))
    canvas[road_dil > 0] = ROAD_COL

    # High-visibility dashed centerlines
    dash_len, gap_len = 14, 8
    road_y_coords, road_x_coords = np.where(road_mask > 0)
    for i in range(0, len(road_y_coords), 4):
        ry, rx = road_y_coords[i], road_x_coords[i]
        if (rx // (dash_len + gap_len)) % 2 == 0:
            canvas[ry, rx] = ROAD_DASH_COL

    # 4. Draw Shelter Zones (Class 1) with individual humanitarian tent graphics
    shelter_mask = (grid_hd == 1).astype(np.uint8)
    num_s, s_labels, s_stats, _ = cv2.connectedComponentsWithStats(shelter_mask)

    for sid in range(1, num_s):
        sx = s_stats[sid, cv2.CC_STAT_LEFT]
        sy = s_stats[sid, cv2.CC_STAT_TOP]
        sw = s_stats[sid, cv2.CC_STAT_WIDTH]
        sh = s_stats[sid, cv2.CC_STAT_HEIGHT]
        _draw_tent_units(canvas, sx, sy, sx + sw, sy + sh)

    # Scale facility badge radius
    badge_r = max(11, int(14 * (CANVAS_SIZE / 256) * 0.25))

    # 5. Draw Humanitarian Facility Badges
    # Medical Centers (Class 4) - Red Cross
    num_m, _, _, m_centroids = cv2.connectedComponentsWithStats((grid_hd == 4).astype(np.uint8))
    for mid in range(1, num_m):
        mcx, mcy = int(m_centroids[mid][0]), int(m_centroids[mid][1])
        _draw_medical_badge(canvas, mcx, mcy, int(badge_r * 1.35))

    # Food Distribution Hubs (Class 6) - Gold "F"
    num_f, _, _, f_centroids = cv2.connectedComponentsWithStats((grid_hd == 6).astype(np.uint8))
    for fid in range(1, num_f):
        fcx, fcy = int(f_centroids[fid][0]), int(f_centroids[fid][1])
        _draw_badge_with_label(canvas, fcx, fcy, int(badge_r * 1.25), FOOD_FILL, FOOD_STROKE, "F")

    # Community Centers & Schools (Class 7) - Violet "C"
    num_c, _, _, c_centroids = cv2.connectedComponentsWithStats((grid_hd == 7).astype(np.uint8))
    for cid in range(1, num_c):
        ccx, ccy = int(c_centroids[cid][0]), int(c_centroids[cid][1])
        _draw_badge_with_label(canvas, ccx, ccy, int(badge_r * 1.25), COMMUNITY_FILL, COMMUNITY_STROKE, "C")

    # Water Points (Class 3) - Blue Droplet
    num_w, _, _, w_centroids = cv2.connectedComponentsWithStats((grid_hd == 3).astype(np.uint8))
    for wid in range(1, num_w):
        wcx, wcy = int(w_centroids[wid][0]), int(w_centroids[wid][1])
        _draw_water_badge(canvas, wcx, wcy, badge_r)

    # Latrine / Hygiene Blocks (Class 5) - Green "L"
    num_l, _, _, l_centroids = cv2.connectedComponentsWithStats((grid_hd == 5).astype(np.uint8))
    for lid in range(1, num_l):
        lcx, lcy = int(l_centroids[lid][0]), int(l_centroids[lid][1])
        _draw_badge_with_label(canvas, lcx, lcy, badge_r, LATRINE_FILL, LATRINE_STROKE, "L")

    # Camp Admin / Gate Post (Class 8) - Cyan "A"
    num_a, _, _, a_centroids = cv2.connectedComponentsWithStats((grid_hd == 8).astype(np.uint8))
    for aid in range(1, num_a):
        acx, acy = int(a_centroids[aid][0]), int(a_centroids[aid][1])
        _draw_badge_with_label(canvas, acx, acy, int(badge_r * 1.25), ADMIN_FILL, ADMIN_STROKE, "A")

    # 6. Cartographic HUD annotations (Crisp, never obscuring central camp)
    _draw_cartographic_annotations(canvas, h, w, model_name=model_name)
    _draw_blueprint_hud(canvas, h, w, layout.get("metrics", {}))

    return canvas
