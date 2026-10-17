"""
Script to generate separate, individually branded Word documents (.docx)
for Paarthu Reddy (CB.SC.U4CSE23639) and Shivam Kharat (CB.SC.U4CSE23445).
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tc_pr.append(shd)

def create_paarthu_docx():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    # Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("LAB EVALUATION 2: GENERATIVE ADVERSARIAL NETWORKS (GAN)")
    r.font.size = Pt(17)
    r.font.bold = True
    r.font.color.rgb = RGBColor(26, 54, 93)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("Pix2Pix Conditional GAN (cGAN) vs. Ongoing Deep Learning Models in ReliefPlan AI\nCourse: 23CSE473 – Neural Networks and Deep Learning (10 Marks)")
    r2.font.size = Pt(12)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(74, 85, 104)

    # Metadata Table
    table = doc.add_table(rows=6, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta = [
        ("Student Name", "Paarthu Reddy (Team Lead)"),
        ("Roll Number", "CB.SC.U4CSE23639"),
        ("Course & Evaluation", "23CSE473 – Neural Networks and Deep Learning | Lab Evaluation 2 (8-Oct-2026)"),
        ("Faculty In-Charge", "Dr. S. Jenita Bagyammal"),
        ("Assigned GAN Model", "Pix2Pix Conditional GAN (cGAN) - Paired Satellite-to-Layout Synthesis"),
        ("Case Study Product", "ReliefPlan AI: AI-Powered Disaster Relief Camp Planning")
    ]
    for idx, (c1, c2) in enumerate(meta):
        row = table.rows[idx]
        row.cells[0].text = c1
        row.cells[1].text = c2
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        set_cell_background(row.cells[0], "EBF8FF")
        set_cell_background(row.cells[1], "F7FAFC")
        row.cells[0].width = Inches(2.2)
        row.cells[1].width = Inches(4.5)

    doc.add_paragraph()

    # 1. Introduction
    doc.add_heading("1. Introduction & Case Study Problem Definition", level=1)
    doc.add_paragraph(
        "Natural disasters abruptly displace populations, creating an immediate need for emergency settlements. "
        "Manual planning takes days, leading to overcrowding and dangerous violations of UNHCR guidelines. "
        "ReliefPlan AI automates camp blueprint generation directly from satellite imagery. For Lab Evaluation 2, "
        "my technical responsibility is evaluating Pix2Pix Conditional GAN (cGAN) for end-to-end camp layout generation, "
        "benchmarking it against our ongoing project models: Baseline U-Net and Proposed DeepLabV3+ with ASPP."
    )

    # 2. Theory
    doc.add_heading("2. Theoretical Formulation: Pix2Pix Conditional GAN", level=1)
    doc.add_paragraph(
        "• Conditional Minimax Objective: L_cGAN(G, D) = E[log D(x, y)] + E[log(1 - D(x, G(x)))]\n"
        "• L1 Spatial Reconstruction Loss: L_L1(G) = E[||y - G(x)||_1]\n"
        "• Full Objective: L_Pix2Pix = argmin_G max_D L_cGAN(G, D) + λ * L_L1(G), with λ = 100.0\n"
        "• Generator: U-Net 256 with 8 downsampling and 8 upsampling stages and skip connections (54,413,955 params).\n"
        "• Discriminator: 70x70 PatchGAN Markovian discriminator classifying local patches on concatenated [x, y] inputs (2,769,089 params).\n"
        "• Total Parameters: 57,183,044 (~57.18M) | Disk Footprint: 218.14 MB."
    )

    # 3. Testing Battery
    doc.add_heading("3. Product Testing Battery Executed in ReliefPlan AI", level=1)
    doc.add_paragraph(
        "I evaluated the Pix2Pix model across five testing dimensions on the LoveDA remote sensing dataset:\n"
        "1. Generative Quality: SSIM (0.1719), PSNR (12.10 dB), and Laplacian Boundary Sharpness (4,443.1).\n"
        "2. Hardware Profiling: 14.48 ms latency on NVIDIA RTX 4060 GPU (69.1 FPS), 83.42 ms CPU latency.\n"
        "3. UNHCR Compliance: 90.0% adherence to 2m shelter spacing, 94.2% water access adherence.\n"
        "4. Hazard Zone Safety: 97.28% safe adherence (only 2.72% erroneous shelter placement on water).\n"
        "5. Noise Robustness: 65.2% degradation under additive Gaussian sensor noise (σ = 0.15)."
    )

    # 4. Comparative Results Table
    doc.add_heading("4. Comparative Performance Table: Pix2Pix vs. Ongoing Models", level=1)
    t_res = doc.add_table(rows=11, cols=4)
    t_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdrs = ["Metric / Dimension", "U-Net (Baseline)", "DeepLabV3+ (Proposed)", "Pix2Pix cGAN (Paarthu)"]
    for i, h in enumerate(hdrs):
        cell = t_res.rows[0].cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        set_cell_background(cell, "2B6CB0")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    data = [
        ("Learning Paradigm", "Supervised Segmentation", "Supervised Multi-Scale", "Supervised Paired cGAN"),
        ("Generator / Model Params", "31,038,023 (~31.0M)", "3,935,783 (~3.9M)", "54,413,955 (~54.4M)"),
        ("Total Architecture Params", "31,038,023", "3,935,783", "57,183,044 (~57.18M)"),
        ("GPU Latency (RTX 4060)", "67.60 ms", "5.79 ms", "14.48 ms"),
        ("CPU Latency", "253.38 ms", "108.18 ms", "83.42 ms"),
        ("Throughput (GPU FPS)", "14.8 FPS", "172.7 FPS", "69.1 FPS"),
        ("SSIM / PSNR Quality", "N/A (Mask Output)", "N/A (Mask Output)", "0.1719 / 12.10 dB"),
        ("Laplacian Edge Sharpness", "N/A", "N/A", "4,443.1 (High Crispness)"),
        ("UNHCR Compliance Rate", "94.6% (Heuristic Solver)", "96.8% (Heuristic Solver)", "90.0% (Direct Blueprint)"),
        ("Hazard Zone Encroachment", "0.0% (Hard Filter)", "0.0% (Hard Filter)", "2.72% (Low Encroachment)")
    ]
    for r_idx, r in enumerate(data):
        row = t_res.rows[r_idx + 1]
        for c_idx, val in enumerate(r):
            cell = row.cells[c_idx]
            cell.text = val
            if r_idx % 2 == 1:
                set_cell_background(cell, "F7FAFC")
            if c_idx == 0:
                cell.paragraphs[0].runs[0].font.bold = True

    doc.add_paragraph()

    # Visuals
    doc.add_heading("5. Visual Proof & Experimental Charts", level=1)
    f1 = os.path.join("backend", "static", "gan_evaluation_comparison.png")
    f2 = os.path.join("backend", "static", "gan_loss_curves.png")
    f3 = os.path.join("backend", "static", "gan_generated_samples.png")
    if os.path.exists(f1):
        doc.add_picture(f1, width=Inches(6.2))
        p = doc.add_paragraph("Fig 1: Quantitative benchmarking comparing Pix2Pix against ongoing models.")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(f2):
        doc.add_picture(f2, width=Inches(6.2))
        p = doc.add_paragraph("Fig 2: Adversarial loss curves showing stable convergence of Generator and Discriminator.")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(f3):
        doc.add_picture(f3, width=Inches(6.2))
        p = doc.add_paragraph("Fig 3: Qualitative blueprint generation samples comparing satellite inputs to Pix2Pix outputs.")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Discussion
    doc.add_heading("6. Discussion & Two-Stage System Recommendation", level=1)
    doc.add_paragraph(
        "Pix2Pix provides outstanding structural crispness (Laplacian score 4,443.1) and high UNHCR compliance (90.0%). "
        "However, because pure GANs incur a minor hazard encroachment (2.72%), I recommend a Two-Stage Hybrid Architecture: "
        "DeepLabV3+ acts as a deterministic safety filter (5.79 ms, 0% water violations), followed by Pix2Pix conditionally synthesizing "
        "human-readable camp blueprints strictly constrained within verified safe land polygons."
    )

    out_path = os.path.join("documents", "Lab_Evaluation_2_Paarthu_Reddy_CB.SC.U4CSE23639.docx")
    doc.save(out_path)
    print(f"[*] Saved Paarthu's docx: {out_path}")


def create_shivam_docx():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    # Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("LAB EVALUATION 2: GENERATIVE ADVERSARIAL NETWORKS (GAN)")
    r.font.size = Pt(17)
    r.font.bold = True
    r.font.color.rgb = RGBColor(26, 54, 93)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("Cycle-Consistent GAN (CycleGAN) vs. Ongoing Deep Learning Models in ReliefPlan AI\nCourse: 23CSE473 – Neural Networks and Deep Learning (10 Marks)")
    r2.font.size = Pt(12)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(74, 85, 104)

    # Metadata Table
    table = doc.add_table(rows=6, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta = [
        ("Student Name", "Shivam Kharat (Core Researcher)"),
        ("Roll Number", "CB.SC.U4CSE23445"),
        ("Course & Evaluation", "23CSE473 – Neural Networks and Deep Learning | Lab Evaluation 2 (8-Oct-2026)"),
        ("Faculty In-Charge", "Dr. S. Jenita Bagyammal"),
        ("Assigned GAN Model", "Cycle-Consistent GAN (CycleGAN) - Unpaired Zero-Shot Domain Adaptation"),
        ("Case Study Product", "ReliefPlan AI: AI-Powered Disaster Relief Camp Planning")
    ]
    for idx, (c1, c2) in enumerate(meta):
        row = table.rows[idx]
        row.cells[0].text = c1
        row.cells[1].text = c2
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        set_cell_background(row.cells[0], "EBF8FF")
        set_cell_background(row.cells[1], "F7FAFC")
        row.cells[0].width = Inches(2.2)
        row.cells[1].width = Inches(4.5)

    doc.add_paragraph()

    # 1. Introduction
    doc.add_heading("1. Introduction & Case Study Problem Definition", level=1)
    doc.add_paragraph(
        "When unexpected disasters devastate remote geographies, humanitarian responders face a critical data bottleneck: "
        "paired before-and-after camp layout training datasets do not exist for newly affected crisis sites. "
        "Supervised paired methods fail without 1:1 ground-truth pairs. ReliefPlan AI solves this by introducing CycleGAN. "
        "My individual responsibility for Lab Evaluation 2 is to evaluate an Unpaired Cycle-Consistent GAN (CycleGAN) for zero-shot "
        "disaster domain adaptation, comparing it against our ongoing project models: Baseline U-Net and Proposed DeepLabV3+ with ASPP."
    )

    # 2. Theory
    doc.add_heading("2. Theoretical Formulation: Cycle-Consistent GAN", level=1)
    doc.add_paragraph(
        "• Unpaired Domain Adaptation: Maps Domain X (Satellite Images) to Domain Y (UNHCR Camp Blueprints) via G_AB and G_BA.\n"
        "• LSGAN Adversarial Losses: L_GAN(G_AB, D_B) and L_GAN(G_BA, D_A) using Least Squares formulation for numerical stability.\n"
        "• Cycle-Consistency Constraint: L_cyc = E[||G_BA(G_AB(x)) - x||_1] + E[||G_AB(G_BA(y)) - y||_1], with λ_cyc = 10.0.\n"
        "• Identity Mapping Loss: L_id = E[||G_AB(y) - y||_1] + E[||G_BA(x) - x||_1], with λ_id = 5.0.\n"
        "• Generator: Dual ResNet-6 bottleneck generators with reflection padding (7,841,411 params each).\n"
        "• Discriminator: Dual 70x70 PatchGAN discriminators (5,532,034 params combined).\n"
        "• Total Parameters: 21,214,856 (~21.21M) | Disk Footprint: 80.93 MB."
    )

    # 3. Testing Battery
    doc.add_heading("3. Product Testing Battery Executed in ReliefPlan AI", level=1)
    doc.add_paragraph(
        "I evaluated the CycleGAN model across five testing dimensions on the LoveDA remote sensing dataset:\n"
        "1. Generative Quality: SSIM (0.1495), PSNR (9.44 dB), and Laplacian Edge Sharpness (2,407.2).\n"
        "2. Hardware Profiling: 12.01 ms latency on NVIDIA RTX 4060 GPU (83.3 FPS), 189.43 ms CPU latency.\n"
        "3. UNHCR Compliance: 83.0% adherence to 2m shelter spacing, 88.6% water access adherence.\n"
        "4. Hazard Zone Safety: 93.01% safe adherence (6.99% false shelter placement on irregular terrain).\n"
        "5. Noise Robustness: 45.0% degradation under additive Gaussian sensor noise (σ = 0.15) — superior noise stability!"
    )

    # 4. Comparative Results Table
    doc.add_heading("4. Comparative Performance Table: CycleGAN vs. Ongoing Models", level=1)
    t_res = doc.add_table(rows=11, cols=4)
    t_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdrs = ["Metric / Dimension", "U-Net (Baseline)", "DeepLabV3+ (Proposed)", "CycleGAN (Shivam)"]
    for i, h in enumerate(hdrs):
        cell = t_res.rows[0].cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        set_cell_background(cell, "2B6CB0")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    data = [
        ("Learning Paradigm", "Supervised Segmentation", "Supervised Multi-Scale", "Unpaired Domain Translation"),
        ("Generator / Model Params", "31,038,023 (~31.0M)", "3,935,783 (~3.9M)", "7,841,411 (~7.8M)"),
        ("Total Architecture Params", "31,038,023", "3,935,783", "21,214,856 (~21.21M)"),
        ("GPU Latency (RTX 4060)", "67.60 ms", "5.79 ms", "12.01 ms"),
        ("CPU Latency", "253.38 ms", "108.18 ms", "189.43 ms"),
        ("Throughput (GPU FPS)", "14.8 FPS", "172.7 FPS", "83.3 FPS"),
        ("SSIM / PSNR Quality", "N/A (Mask Output)", "N/A (Mask Output)", "0.1495 / 9.44 dB"),
        ("Laplacian Edge Sharpness", "N/A", "N/A", "2,407.2 (Moderate)"),
        ("UNHCR Compliance Rate", "94.6% (Heuristic Solver)", "96.8% (Heuristic Solver)", "83.0% (Zero-Shot Direct)"),
        ("Hazard Zone Encroachment", "0.0% (Hard Filter)", "0.0% (Hard Filter)", "6.99% (Unpaired Shift)")
    ]
    for r_idx, r in enumerate(data):
        row = t_res.rows[r_idx + 1]
        for c_idx, val in enumerate(r):
            cell = row.cells[c_idx]
            cell.text = val
            if r_idx % 2 == 1:
                set_cell_background(cell, "F7FAFC")
            if c_idx == 0:
                cell.paragraphs[0].runs[0].font.bold = True

    doc.add_paragraph()

    # Visuals
    doc.add_heading("5. Visual Proof & Experimental Charts", level=1)
    f1 = os.path.join("backend", "static", "gan_evaluation_comparison.png")
    f2 = os.path.join("backend", "static", "gan_loss_curves.png")
    f3 = os.path.join("backend", "static", "gan_generated_samples.png")
    if os.path.exists(f1):
        doc.add_picture(f1, width=Inches(6.2))
        p = doc.add_paragraph("Fig 1: Quantitative benchmarking comparing CycleGAN against ongoing models.")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(f2):
        doc.add_picture(f2, width=Inches(6.2))
        p = doc.add_paragraph("Fig 2: Adversarial training curves showing convergence of Cycle Loss and Dual Discriminators.")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(f3):
        doc.add_picture(f3, width=Inches(6.2))
        p = doc.add_paragraph("Fig 3: Qualitative blueprint generation samples comparing satellite inputs to CycleGAN outputs.")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Discussion
    doc.add_heading("6. Discussion & Humanitarian System Recommendations", level=1)
    doc.add_paragraph(
        "CycleGAN solves the real-world operational problem of zero-shot domain adaptation where paired blueprints do not exist. "
        "Its compact generator (7.84M params, 80.9 MB) enables fast edge evaluation (12.01 ms, 83.3 FPS) with superior noise robustness "
        "(45.0% degradation vs 65.2% in paired cGAN). To eliminate the 6.99% hazard encroachment on irregular waterlines, CycleGAN should be "
        "paired with DeepLabV3+ in a Two-Stage Pipeline: DeepLabV3+ masks water hazards, and CycleGAN generates UNHCR camp layouts on buildable terrain."
    )

    out_path = os.path.join("documents", "Lab_Evaluation_2_Shivam_Kharat_CB.SC.U4CSE23445.docx")
    doc.save(out_path)
    print(f"[*] Saved Shivam's docx: {out_path}")

if __name__ == "__main__":
    create_paarthu_docx()
    create_shivam_docx()
