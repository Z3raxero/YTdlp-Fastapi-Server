from pydantic import BaseModel

class AudioExtractionResponse(BaseModel):
    job_id: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str