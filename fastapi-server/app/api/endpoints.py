from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import Dict
import os
from app.core.extractor import extract_audio
from app.api.models import AudioExtractionResponse, JobStatusResponse

router = APIRouter()

# In-memory job storage for simplicity
jobs = {}

@router.post("/api/v1/extract-audio", response_model=AudioExtractionResponse)
async def extract_audio_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(('.mp4', '.mkv', '.webm', '.avi')):
        raise HTTPException(status_code=400, detail="Invalid video format")
    
    job_id = len(jobs) + 1  # Simple job ID generation
    jobs[job_id] = {"status": "processing", "file_path": f"temp/{file.filename}"}
    
    # Save the uploaded file temporarily
    with open(jobs[job_id]["file_path"], "wb") as f:
        f.write(await file.read())
    
    # Extract audio in a background task
    extract_audio(jobs[job_id]["file_path"], job_id)
    
    return {"job_id": job_id}

@router.get("/api/v1/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: int):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"job_id": job_id, "status": jobs[job_id]["status"]}

@router.get("/api/v1/download/{job_id}")
async def download_audio(job_id: int):
    if job_id not in jobs or jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=404, detail="Job not found or not completed")
    
    audio_file_path = f"output/{job_id}.mp3"  # Assuming output file naming convention
    if not os.path.exists(audio_file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(audio_file_path, media_type="audio/mpeg", filename=f"audio_{job_id}.mp3")