import os
import subprocess
import logging
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory job storage (shared with endpoints)
jobs = {}

def extract_audio(file_path: str, job_id: int):
    """Extract audio from video file using ffmpeg"""
    try:
        logger.info(f"Starting audio extraction for job {job_id}")
        
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        # Define output path
        output_path = f"output/{job_id}.mp3"
        
        # Run ffmpeg command to extract audio
        cmd = [
            "ffmpeg",
            "-i", file_path,
            "-vn",  # No video
            "-acodec", "mp3",
            "-ab", "192k",
            "-y",  # Overwrite output file if it exists
            output_path
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Update job status
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["output_path"] = output_path
        
        logger.info(f"Audio extraction completed for job {job_id}")
        
    except subprocess.CalledProcessError as e:
        error_msg = f"FFmpeg error: {e.stderr}"
        logger.error(error_msg)
        jobs[job_id]["status"] = f"failed: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        jobs[job_id]["status"] = f"failed: {error_msg}"
    finally:
        # Clean up input file
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up input file: {file_path}")