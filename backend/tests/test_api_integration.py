import os
import sys
import io
import pytest
import numpy as np
import cv2
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def create_dummy_png(color=(120, 150, 100), size=(256, 256)):
    """Creates an in-memory PNG byte stream representing a satellite terrain tile."""
    img = np.full((size[0], size[1], 3), color, dtype=np.uint8)
    # Add a mock river feature (blue stripe)
    img[100:130, :, :] = [180, 50, 20]
    success, encoded = cv2.imencode(".png", img)
    assert success
    return io.BytesIO(encoded.tobytes())

# ── 1. Service Health & Handshake Tests ──────────────────────────────────────────
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ReliefPlan AI Backend" in data["service"]

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_models_compare_endpoint():
    response = client.get("/api/models/compare")
    assert response.status_code == 200
    data = response.json()
    assert "unet" in data
    assert "deeplabv3" in data

def test_dataset_images_endpoint():
    response = client.get("/api/dataset/images")
    assert response.status_code == 200
    assert "images" in response.json()

# ── 2. Negative & Validation Input Tests ────────────────────────────────────────
def test_upload_missing_file():
    response = client.post("/api/upload")
    assert response.status_code == 422  # Validation error

def test_upload_invalid_non_image():
    dummy_text = io.BytesIO(b"This is a text file, not a satellite PNG.")
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", dummy_text, "text/plain")},
        data={"model": "deeplabv3"}
    )
    assert response.status_code in (400, 500)

def test_upload_empty_file():
    empty_file = io.BytesIO(b"")
    response = client.post(
        "/api/upload",
        files={"file": ("empty.png", empty_file, "image/png")},
        data={"model": "deeplabv3"}
    )
    assert response.status_code in (400, 500)

# ── 3. Pipeline Integrity & Model Execution Tests ──────────────────────────────
def test_pipeline_deeplabv3_synthesis():
    png_stream = create_dummy_png()
    response = client.post(
        "/api/upload",
        files={"file": ("satellite_tile.png", png_stream, "image/png")},
        data={"model": "deeplabv3"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert "blueprint_url" in data
    assert "segmentation_url" in data
    assert "results" in data

    res = data["results"]
    assert res["total_shelters"] > 0
    assert res["estimated_capacity"] > 0
    assert "unhcr_compliance" in res
    assert "water_points" in res
    assert "latrine_blocks" in res

def test_pipeline_unet_synthesis():
    png_stream = create_dummy_png()
    response = client.post(
        "/api/upload",
        files={"file": ("satellite_tile_unet.png", png_stream, "image/png")},
        data={"model": "unet"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["results"]["total_shelters"] > 0
    assert "unet" in data["message"].lower()

# ── 4. Spatial Constraints & Determinism Tests ──────────────────────────────────
def test_unhcr_spatial_metrics_consistency():
    png_stream = create_dummy_png()
    response = client.post(
        "/api/upload",
        files={"file": ("satellite_check.png", png_stream, "image/png")},
        data={"model": "deeplabv3"}
    )
    assert response.status_code == 200
    metrics = response.json()["results"]
    # Ratio check: each shelter pod houses ~5 people
    assert metrics["estimated_capacity"] == metrics["total_shelters"] * 5
    # Max walking distance should be <= 50m to water points
    assert metrics["avg_walking_distance_m"] <= 50.0

def test_determinism_same_image_reproducibility():
    img_bytes = create_dummy_png().getvalue()
    
    r1 = client.post(
        "/api/upload",
        files={"file": ("seed.png", io.BytesIO(img_bytes), "image/png")},
        data={"model": "deeplabv3"}
    ).json()["results"]

    r2 = client.post(
        "/api/upload",
        files={"file": ("seed.png", io.BytesIO(img_bytes), "image/png")},
        data={"model": "deeplabv3"}
    ).json()["results"]

    assert r1["total_shelters"] == r2["total_shelters"]
    assert r1["estimated_capacity"] == r2["estimated_capacity"]
    assert r1["buildable_area_pixels"] == r2["buildable_area_pixels"]

def test_static_asset_serving():
    png_stream = create_dummy_png()
    response = client.post(
        "/api/upload",
        files={"file": ("satellite_asset.png", png_stream, "image/png")},
        data={"model": "deeplabv3"}
    )
    data = response.json()
    blueprint_path = data["blueprint_url"].replace("http://localhost:8000", "")
    asset_resp = client.get(blueprint_path)
    assert asset_resp.status_code == 200
    assert asset_resp.headers["content-type"] == "image/png"
