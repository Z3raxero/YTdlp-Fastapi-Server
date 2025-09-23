from fastapi import APIRouter, HTTPException, BackgroundTasks, Body
from fastapi.responses import FileResponse
from typing import Dict
import os
import uuid
from app.core.extractor import extract_audio_from_url, jobs
from app.api.models import AudioExtractionRequest, AudioExtractionResponse, JobStatusResponse

router = APIRouter()

@router.post("/extract-audio", response_model=AudioExtractionResponse)
async def extract_audio_endpoint(
    request: AudioExtractionRequest,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    # Validate URL format (basic check)
    if not request.url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job
    jobs[job_id] = {
        "status": "processing",
        "url": request.url,
        "format": request.format
    }
    
    # Add background task
    background_tasks.add_task(extract_audio_from_url, request.url, job_id, request.format)
    
    return {"job_id": job_id}

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"job_id": job_id, "status": jobs[job_id]["status"]}

@router.get("/download/{job_id}")
async def download_audio(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    if "output_path" not in job or not os.path.exists(job["output_path"]):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Get original filename without extension
    original_name = job.get("filename", "audio")
    output_filename = f"{original_name}_{job_id}.{job['format']}"
    
    return FileResponse(
        job["output_path"],
        media_type=f"audio/{job['format']}",
        filename=output_filename
    )