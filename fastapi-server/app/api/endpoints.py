from fastapi import APIRouter, HTTPException, BackgroundTasks, Body, Request
from fastapi.responses import FileResponse
from typing import Dict
import os
import uuid
import logging
from app.core.extractor import extract_audio_from_url, jobs
from app.api.models import AudioExtractionRequest, AudioExtractionResponse, JobStatusResponse

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/extract-audio", response_model=AudioExtractionResponse)
async def extract_audio_endpoint(
    request: Request,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    logger.info("Extract audio endpoint called")
    
    try:
        # Get raw request body
        body = await request.body()
        logger.debug(f"Raw request body: {body}")
        
        # Parse request body
        try:
            request_data = await request.json()
            logger.info(f"Parsed request data: {request_data}")
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Validate request data
        if not isinstance(request_data, dict):
            logger.error("Request data is not a dictionary")
            raise HTTPException(status_code=400, detail="Invalid request format")
        
        if 'url' not in request_data:
            logger.error("Missing 'url' field in request")
            raise HTTPException(status_code=422, detail="URL is required")
        
        url = request_data['url']
        format = request_data.get('format', 'mp3')
        
        logger.info(f"Processing URL: {url}, Format: {format}")
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            logger.error(f"Invalid URL format: {url}")
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job
        jobs[job_id] = {
            "status": "processing",
            "url": url,
            "format": format
        }
        
        logger.info(f"Created job {job_id} for URL: {url}")
        
        # Add background task
        background_tasks.add_task(extract_audio_from_url, url, job_id, format)
        
        return {"job_id": job_id}
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in extract_audio_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    logger.info(f"Status check for job {job_id}")
    
    if job_id not in jobs:
        logger.warning(f"Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"job_id": job_id, "status": jobs[job_id]["status"]}

@router.get("/download/{job_id}")
async def download_audio(job_id: str):
    logger.info(f"Download request for job {job_id}")
    
    if job_id not in jobs:
        logger.warning(f"Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        logger.warning(f"Job not completed: {job_id}, status: {job['status']}")
        raise HTTPException(status_code=400, detail="Job not completed")
    
    if "output_path" not in job or not os.path.exists(job["output_path"]):
        logger.error(f"Output file not found for job {job_id}")
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Get original filename without extension
    original_name = job.get("filename", "audio")
    output_filename = f"{original_name}_{job_id}.{job['format']}"
    
    logger.info(f"Serving file {job['output_path']} as {output_filename}")
    
    return FileResponse(
        job["output_path"],
        media_type=f"audio/{job['format']}",
        filename=output_filename
    )