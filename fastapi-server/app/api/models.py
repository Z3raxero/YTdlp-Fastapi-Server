from pydantic import BaseModel
from typing import Optional

class VideoUploadRequest(BaseModel):
    video_url: str

class AudioExtractionResponse(BaseModel):
    job_id: str
    message: str

class ExtractionStatusResponse(BaseModel):
    job_id: str
    progress: Optional[int] = None
    status: str

class AudioDownloadResponse(BaseModel):
    file_url: str
    message: str