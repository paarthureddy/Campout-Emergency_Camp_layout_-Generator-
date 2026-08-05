import os
import cv2
import numpy as np
import logging
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uuid
from pydantic import BaseModel
from typing import Dict, Any, List

class UploadResponse(BaseModel):
    message: str
    job_id: str
    blueprint_url: str
    results: Dict[str, Any]

class StatusResponse(BaseModel):
    job_id: str
    status: str
    results: Dict[str, Any]

# Import pipeline modules
from pipeline.segmentation import segment_terrain
from pipeline.analysis import analyze_terrain
from pipeline.optimization import generate_layout
from pipeline.renderer import render_blueprint

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="ReliefPlan AI Backend", description="API for automated disaster relief camp planning.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from config import STATIC_DIR, DATA_DIR

# Serve static directory for returning generated blueprints
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mount data directory for developer dataset visualization
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

import subprocess

@app.get("/api/dataset/images")
def get_dataset_images():
    train_images_dir = os.path.join(DATA_DIR, "Train_256", "images")
    if not os.path.exists(train_images_dir):
        return {"images": []}
    files = sorted([f for f in os.listdir(train_images_dir) if f.endswith('.png')])
    # Return max 50 images for performance
    return {"images": files[:50]}

@app.get("/api/models/compare")
def get_model_comparison():
    # Return paths to learning curve artifacts
    return {
        "unet": "http://localhost:8000/static/learning_curves_unet.png",
        "deeplabv3": "http://localhost:8000/static/learning_curves_deeplabv3.png"
    }

@app.post("/api/train")
def trigger_training(model: str = "unet"):
    # Run in background via subprocess
    cmd = f"python train.py --epochs 2 --model {model} --fast_demo"
    subprocess.Popen(cmd, shell=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    return {"message": f"Training started for {model}", "status": "running"}

@app.get("/")
def read_root():
    return {"message": "Welcome to the ReliefPlan AI API"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ReliefPlan AI Backend"}

from fastapi import FastAPI, UploadFile, File, Form, HTTPException

@app.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...), model: str = Form("unet")):
    job_id = str(uuid.uuid4())
    logger.info(f"Started upload processing with model: {model}, Job ID: {job_id}")
    
    try:
        # Read image from request
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        original_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if original_image is None:
            raise ValueError("Invalid image format.")
        
        # 1. Segmentation (Now passing the chosen model)
        segmented_mask = segment_terrain(original_image, model_name=model)
        
        # 2. Analysis
        terrain_analysis = analyze_terrain(segmented_mask)
        
        # 3. Optimization
        layout = generate_layout(terrain_analysis)
        
        # 4. Renderer
        blueprint = render_blueprint(original_image, layout, segmented_mask)
        
        # Save blueprint to static directory
        blueprint_filename = f"{job_id}.png"
        blueprint_path = os.path.join(STATIC_DIR, blueprint_filename)
        cv2.imwrite(blueprint_path, blueprint)
        
        return JSONResponse(status_code=200, content={
            "message": f"Pipeline completed using {model} model.",
            "job_id": job_id,
            "blueprint_url": f"http://localhost:8000/static/{blueprint_filename}",
            "results": layout["metrics"]
        })
    except Exception as e:
        logger.error(f"Image processing failed for Job ID: {job_id}. Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    # Mock status endpoint
    # Simulating a pipeline that finishes immediately for demo purposes
    return {
        "job_id": job_id,
        "status": "completed",
        "results": {
            "land_utilization_percent": 85,
            "total_shelters": 450,
            "avg_walking_distance_m": 42,
            "facilities": {
                "medical_centers": 2,
                "water_points": 15,
                "latrines": 30
            }
        }
    }
