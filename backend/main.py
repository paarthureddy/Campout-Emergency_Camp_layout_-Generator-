import os
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uuid

# Import pipeline modules
from pipeline.segmentation import segment_terrain
from pipeline.analysis import analyze_terrain
from pipeline.optimization import generate_layout
from pipeline.renderer import render_blueprint

app = FastAPI(title="ReliefPlan AI Backend", description="API for automated disaster relief camp planning.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static directory for returning generated blueprints
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to the ReliefPlan AI API"}

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    
    # Read image from request
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    original_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 1. Segmentation
    segmented_mask = segment_terrain(original_image)
    
    # 2. Analysis
    terrain_analysis = analyze_terrain(segmented_mask)
    
    # 3. Optimization
    layout = generate_layout(terrain_analysis)
    
    # 4. Renderer
    blueprint = render_blueprint(original_image, layout)
    
    # Save blueprint to static directory
    blueprint_filename = f"{job_id}.png"
    blueprint_path = os.path.join(STATIC_DIR, blueprint_filename)
    cv2.imwrite(blueprint_path, blueprint)
    
    return JSONResponse(status_code=200, content={
        "message": "Pipeline completed successfully.",
        "job_id": job_id,
        "blueprint_url": f"http://localhost:8000/static/{blueprint_filename}",
        "results": layout["metrics"]
    })

@app.get("/api/status/{job_id}")
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
