from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict
import os
import uuid
from app.core.extractor import extract_audio, jobs
from app.api.models import AudioExtractionResponse, JobStatusResponse

router = APIRouter()

@router.post("/api/v1/extract-audio", response_model=AudioExtractionResponse)
async def extract_audio_endpoint(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    # Validate file format
    if not file.filename.endswith(('.mp4', '.mkv', '.webm', '.avi')):
        raise HTTPException(status_code=400, detail="Invalid video format")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Create temp directory if it doesn't exist
    os.makedirs("temp", exist_ok=True)
    
    # Save the uploaded file temporarily
    temp_path = f"temp/{job_id}_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    # Initialize job
    jobs[job_id] = {
        "status": "processing",
        "file_path": temp_path,
        "filename": file.filename
    }
    
    # Add background task
    background_tasks.add_task(extract_audio, temp_path, job_id)
    
    return {"job_id": job_id}

@router.get("/api/v1/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"job_id": job_id, "status": jobs[job_id]["status"]}

@router.get("/api/v1/download/{job_id}")
async def download_audio(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    if "output_path" not in job or not os.path.exists(job["output_path"]):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Get original filename without extension
    original_name = os.path.splitext(job["filename"])[0]
    output_filename = f"{original_name}_{job_id}.mp3"
    
    return FileResponse(
        job["output_path"],
        media_type="audio/mpeg",
        filename=output_filename
    )