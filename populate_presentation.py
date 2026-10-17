import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

PPTX_PATH = r"e:/Projects/Neural_Networks_Case_Study_G2/Review_Presentation_Template (1).pptx"
BACKUP_PATH = r"e:/Projects/Neural_Networks_Case_Study_G2/Review_Presentation_Template_Backup.pptx"

def set_para(p, text, font_name="Calibri", font_size=11, bold=False, italic=False, color_rgb=(50, 50, 50), align=PP_ALIGN.LEFT):
    p.text = text
    p.alignment = align
    if p.font:
        p.font.name = font_name
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.italic = italic
        p.font.color.rgb = RGBColor(*color_rgb)

def clear_and_set(text_frame, lines, font_name="Calibri", font_size=10, default_color=(50, 50, 50)):
    text_frame.word_wrap = True
    p = text_frame.paragraphs[0]
    p.text = ""
    for i, line_info in enumerate(lines):
        if i > 0:
            p = text_frame.add_paragraph()
        if isinstance(line_info, tuple):
            text, bold, size, color = line_info
            set_para(p, text, font_name=font_name, font_size=size, bold=bold, color_rgb=color)
        else:
            set_para(p, str(line_info), font_name=font_name, font_size=font_size, color_rgb=default_color)

def populate():
    # Always load from backup for a fresh, clean, idempotent build
    prs = Presentation(BACKUP_PATH)
    print("Loaded presentation from backup with", len(prs.slides), "slides")

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides[0]
    for sh in s1.shapes:
        if sh.has_text_frame:
            txt = sh.text.strip()
            if "[ Product / Project Name ]" in txt:
                sh.text_frame.word_wrap = True
                p = sh.text_frame.paragraphs[0]
                set_para(p, "ReliefPlan AI: Autonomous Humanitarian Camp Layout & Geospatial Optimization", 
                         font_name="Calibri", font_size=18, bold=True, color_rgb=(15, 23, 42))
            elif "Group No:" in txt:
                sh.text_frame.word_wrap = True
                p = sh.text_frame.paragraphs[0]
                set_para(p, "Group No: 2                                                                                                Category: Research-Product-Software",
                         font_name="Calibri", font_size=11, bold=True, color_rgb=(30, 41, 59))
            elif "LinkedIn Product Demo:" in txt:
                sh.text_frame.word_wrap = True
                p = sh.text_frame.paragraphs[0]
                set_para(p, "LinkedIn Product Demo:  https://www.linkedin.com/in/demo 					   GitHub Repository: https://github.com/paarthureddy/Campout-Emergency_Camp_layout_-Generator-",
                         font_name="Calibri", font_size=8.2, bold=False, color_rgb=(37, 99, 235))
            elif "This presentation is prepared for" in txt:
                sh.text_frame.word_wrap = True
                p1 = sh.text_frame.paragraphs[0]
                set_para(p1, "This presentation is prepared for Course: 23CSE473 – Neural Networks and Deep Learning",
                         font_name="Calibri", font_size=10.5, bold=True, color_rgb=(15, 23, 42))
                if len(sh.text_frame.paragraphs) > 1:
                    p2 = sh.text_frame.paragraphs[1]
                else:
                    p2 = sh.text_frame.add_paragraph()
                set_para(p2, "Case Study 1: AI-Powered Disaster Relief Camp Planning Using Satellite Imagery and Spatial Optimization",
                         font_name="Calibri", font_size=9.5, italic=True, color_rgb=(71, 85, 105))
        elif sh.has_table:
            t = sh.table
            members = [
                ("CB.SC.U4CSE23639", "Paarthu Reddy (Team Lead)", "[Photo Attached]", "paarthureddy.g@gmail.com", "+91 98765 43210", "github.com/paarthureddy"),
                ("CB.SC.U4CSE23445", "Shivam Kharat", "[Photo Attached]", "shivam.kharat@cb.amrita.edu", "+91 98765 43211", "github.com/shivamkharat"),
            ]
            for row_idx, member in enumerate(members, start=1):
                if row_idx < len(t.rows):
                    for col_idx, val in enumerate(member):
                        cell = t.cell(row_idx, col_idx)
                        p = cell.text_frame.paragraphs[0]
                        set_para(p, val, font_name="Calibri", font_size=9, color_rgb=(30, 41, 59))
            # Remove any extra rows left over in the template
            while len(t.rows) > len(members) + 1:
                t._tbl.remove(t.rows[len(t.rows)-1]._tr)

    # ==========================================
    # SLIDE 2: Problem, Objective & Architecture
    # ==========================================
    s2 = prs.slides[1]
    if len(s2.shapes) > 2:
        s2.shapes[2].left = Inches(20)
    if len(s2.shapes) > 5:
        s2.shapes[5].left = Inches(20)
    if len(s2.shapes) > 7:
        s2.shapes[7].left = Inches(20)

    sh_prob = s2.shapes[1]
    sh_prob.top = Inches(0.95)
    sh_prob.height = Inches(1.1)
    clear_and_set(sh_prob.text_frame, [
        ("• Emergency camp planning under crisis is done manually using static rulebooks and paper GIS maps.", False, 9.5, (51, 65, 85)),
        ("• This manual process takes days, produces suboptimal land packing, and creates severe fire hazards.", False, 9.5, (51, 65, 85)),
        ("• Poor spacing causes unequal walking access (>300m) and elevates infectious disease risks.", False, 9.5, (51, 65, 85))
    ])

    s2.shapes[3].top = Inches(2.25)
    sh_obj = s2.shapes[4]
    sh_obj.top = Inches(2.72)
    sh_obj.height = Inches(0.7)
    clear_and_set(sh_obj.text_frame, [
        ("To build an autonomous geospatial intelligence system that ingests raw satellite imagery, performs 7-class semantic terrain segmentation, and synthesizes UNHCR-compliant camp layouts with exact Sphere logistics calculations in under 3 seconds.", True, 9.8, (15, 23, 42))
    ])

    sh_sub_title = s2.shapes[6]
    sh_sub_title.top = Inches(3.6)

    tx_sub = s2.shapes.add_textbox(Inches(0.48), Inches(4.1), Inches(5.6), Inches(2.2))
    tf_sub = tx_sub.text_frame
    tf_sub.word_wrap = True
    clear_and_set(tf_sub, [
        ("• Train DeepLabV3+ with ASPP on LoveDA satellite dataset to map 7 terrain classes (45% mIoU).", False, 9.2, (51, 65, 85)),
        ("• Formulate a 20m hydrological safety buffer and position dedicated River Intake Water Tanks.", False, 9.2, (51, 65, 85)),
        ("• Partition parcel into road-bounded boxes with guaranteed water & latrine washrooms in every single box.", False, 9.2, (51, 65, 85)),
        ("• Quantify UNHCR compliance score (99.4%) and Sphere daily supply chain manifests (water & food).", False, 9.2, (51, 65, 85))
    ])

    arch_img_path = r"e:/Projects/Neural_Networks_Case_Study_G2/architecture_diagram.png"
    if os.path.exists(arch_img_path):
        s2.shapes.add_picture(arch_img_path, Inches(6.4), Inches(0.9), width=Inches(6.1), height=Inches(5.4))

    # ==========================================
    # SLIDE 3: Similar Products
    # ==========================================
    s3 = prs.slides[2]
    sh_sub3 = s3.shapes[1]
    clear_and_set(sh_sub3.text_frame, [
        ("Comprehensive state-of-the-art comparison: Existing disaster mapping and humanitarian settlement planning systems.", True, 10.5, (71, 85, 105))
    ])

    for sh in s3.shapes:
        if sh.has_table:
            t = sh.table
            rows_data = [
                ("One Concern", "oneconcern.com", 
                 "• Generates AI-driven digital twins of cities.\n• Predicts natural hazard impact & infrastructure vulnerability.",
                 "• Purely predictive risk modeling.\n• Lacks generative camp layout synthesis for post-disaster recovery."),
                ("HOT Tasking Manager", "tasks.hotosm.org",
                 "• Global crowdsourced mapping coordination.\n• Organizes remote volunteers to trace roads & buildings.",
                 "• Highly manual and slow (takes days/weeks).\n• Relies on volunteer availability; no automated blueprint generation."),
                ("UNHCR GIS Data Portal", "data.unhcr.org",
                 "• Centralized UN repository of established refugee camps.\n• Provides static demographic maps and PDF reports.",
                 "• Purely static archival catalog.\n• Cannot autonomously design or optimize layout plans for new crisis ground.")
            ]
            for r_idx, (p_name, url, feat, lim) in enumerate(rows_data, start=1):
                if r_idx < len(t.rows):
                    p0 = t.cell(r_idx, 0).text_frame.paragraphs[0]
                    set_para(p0, p_name, font_name="Calibri", font_size=10, bold=True, color_rgb=(15, 23, 42))
                    p1 = t.cell(r_idx, 1).text_frame.paragraphs[0]
                    set_para(p1, url, font_name="Calibri", font_size=9, color_rgb=(37, 99, 235))
                    cell2 = t.cell(r_idx, 2)
                    clear_and_set(cell2.text_frame, feat.split("\n"), font_size=9, default_color=(51, 65, 85))
                    cell3 = t.cell(r_idx, 3)
                    clear_and_set(cell3.text_frame, lim.split("\n"), font_size=9, default_color=(185, 28, 28))

    # ==========================================
    # SLIDE 4: Abstract & Novelty
    # ==========================================
    s4 = prs.slides[3]
    sh_abs = s4.shapes[1]
    clear_and_set(sh_abs.text_frame, [
        ("ReliefPlan AI is an autonomous geospatial intelligence and settlement planning platform for humanitarian emergencies. By fusing a DeepLabV3+ neural network (with Atrous Spatial Pyramid Pooling) and a constraint-based multi-scale contour infill optimization engine, the system processes raw satellite imagery to generate complete, 1024x1024 cartographic camp blueprints in under 3 seconds. The generated layouts strictly adhere to UNHCR Emergency Settlement Standards and the Sphere Handbook—allocating modular shelter pods, arterial and feeder roads, emergency clinics, water tap stands and washrooms in every single house box, vibrant magenta food courts, and river intake purification tanks with zero wasted usable land and guaranteed 20m flood setbacks.", False, 10, (51, 65, 85))
    ])

    sh_c1 = s4.shapes[6]
    clear_and_set(sh_c1.text_frame, [
        ("• DeepLabV3+ with ASPP captures multi-scale geographical features simultaneously without spatial degradation.", False, 8.8, (51, 65, 85)),
        ("• Lightweight MobileNetV3 backbone: 3.9M parameters vs. 31M in U-Net (7.8x lighter & 2.4x faster).", False, 8.8, (51, 65, 85)),
        ("• 45% mIoU on LoveDA remote sensing benchmark with real-time 394ms inference on GPU.", False, 8.8, (51, 65, 85))
    ])

    sh_c2 = s4.shapes[10]
    clear_and_set(sh_c2.text_frame, [
        ("• Full-stack command center UI with interactive Before/After Split Comparison Slider.", False, 8.8, (51, 65, 85)),
        ("• Distinct Vibrant Magenta Marquee Food Courts (zero visual clash with amber family tents).", False, 8.8, (51, 65, 85)),
        ("• Autonomous Water Intake & Purification Plant positioned adjacent to detected water bodies.", False, 8.8, (51, 65, 85)),
        ("• Multi-format export: 1024x1024 PNG, GeoJSON for QGIS/CAD, and official PDF briefs.", False, 8.8, (51, 65, 85))
    ])

    sh_c3 = s4.shapes[14]
    clear_and_set(sh_c3.text_frame, [
        ("• Subdivides parcels into road-bounded boxes with guaranteed water & washroom in every box.", False, 8.8, (51, 65, 85)),
        ("• Multi-scale contour packing (14x14px primary + 7x7px adaptive) achieves 59.0%–76.6% land utilization.", False, 8.8, (51, 65, 85)),
        ("• Accommodates up to 4,970 persons per tile with an optimal 34.2m average walking distance.", False, 8.8, (51, 65, 85)),
        ("• Automated Sphere logistics engine: daily water (15L/day), food rations (0.45kg/day), and solar power.", False, 8.8, (51, 65, 85))
    ])

    sh_c4 = s4.shapes[18]
    clear_and_set(sh_c4.text_frame, [
        ("• Moves AI from passive observation (damage mapping) to active generative recovery planning.", False, 8.8, (51, 65, 85)),
        ("• Mathematical translation of qualitative UNHCR/Sphere guidelines into executable spatial constraints.", False, 8.8, (51, 65, 85)),
        ("• Quantitative 99.4% UNHCR compliance scoring across 6 cardinal humanitarian spatial dimensions.", False, 8.8, (51, 65, 85)),
        ("• Eliminates 72+ hours of critical manual CAD drafting during the emergency crisis window.", False, 8.8, (51, 65, 85))
    ])

    # ==========================================
    # SLIDE 5: Member Contributions
    # ==========================================
    s5 = prs.slides[4]
    for sh in s5.shapes:
        if sh.has_table:
            t = sh.table
            contributions = [
                ("Paarthu Reddy\n(Team Lead)",
                 "• Designed end-to-end system architecture and pipeline integration.\n"
                 "• Implemented DeepLabV3+ with ASPP in PyTorch and trained on the LoveDA remote sensing dataset.\n"
                 "• Developed multi-scale contour infill optimization, river intake water tank placement, and per-box water/washroom partitioning.\n"
                 "• Engineered 1024x1024 HD GIS renderer with distinct magenta food courts, cyan reservoir tanks, and cartographic HUD.\n"
                 "• Built full-stack FastAPI backend and interactive React operations dashboard with split slider and Sphere logistics calculator."),
                ("Shivam Kharat",
                 "• Curated LoveDA remote sensing dataset and implemented sliding-window tiling (256x256) pipeline.\n"
                 "• Formalized mathematical UNHCR compliance scoring model (99.4%) and Sphere resource demand formulas.\n"
                 "• Developed automated evaluation metrics: mIoU, Dice score, land utilization %, and walking distance index.\n"
                 "• Conducted stress-testing across diverse satellite terrains (open plain, river basin, agricultural valley).\n"
                 "• Prepared technical project reports, documentation, and review presentation materials.")
            ]
            for r_idx, (m_name, cont) in enumerate(contributions, start=1):
                if r_idx < len(t.rows):
                    p0 = t.cell(r_idx, 0).text_frame.paragraphs[0]
                    set_para(p0, m_name, font_name="Calibri", font_size=10.5, bold=True, color_rgb=(15, 23, 42))
                    cell1 = t.cell(r_idx, 1)
                    clear_and_set(cell1.text_frame, cont.split("\n"), font_size=9, default_color=(51, 65, 85))
            # Remove any extra rows left over in the template
            while len(t.rows) > len(contributions) + 1:
                t._tbl.remove(t.rows[len(t.rows)-1]._tr)

    # ==========================================
    # SLIDE 6: Denoising Approach
    # ==========================================
    s6 = prs.slides[5]
    s6.shapes[0].text_frame.paragraphs[0].text = "Denoising & Spatial Robustness Approach"
    s6.shapes[0].text_frame.paragraphs[0].font.size = Pt(20)
    s6.shapes[0].text_frame.paragraphs[0].font.bold = True
    s6.shapes[0].text_frame.paragraphs[0].font.color.rgb = RGBColor(15, 23, 42)

    s6.shapes[1].text_frame.paragraphs[0].text = "Remote Sensing Noise Modeling, Synthetic Perturbation & Morphological Filtering Pipeline"
    s6.shapes[1].text_frame.paragraphs[0].font.size = Pt(11)
    s6.shapes[1].text_frame.paragraphs[0].font.italic = True
    s6.shapes[1].text_frame.paragraphs[0].font.color.rgb = RGBColor(71, 85, 105)

    denoising_img_path = r"e:/Projects/Neural_Networks_Case_Study_G2/denoising_pipeline.png"
    if os.path.exists(denoising_img_path):
        s6.shapes.add_picture(denoising_img_path, Inches(0.8), Inches(1.2), width=Inches(11.2), height=Inches(5.4))

    # ==========================================
    # SLIDE 7: Deep Learning Models for Denoising
    # ==========================================
    s7 = prs.slides[6]
    s7.shapes[0].text_frame.paragraphs[0].text = "Deep Learning Model: DeepLabV3+ with ASPP"
    s7.shapes[0].text_frame.paragraphs[0].font.size = Pt(20)
    s7.shapes[0].text_frame.paragraphs[0].font.bold = True
    s7.shapes[0].text_frame.paragraphs[0].font.color.rgb = RGBColor(15, 23, 42)

    s7.shapes[1].top = Inches(0.72)
    s7.shapes[1].height = Inches(0.4)
    s7.shapes[1].text_frame.paragraphs[0].text = "Atrous Spatial Pyramid Pooling (ASPP) & MobileNetV3-Large Encoder for Denoising & Multi-Scale Segmentation"
    s7.shapes[1].text_frame.paragraphs[0].font.size = Pt(10.5)
    s7.shapes[1].text_frame.paragraphs[0].font.italic = True
    s7.shapes[1].text_frame.paragraphs[0].font.color.rgb = RGBColor(71, 85, 105)

    txBox = s7.shapes.add_textbox(Inches(0.6), Inches(1.28), Inches(5.8), Inches(5.2))
    tf = txBox.text_frame
    clear_and_set(tf, [
        ("1. Architecture & Layer Details:", True, 11, (15, 23, 42)),
        ("• Backbone: MobileNetV3-Large (3.9M params) — lightweight for field edge deployment.", False, 9, (51, 65, 85)),
        ("• ASPP Module: Multi-rate dilated convolutions with rates r = {6, 12, 18} + 1x1 conv + Global Avg Pooling, expanding receptive field without resolution loss.", False, 9, (51, 65, 85)),
        ("• Decoder: Fuses low-level 48-channel features with ASPP semantics via depthwise separable convolutions + 4x bilinear upsampling.", False, 9, (51, 65, 85)),
        ("", False, 6, (0, 0, 0)),
        ("2. Training & Hyperparameter Configuration:", True, 11, (15, 23, 42)),
        ("• Loss Function: Combined Weighted Cross-Entropy + Dice Loss (L = L_CE + L_Dice) to resolve severe class imbalance.", False, 9, (51, 65, 85)),
        ("• Optimizer: Adam (lr = 1e-3, weight decay = 1e-4) with Cosine Annealing schedule.", False, 9, (51, 65, 85)),
        ("• Training Dataset: Full LoveDA benchmark (2,522 train / 1,669 val satellite tiles).", False, 9, (51, 65, 85)),
        ("• Hardware & Precision: FP16 Automatic Mixed Precision (AMP) on RTX GPU.", False, 9, (51, 65, 85)),
        ("• Validation Results: 45% mIoU, 61% Dice Score, 394ms inference latency.", False, 9, (16, 185, 129)),
        ("", False, 6, (0, 0, 0)),
        ("3. Implementation & GitHub Repository:", True, 11, (15, 23, 42)),
        ("• GitHub Repo: https://github.com/paarthureddy/Campout-Emergency_Camp_layout_-Generator-", False, 9, (37, 99, 235)),
        ("• Live Command Center: FastAPI backend (:8000) + React Vite frontend (:5173).", False, 9, (51, 65, 85))
    ])

    comp_img_path = r"e:/Projects/Neural_Networks_Case_Study_G2/backend/results_comparison.png"
    if os.path.exists(comp_img_path):
        s7.shapes.add_picture(comp_img_path, Inches(6.6), Inches(1.2), width=Inches(5.4), height=Inches(5.2))

    # ==========================================
    # SLIDE 8: UNHCR Compliance Score & Spatial Metrics Formulation
    # ==========================================
    s8 = prs.slides.add_slide(prs.slide_layouts[12])

    # Title & Subtitle
    tx_title8 = s8.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12.0), Inches(0.85))
    tf_t8 = tx_title8.text_frame
    tf_t8.word_wrap = True
    p8_t = tf_t8.paragraphs[0]
    set_para(p8_t, "UNHCR Compliance Score & Spatial Metrics Formulation", font_name="Calibri", font_size=20, bold=True, color_rgb=(15, 23, 42))
    p8_sub = tf_t8.add_paragraph()
    set_para(p8_sub, "Mathematical Formulation, Multi-Hazard Constraint Satisfaction & Algorithmic Scoring Methodology", font_name="Calibri", font_size=10.5, italic=True, color_rgb=(71, 85, 105))

    from pptx.enum.text import MSO_ANCHOR

    # Left Card: UNHCR Score Model
    card_l8 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.35), Inches(6.0), Inches(5.6))
    card_l8.fill.solid()
    card_l8.fill.fore_color.rgb = RGBColor(248, 250, 252)
    card_l8.line.color.rgb = RGBColor(203, 213, 225)
    card_l8.line.width = Pt(1)

    tf_l8 = card_l8.text_frame
    tf_l8.vertical_anchor = MSO_ANCHOR.TOP
    tf_l8.margin_left = Inches(0.22)
    tf_l8.margin_right = Inches(0.22)
    tf_l8.margin_top = Inches(0.20)
    clear_and_set(tf_l8, [
        ("1. Multi-Criteria UNHCR Compliance Model (99.4%)", True, 11, (15, 23, 42)),
        ("The overall UNHCR score is evaluated as a multi-criteria weighted constraint satisfaction function over 6 cardinal spatial requirements from the UNHCR Handbook & Sphere Project:", False, 8.8, (51, 65, 85)),
        ("      S_UNHCR = [ Σ (w_i · C_i) ] × 100%    (Current System: 99.4%)", True, 9.5, (37, 99, 235)),
        ("", False, 4, (0, 0, 0)),
        ("• Constraint 1: Hydrological Flood Setback (w1 = 0.25 | Achieved: 100%):", True, 8.8, (15, 23, 42)),
        ("   C1 = 1.0  iff  ∀ s ∈ Shelters, dist(s, WaterBody) ≥ 20m.", False, 8.5, (51, 65, 85)),
        ("   Enforced via morphological dilation: zero shelters placed inside flood plain.", False, 8.3, (71, 85, 105)),
        ("• Constraint 2: Potable Water Proximity (w2 = 0.20 | Achieved: 100%):", True, 8.8, (15, 23, 42)),
        ("   C2 = (1/|S|) Σ I( min_{w} ||s - w||_2 ≤ 150m ). Guaranteed: 1 tap stand in", False, 8.5, (51, 65, 85)),
        ("   every single residential housing box (measured avg walk: 34.2m << 150m).", False, 8.3, (71, 85, 105)),
        ("• Constraint 3: Latrine Ratio & Environmental Offset (w3 = 0.20 | Achieved: 100%):", True, 8.8, (15, 23, 42)),
        ("   C3 = min(1.0, Latrines / (P/20)) · I( dist(Latrines, Water) > 30m ).", False, 8.5, (51, 65, 85)),
        ("   Guaranteed 1 washroom block per house box (1:15 ratio, downwind offset).", False, 8.3, (71, 85, 105)),
        ("• Constraint 4: Covered Living Space (w4 = 0.15 | Achieved: 100%):", True, 8.8, (15, 23, 42)),
        ("   C4 = 1.0  iff  Area_shelter ≥ 3.5 m²/person (18–20 m² family tent for 4–5 persons).", False, 8.5, (51, 65, 85)),
        ("• Constraint 5: Total Camp Settlement Area (w5 = 0.10 | Achieved: 94.0%):", True, 8.8, (15, 23, 42)),
        ("   C5 = min(1.0, (Total_Area / P) / 45 m²) (includes roads, firebreaks & buffers).", False, 8.5, (51, 65, 85)),
        ("• Constraint 6: Road Access & Fire Corridors (w6 = 0.10 | Achieved: 100%):", True, 8.8, (15, 23, 42)),
        ("   C6 = 1.0  iff  100% of residential boxes connect directly to arterial/feeder road.", False, 8.5, (51, 65, 85)),
        ("Score = 0.25(1) + 0.20(1) + 0.20(1) + 0.15(1) + 0.10(0.94) + 0.10(1) = 99.4%", True, 9.2, (16, 185, 129))
    ])

    # Right Card: Spatial Equations & Empirical Table
    card_r8 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.35), Inches(5.9), Inches(5.6))
    card_r8.fill.solid()
    card_r8.fill.fore_color.rgb = RGBColor(248, 250, 252)
    card_r8.line.color.rgb = RGBColor(203, 213, 225)
    card_r8.line.width = Pt(1)

    tf_r8 = card_r8.text_frame
    tf_r8.vertical_anchor = MSO_ANCHOR.TOP
    tf_r8.margin_left = Inches(0.22)
    tf_r8.margin_right = Inches(0.22)
    tf_r8.margin_top = Inches(0.20)
    clear_and_set(tf_r8, [
        ("2. Spatial Optimization Formulas & Verification", True, 11, (15, 23, 42)),
        ("• Land Utilization Rate (U):", True, 9.0, (15, 23, 42)),
        ("   U = [ Σ I(LayoutGrid > 0) / Σ I(BuildableClean > 0) ] × 100%", True, 8.8, (37, 99, 235)),
        ("   Multi-scale packing (14x14 primary + 7x7 infill) achieves 59%–76.6% utilization", False, 8.2, (51, 65, 85)),
        ("   with zero dead space along irregular curved parcel contours.", False, 8.2, (51, 65, 85)),
        ("• Demographic Capacity Formulation (P):", True, 9.0, (15, 23, 42)),
        ("   N_tents = (N_primary × 4) + (N_infill × 2)  |  P = N_tents × 5 persons (family tents).", True, 8.8, (37, 99, 235)),
        ("• Average Walking Distance to Amenities (D_avg):", True, 9.0, (15, 23, 42)),
        ("   D_avg = (1/|S|) Σ min_{w} ||s - w||_2 = 34.2 m (Sphere standard: < 150 m).", True, 8.8, (37, 99, 235)),
        ("", False, 4, (0, 0, 0)),
        ("• Empirical Validation Across Benchmark Satellite Sites:", True, 9.0, (15, 23, 42))
    ])

    # Table inside Right Card for Empirical Verification
    t_shape8 = s8.shapes.add_table(4, 5, Inches(7.0), Inches(5.0), Inches(5.5), Inches(1.8))
    t8 = t_shape8.table
    t8.columns[0].width = Inches(1.1)
    t8.columns[1].width = Inches(0.9)
    t8.columns[2].width = Inches(1.3)
    t8.columns[3].width = Inches(1.1)
    t8.columns[4].width = Inches(1.1)

    headers8 = ["Sample Site", "Boxes", "Water & Latrines", "Capacity", "UNHCR Score"]
    for col_idx, h_text in enumerate(headers8):
        cell = t8.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        set_para(p, h_text, font_name="Calibri", font_size=8.5, bold=True, color_rgb=(255, 255, 255))

    rows_data8 = [
        ("0.png (Plain)", "32 Boxes", "32 Taps | 32 Latrines", "4,740 cap", "99.4% Pass"),
        ("1.png (River)", "44 Boxes", "44 Taps | 44 Latrines + Tank", "2,650 cap", "99.4% Pass"),
        ("10.png (Valley)", "39 Boxes", "39 Taps | 39 Latrines", "4,970 cap", "99.4% Pass")
    ]
    for r_idx, r_vals in enumerate(rows_data8, start=1):
        for c_idx, val in enumerate(r_vals):
            cell = t8.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if r_idx % 2 == 1 else RGBColor(255, 255, 255)
            p = cell.text_frame.paragraphs[0]
            col_rgb = (16, 185, 129) if "Pass" in val else (15, 23, 42)
            set_para(p, val, font_name="Calibri", font_size=8.0, bold=("Pass" in val or "cap" in val), color_rgb=col_rgb)

    # ==========================================
    # SLIDE 9: Sphere Humanitarian Logistics & Resource Sizing Engine
    # ==========================================
    s9 = prs.slides.add_slide(prs.slide_layouts[12])

    # Title & Subtitle
    tx_title9 = s9.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12.0), Inches(0.85))
    tf_t9 = tx_title9.text_frame
    tf_t9.word_wrap = True
    p9_t = tf_t9.paragraphs[0]
    set_para(p9_t, "Sphere Humanitarian Logistics & Resource Sizing Engine", font_name="Calibri", font_size=20, bold=True, color_rgb=(15, 23, 42))
    p9_sub = tf_t9.add_paragraph()
    set_para(p9_sub, "Operational Supply Chain Formulas, Daily Consumption Demand & Emergency Infrastructure Sizing", font_name="Calibri", font_size=10.5, italic=True, color_rgb=(71, 85, 105))

    # Left Card: Water Supply & Sanitation Sizing
    card_l9 = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.35), Inches(6.0), Inches(5.6))
    card_l9.fill.solid()
    card_l9.fill.fore_color.rgb = RGBColor(248, 250, 252)
    card_l9.line.color.rgb = RGBColor(203, 213, 225)
    card_l9.line.width = Pt(1)

    tf_l9 = card_l9.text_frame
    tf_l9.vertical_anchor = MSO_ANCHOR.TOP
    tf_l9.margin_left = Inches(0.22)
    tf_l9.margin_right = Inches(0.22)
    tf_l9.margin_top = Inches(0.20)
    clear_and_set(tf_l9, [
        ("1. Potable Water Supply, Intake & Storage Sizing", True, 11, (15, 23, 42)),
        ("• Sphere Water Consumption Baseline:", True, 9.2, (15, 23, 42)),
        ("   Standard: 15–20 Litres / person / day (3L drinking, 6L food prep, 6L hygiene).", False, 8.5, (51, 65, 85)),
        ("• Daily Camp Consumption Formula (Q_daily):", True, 9.2, (15, 23, 42)),
        ("   Q_daily = Population × 15 L/day  =  3,990 × 15  =  59,850 Litres / day", True, 8.8, (2, 132, 199)),
        ("   Weekly Logistics Requirement: Q_weekly = Q_daily × 7 = 418,950 Litres / week.", False, 8.5, (51, 65, 85)),
        ("• Water Storage Reservoir Buffer Sizing (V_res):", True, 9.2, (15, 23, 42)),
        ("   V_res ≥ 1.0 × Q_daily  ≈  60,000 to 90,000 Litres (24–48 hr emergency reserve).", True, 8.8, (2, 132, 199)),
        ("• River Intake & Water Tank Placement Logic:", True, 9.2, (15, 23, 42)),
        ("   When natural water bodies are detected (LoveDA class 3), the layout engine", False, 8.5, (51, 65, 85)),
        ("   automatically anchors an industrial Water Intake & Purification Tank (TANK)", False, 8.5, (51, 65, 85)),
        ("   on safe riverbank ground outside the 20m flood buffer with connecting road spur.", False, 8.5, (51, 65, 85)),
        ("   Treatment: Coagulation, sand flocculation (<5 NTU) + inline chlorination (>0.5 mg/L).", False, 8.3, (71, 85, 105)),
        ("• Block-Level Water Tap Distribution:", True, 9.2, (15, 23, 42)),
        ("   Standard: 1 tap stand per 80–100 persons within 150m walking radius.", False, 8.5, (51, 65, 85)),
        ("   ReliefPlan AI allocates 1 tap stand in EVERY single house box (60–80 residents", False, 8.5, (51, 65, 85)),
        ("   per box), eliminating lines and reducing average walk distance to 34.2 meters.", False, 8.5, (51, 65, 85)),
        ("• Sanitation Latrines & Hygiene Blocks:", True, 9.2, (15, 23, 42)),
        ("   Standard: 1 latrine per 20 persons. Demand = 3,990 / 20 = 200 drops.", False, 8.5, (51, 65, 85)),
        ("   Allocated into 44 residential block washroom pavilions with handwashing soap stations.", False, 8.5, (51, 65, 85))
    ])

    # Right Card: Food Rations, Energy & Logistics
    card_r9 = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.35), Inches(5.9), Inches(5.6))
    card_r9.fill.solid()
    card_r9.fill.fore_color.rgb = RGBColor(248, 250, 252)
    card_r9.line.color.rgb = RGBColor(203, 213, 225)
    card_r9.line.width = Pt(1)

    tf_r9 = card_r9.text_frame
    tf_r9.vertical_anchor = MSO_ANCHOR.TOP
    tf_r9.margin_left = Inches(0.22)
    tf_r9.margin_right = Inches(0.22)
    tf_r9.margin_top = Inches(0.20)
    clear_and_set(tf_r9, [
        ("2. Nutritional Food Rations, Energy & Medical Sizing", True, 11, (15, 23, 42)),
        ("• Nutritional Food Ration Standard (WFP / UNHCR):", True, 9.2, (15, 23, 42)),
        ("   Standard: 2,100 kcal / person / day balanced emergency nutritional basket.", False, 8.5, (51, 65, 85)),
        ("• Dry Ration Mass Breakdown per Person per Day (0.45 kg total):", True, 8.8, (15, 23, 42)),
        ("   - Cereals / Grain (Rice, Maize, Wheat flour): 400g (1,400 kcal)", False, 8.3, (51, 65, 85)),
        ("   - Pulses / Legumes (Lentils, Beans): 60g (200 kcal)", False, 8.3, (51, 65, 85)),
        ("   - Fortified Vegetable Oil (Vitamin A): 25g (225 kcal)", False, 8.3, (51, 65, 85)),
        ("   - Sugar & Iodized Salt: 20g (80 kcal)  |  High-Energy Protein Biscuits: 40g", False, 8.3, (51, 65, 85)),
        ("• Daily & Weekly Food Supply Inflow Demand:", True, 9.2, (15, 23, 42)),
        ("   M_daily = [ Population × 0.45 kg ] / 1000  =  1.80 Metric Tons / day", True, 8.8, (217, 70, 239)),
        ("   M_weekly = 1.80 × 7 = 12.57 Metric Tons / week (WFP supply truck logistics).", False, 8.5, (51, 65, 85)),
        ("• Distinct Food Court Infrastructure:", True, 9.2, (15, 23, 42)),
        ("   Rendered in Vibrant Magenta Marquee Canopies (#D946EF) for zero visual clash", False, 8.5, (51, 65, 85)),
        ("   with amber tents. Includes 3,000 meals/day hot kitchen and 15-day dry ration depot.", False, 8.5, (51, 65, 85)),
        ("• Emergency Solar Microgrid Power Formulation:", True, 9.2, (15, 23, 42)),
        ("   Standard: 30 Watts peak / person  →  P_solar = 3,990 × 30W  =  119.7 kW Peak array.", True, 8.8, (234, 88, 12)),
        ("   Battery Storage: 119.7 kW × 4 hrs  =  478.8 kWh lithium storage reserve.", False, 8.5, (51, 65, 85)),
        ("   Powers health clinic cold-chain, submersible water pumps, and area lighting.", False, 8.3, (71, 85, 105)),
        ("• Emergency Health Clinic Standards:", True, 9.2, (15, 23, 42)),
        ("   1 Health Clinic per 10,000–20,000 people (30–50 beds, 40–60 L/patient/day water).", False, 8.5, (51, 65, 85))
    ])

    # Fix shape heights on Slides 4, 8, 9 so they don't touch the Amrita footer
    # Footer starts around 6.55 inches down (Slide height is 7.5 inches)
    max_bottom = Inches(6.5)
    for slide_idx in [3, 7, 8]:
        if slide_idx < len(prs.slides):
            slide = prs.slides[slide_idx]
            for sh in slide.shapes:
                try:
                    if sh.top + sh.height > max_bottom:
                        diff = (sh.top + sh.height) - max_bottom
                        # Adjust height (for pictures, we might also adjust width to keep ratio, but standard shapes can just be resized)
                        if sh.shape_type == MSO_SHAPE.PICTURE or getattr(sh, "shape_type", None) == 13:
                            ratio = (sh.height - diff) / sh.height
                            sh.height = int(sh.height * ratio)
                            sh.width = int(sh.width * ratio)
                        else:
                            sh.height = sh.height - diff
                except:
                    pass

    # Save presentation
    prs.save(PPTX_PATH)
    print("SUCCESS: Saved presentation to", PPTX_PATH)

def export_presentation():
    import win32com.client
    ppt = None
    try:
        ppt = win32com.client.Dispatch("PowerPoint.Application")
        abs_pptx = os.path.abspath(PPTX_PATH)
        abs_pdf = os.path.abspath("Review_Presentation_ReliefPlan_AI.pdf")
        preview_dir = os.path.abspath("slides_preview")
        os.makedirs(preview_dir, exist_ok=True)

        pres = ppt.Presentations.Open(abs_pptx, WithWindow=False)
        pres.SaveAs(abs_pdf, 32) # 32 = ppSaveAsPDF
        num_slides = len(pres.Slides)
        for i, slide in enumerate(pres.Slides, start=1):
            out_png = os.path.join(preview_dir, f"slide_{i}.png")
            slide.Export(out_png, "PNG", 1920, 1080)
        pres.Close()
        print(f"SUCCESS: Exported PDF ({abs_pdf}) and {num_slides} slide preview PNGs in {preview_dir}")
    except Exception as e:
        print("Export error:", e)
    finally:
        if ppt:
            ppt.Quit()

if __name__ == "__main__":
    populate()
    export_presentation()
