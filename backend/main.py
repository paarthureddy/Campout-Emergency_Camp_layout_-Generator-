import os
import cv2
import numpy as np
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uuid
from pydantic import BaseModel
from typing import Dict, Any
import subprocess

class UploadResponse(BaseModel):
    message: str
    job_id: str
    blueprint_url: str
    segmentation_url: str
    results: Dict[str, Any]

class StatusResponse(BaseModel):
    job_id: str
    status: str
    results: Dict[str, Any]

# Import pipeline modules
from pipeline.segmentation import segment_terrain
from pipeline.analysis     import analyze_terrain
from pipeline.optimization import generate_layout
from pipeline.renderer     import render_blueprint, create_semantic_overlay

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ReliefPlan AI Backend",
    description="API for automated disaster relief camp planning."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from config import STATIC_DIR, DATA_DIR

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/data",   StaticFiles(directory=DATA_DIR),   name="data")


@app.get("/api/dataset/images")
def get_dataset_images():
    train_images_dir = os.path.join(DATA_DIR, "Train_256", "images")
    if not os.path.exists(train_images_dir):
        return {"images": []}
    files = sorted([f for f in os.listdir(train_images_dir) if f.endswith(".png")])
    return {"images": files[:50]}


@app.get("/api/models/compare")
def get_model_comparison():
    return {
        "unet":      "http://localhost:8000/static/learning_curves_unet.png",
        "deeplabv3": "http://localhost:8000/static/learning_curves_deeplabv3.png",
    }


@app.post("/api/train")
def trigger_training(model: str = "unet"):
    # Never run destructive fast_demo that overwrites good checkpoints
    return {"message": "Training must be run via train.py directly with explicit epochs.", "status": "disabled"}


@app.get("/")
def read_root():
    return {"message": "Welcome to the ReliefPlan AI API"}


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ReliefPlan AI Backend"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...), model: str = Form("unet")):
    job_id = str(uuid.uuid4())
    logger.info(f"[{job_id}] Processing started — model: {model}")

    try:
        # ── Read image ────────────────────────────────────────────────────────
        contents = await file.read()
        nparr    = np.frombuffer(contents, np.uint8)
        original_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if original_image is None:
            raise ValueError("Invalid image format — could not decode.")

        # ── 1. Segmentation ───────────────────────────────────────────────────
        logger.info(f"[{job_id}] Running segmentation with {model.upper()}...")
        segmented_mask = segment_terrain(original_image, model_name=model)

        # ── 2. Analysis ───────────────────────────────────────────────────────
        logger.info(f"[{job_id}] Analyzing terrain...")
        terrain_analysis = analyze_terrain(segmented_mask)
        terrain_analysis["segmented_mask"] = segmented_mask

        # ── 3. Layout optimisation ────────────────────────────────────────────
        logger.info(f"[{job_id}] Generating layout...")
        layout = generate_layout(terrain_analysis)

        # ── 4. Render blueprint ───────────────────────────────────────────────
        logger.info(f"[{job_id}] Rendering blueprint...")
        blueprint = render_blueprint(
            original_image, layout, segmented_mask, model_name=model
        )

        # ── 5. Render segmentation map ────────────────────────────────────────
        logger.info(f"[{job_id}] Rendering segmentation map...")
        seg_map = create_semantic_overlay(original_image, segmented_mask)

        # ── Save outputs ──────────────────────────────────────────────────────
        blueprint_filename   = f"{job_id}_blueprint.png"
        seg_filename         = f"{job_id}_segmentation.png"
        blueprint_path = os.path.join(STATIC_DIR, blueprint_filename)
        seg_path       = os.path.join(STATIC_DIR, seg_filename)

        cv2.imwrite(blueprint_path, blueprint)
        cv2.imwrite(seg_path,       seg_map)

        logger.info(f"[{job_id}] Pipeline complete. "
                    f"Shelters: {layout['metrics']['total_shelters']}, "
                    f"Buildable: {terrain_analysis['buildable_area_pixels']}px")

        return JSONResponse(status_code=200, content={
            "message":         f"Pipeline completed using {model} model.",
            "job_id":          job_id,
            "blueprint_url":   f"http://localhost:8000/static/{blueprint_filename}",
            "segmentation_url": f"http://localhost:8000/static/{seg_filename}",
            "results": {
                **layout["metrics"],
                "class_breakdown": terrain_analysis["class_breakdown"],
                "buildable_area_pixels": terrain_analysis["buildable_area_pixels"],
            },
        })

    except Exception as e:
        logger.error(f"[{job_id}] Pipeline failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image processing failed: {e}")


@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    return {
        "job_id":  job_id,
        "status":  "completed",
        "results": {
            "land_utilization_percent": 85,
            "total_shelters":           450,
            "avg_walking_distance_m":    42,
            "facilities": {
                "medical_centers": 2,
                "water_points":    15,
                "latrines":        30,
            },
        },
    }
