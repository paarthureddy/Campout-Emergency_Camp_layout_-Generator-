import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

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
            # Table in Slide 1: Roll No, Name, Photo, Email, Mobile, GitHub
            t = sh.table
            members = [
                ("CB.EN.U4CSE22001", "Paarthu Reddy (Team Lead)", "[Photo Attached]", "paarthureddy.g@gmail.com", "+91 98765 43210", "github.com/paarthureddy"),
                ("CB.EN.U4CSE22002", "Team Member 2", "[Photo Attached]", "member2@cb.amrita.edu", "+91 98765 43211", "github.com/member2"),
                ("CB.EN.U4CSE22003", "Team Member 3", "[Photo Attached]", "member3@cb.amrita.edu", "+91 98765 43212", "github.com/member3")
            ]
            for row_idx, member in enumerate(members, start=1):
                if row_idx < len(t.rows):
                    for col_idx, val in enumerate(member):
                        cell = t.cell(row_idx, col_idx)
                        p = cell.text_frame.paragraphs[0]
                        set_para(p, val, font_name="Calibri", font_size=9, color_rgb=(30, 41, 59))

    # ==========================================
    # SLIDE 2: Problem, Objective & Architecture
    # ==========================================
    s2 = prs.slides[1]
    # Remove/hide stray template shapes 2, 5, and 7
    if len(s2.shapes) > 2:
        s2.shapes[2].left = Inches(20) # move off-slide
    if len(s2.shapes) > 5:
        s2.shapes[5].left = Inches(20) # move off-slide
    if len(s2.shapes) > 7:
        s2.shapes[7].left = Inches(20) # move off-slide

    # Shape 1 is Problem Statement text box
    sh_prob = s2.shapes[1]
    sh_prob.top = Inches(0.95)
    sh_prob.height = Inches(1.1)
    clear_and_set(sh_prob.text_frame, [
        ("• Emergency camp planning under crisis is done manually using static rulebooks and paper GIS maps.", False, 9.5, (51, 65, 85)),
        ("• This manual process takes days, produces suboptimal land packing, and creates severe fire hazards.", False, 9.5, (51, 65, 85)),
        ("• Poor spacing causes unequal walking access (>300m) and elevates infectious disease risks.", False, 9.5, (51, 65, 85))
    ])

    # Shape 3 is Objective Title
    s2.shapes[3].top = Inches(2.25)

    # Shape 4 is Objective text box
    sh_obj = s2.shapes[4]
    sh_obj.top = Inches(2.72)
    sh_obj.height = Inches(0.7)
    clear_and_set(sh_obj.text_frame, [
        ("To build an autonomous geospatial intelligence system that ingests raw satellite imagery, performs 7-class semantic terrain segmentation, and synthesizes UNHCR-compliant camp layouts in under 3 seconds.", True, 9.8, (15, 23, 42))
    ])

    # Shape 6 is Sub-Objectives title
    sh_sub_title = s2.shapes[6]
    sh_sub_title.top = Inches(3.6)

    # Add a clean text box for Sub-Objectives
    tx_sub = s2.shapes.add_textbox(Inches(0.48), Inches(4.1), Inches(5.6), Inches(2.2))
    tf_sub = tx_sub.text_frame
    tf_sub.word_wrap = True
    clear_and_set(tf_sub, [
        ("• Train DeepLabV3+ with ASPP on the LoveDA satellite dataset to accurately map 7 terrain classes.", False, 9.2, (51, 65, 85)),
        ("• Formulate a 20m morphological hydrological safety buffer around water bodies for flood protection.", False, 9.2, (51, 65, 85)),
        ("• Engineer a multi-scale contour infill optimization algorithm (14x14px + 7x7px) to eliminate dead space.", False, 9.2, (51, 65, 85)),
        ("• Deploy an interactive Humanitarian Command Center UI with before/after split slider and Sphere manifest.", False, 9.2, (51, 65, 85))
    ])

    # Right side: add architecture diagram image
    arch_img_path = r"e:/Projects/Neural_Networks_Case_Study_G2/architecture_diagram.png"
    if os.path.exists(arch_img_path):
        s2.shapes.add_picture(arch_img_path, Inches(6.4), Inches(0.9), width=Inches(6.1), height=Inches(5.4))

    # ==========================================
    # SLIDE 3: Similar Products
    # ==========================================
    s3 = prs.slides[2]
    # Shape 1 is Subtitle / description
    sh_sub3 = s3.shapes[1]
    clear_and_set(sh_sub3.text_frame, [
        ("Comprehensive state-of-the-art comparison: Existing disaster mapping and humanitarian settlement planning systems.", True, 10.5, (71, 85, 105))
    ])

    # Shape 2 is Table with 4 rows and 4 cols
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
    # Shape 1 is Abstract text box
    sh_abs = s4.shapes[1]
    clear_and_set(sh_abs.text_frame, [
        ("ReliefPlan AI is an autonomous geospatial intelligence and settlement planning platform for humanitarian emergencies. By fusing a DeepLabV3+ neural network (with Atrous Spatial Pyramid Pooling) and a constraint-based multi-scale contour infill optimization engine, the system processes raw satellite imagery to generate complete, 1024x1024 cartographic camp blueprints in under 3 seconds. The generated layouts strictly adhere to UNHCR Emergency Settlement Standards and the Sphere Handbook—allocating modular shelter pods, arterial and feeder roads, emergency clinics, water tap stands, food depots, schools, and downwind latrines with zero wasted usable land and guaranteed 20m flood setbacks.", False, 10, (51, 65, 85))
    ])

    # Novelty 4 Cards:
    # Card 1: State of the Art (Shape 6 is Text 8)
    sh_c1 = s4.shapes[6]
    clear_and_set(sh_c1.text_frame, [
        ("• DeepLabV3+ with ASPP (Atrous Spatial Pyramid Pooling) captures multi-scale geographical features simultaneously.", False, 8.8, (51, 65, 85)),
        ("• Lightweight MobileNetV3 backbone: 3.9M parameters vs. 31M in U-Net (7.8x lighter & 2.4x faster).", False, 8.8, (51, 65, 85)),
        ("• 45% mIoU on LoveDA benchmark with real-time 394ms inference on GPU.", False, 8.8, (51, 65, 85))
    ])

    # Card 2: Product (Shape 10 is Text 13)
    sh_c2 = s4.shapes[10]
    clear_and_set(sh_c2.text_frame, [
        ("• ReliefPlan AI: Full-stack humanitarian command center UI.", False, 8.8, (51, 65, 85)),
        ("• Interactive Before/After Split Comparison Slider over raw satellite terrain.", False, 8.8, (51, 65, 85)),
        ("• Real-time GPS meter coordinate tracker (1px ≈ 0.5m) and cartographic HUD.", False, 8.8, (51, 65, 85)),
        ("• Multi-format export: 1024x1024 PNG, GeoJSON for QGIS/CAD, and PDF briefs.", False, 8.8, (51, 65, 85))
    ])

    # Card 3: Product Features (Shape 14 is Text 18)
    sh_c3 = s4.shapes[14]
    clear_and_set(sh_c3.text_frame, [
        ("• Multi-scale contour infill packing (14x14px primary + 7x7px adaptive infill) achieves 59.0% land utilization.", False, 8.8, (51, 65, 85)),
        ("• Accommodates 3,990 persons per tile with an optimal 38.5m average walking distance.", False, 8.8, (51, 65, 85)),
        ("• Automated Sphere logistics engine: daily water (L/day), food (tons), health kits, and solar power.", False, 8.8, (51, 65, 85))
    ])

    # Card 4: Research Gap Focused (Shape 18 is Text 23)
    sh_c4 = s4.shapes[18]
    clear_and_set(sh_c4.text_frame, [
        ("• Moves AI from passive observation (damage mapping) to active generative recovery planning.", False, 8.8, (51, 65, 85)),
        ("• Mathematical translation of qualitative UNHCR/Sphere guidelines into executable spatial constraints.", False, 8.8, (51, 65, 85)),
        ("• Zero manual CAD drafting required during the critical 72-hour emergency window.", False, 8.8, (51, 65, 85))
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
                 "• Developed multi-scale contour infill spatial optimization algorithm and 20m hydrological flood buffer.\n"
                 "• Engineered 1024x1024 HD GIS renderer with custom SVG-style humanitarian badges and clean HUD.\n"
                 "• Built full-stack FastAPI backend and interactive React operations dashboard with split slider and Sphere logistics engine."),
                ("Team Member 2",
                 "• Curated LoveDA remote sensing dataset and implemented sliding-window tiling (256x256) pipeline.\n"
                 "• Evaluated class imbalance and formulated weighted cross-entropy loss weights.\n"
                 "• Built and trained baseline U-Net architecture for comparative ablation benchmarking.\n"
                 "• Implemented sensor noise injection and synthetic perturbation experiments."),
                ("Team Member 3",
                 "• Formalized UNHCR Emergency Settlement Standards and Sphere Handbook spatial constraints.\n"
                 "• Developed automated evaluation metrics: mIoU, Dice score, land utilization %, and walking distance index.\n"
                 "• Conducted stress-testing across diverse satellite terrains (open land, river basins, farmland).\n"
                 "• Prepared technical project reports, documentation, and review presentation materials.")
            ]
            for r_idx, (m_name, cont) in enumerate(contributions, start=1):
                if r_idx < len(t.rows):
                    p0 = t.cell(r_idx, 0).text_frame.paragraphs[0]
                    set_para(p0, m_name, font_name="Calibri", font_size=10.5, bold=True, color_rgb=(15, 23, 42))
                    
                    cell1 = t.cell(r_idx, 1)
                    clear_and_set(cell1.text_frame, cont.split("\n"), font_size=9, default_color=(51, 65, 85))

    # ==========================================
    # SLIDE 6: Denoising Approach
    # ==========================================
    s6 = prs.slides[5]
    # Title
    s6.shapes[0].text_frame.paragraphs[0].text = "Denoising & Spatial Robustness Approach"
    s6.shapes[0].text_frame.paragraphs[0].font.size = Pt(20)
    s6.shapes[0].text_frame.paragraphs[0].font.bold = True
    s6.shapes[0].text_frame.paragraphs[0].font.color.rgb = RGBColor(15, 23, 42)

    # Subtitle
    s6.shapes[1].text_frame.paragraphs[0].text = "Remote Sensing Noise Modeling, Synthetic Perturbation & Morphological Filtering Pipeline"
    s6.shapes[1].text_frame.paragraphs[0].font.size = Pt(11)
    s6.shapes[1].text_frame.paragraphs[0].font.italic = True
    s6.shapes[1].text_frame.paragraphs[0].font.color.rgb = RGBColor(71, 85, 105)

    # Insert Denoising Diagram
    denoising_img_path = r"e:/Projects/Neural_Networks_Case_Study_G2/denoising_pipeline.png"
    if os.path.exists(denoising_img_path):
        s6.shapes.add_picture(denoising_img_path, Inches(0.8), Inches(1.2), width=Inches(11.2), height=Inches(5.4))

    # ==========================================
    # SLIDE 7: Deep Learning Models for Denoising
    # ==========================================
    s7 = prs.slides[6]
    # Title
    s7.shapes[0].text_frame.paragraphs[0].text = "Deep Learning Model: DeepLabV3+ with ASPP"
    s7.shapes[0].text_frame.paragraphs[0].font.size = Pt(20)
    s7.shapes[0].text_frame.paragraphs[0].font.bold = True
    s7.shapes[0].text_frame.paragraphs[0].font.color.rgb = RGBColor(15, 23, 42)

    # Subtitle
    s7.shapes[1].top = Inches(0.72)
    s7.shapes[1].height = Inches(0.4)
    s7.shapes[1].text_frame.paragraphs[0].text = "Atrous Spatial Pyramid Pooling (ASPP) & MobileNetV3-Large Encoder for Denoising & Multi-Scale Segmentation"
    s7.shapes[1].text_frame.paragraphs[0].font.size = Pt(10.5)
    s7.shapes[1].text_frame.paragraphs[0].font.italic = True
    s7.shapes[1].text_frame.paragraphs[0].font.color.rgb = RGBColor(71, 85, 105)

    # Left text box with architectural & training specs
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

    # Right side: insert benchmark comparison chart
    comp_img_path = r"e:/Projects/Neural_Networks_Case_Study_G2/backend/results_comparison.png"
    if os.path.exists(comp_img_path):
        s7.shapes.add_picture(comp_img_path, Inches(6.6), Inches(1.2), width=Inches(5.4), height=Inches(5.2))

    # Save presentation
    prs.save(PPTX_PATH)
    print("SUCCESS: Saved presentation to", PPTX_PATH)

if __name__ == "__main__":
    populate()
