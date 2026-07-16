from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time

app = FastAPI(title="ReliefPlan AI Backend", description="API for automated disaster relief camp planning.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the ReliefPlan AI API"}

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    # Mock behavior for image upload and processing
    job_id = str(uuid.uuid4())
    # In a real scenario, this would save the image and trigger the ML pipeline asynchronously
    
    return JSONResponse(status_code=202, content={
        "message": "Image uploaded successfully, processing started.",
        "job_id": job_id,
        "filename": file.filename
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
