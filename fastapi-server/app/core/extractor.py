import os
import subprocess
import logging
import yt_dlp
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory job storage (shared with endpoints)
jobs = {}

def extract_audio_from_url(url: str, job_id: str, format: str = "mp3"):
    """Download video from URL and extract audio using yt-dlp and ffmpeg"""
    try:
        logger.info(f"Starting audio extraction for job {job_id} from URL: {url}")
        
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        # Define output path
        output_path = f"output/{job_id}.{format}"
        
        # Update job status
        jobs[job_id]["status"] = "downloading"
        
        # yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"temp/{job_id}.%(ext)s",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format,
                'preferredquality': '192',
            }],
            'keepvideo': False,
        }
        
        # Download and extract audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # The actual output file after post-processing
            actual_output = f"temp/{job_id}.{format}"
            # Move to output directory
            os.rename(actual_output, output_path)
            
            # Get the video title for the filename
            video_title = info.get('title', 'audio')
            jobs[job_id]["filename"] = video_title
            jobs[job_id]["output_path"] = output_path
        
        # Update job status
        jobs[job_id]["status"] = "completed"
        logger.info(f"Audio extraction completed for job {job_id}")
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg)
        jobs[job_id]["status"] = f"failed: {error_msg}"
    finally:
        # Clean up any temporary files
        temp_file = f"temp/{job_id}."
        for ext in ['mp4', 'webm', 'mkv', format]:
            if os.path.exists(temp_file + ext):
                os.remove(temp_file + ext)
                logger.info(f"Cleaned up temporary file: {temp_file + ext}")