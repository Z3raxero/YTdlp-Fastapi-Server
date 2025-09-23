#This is the bulk lifter for the FastAPI server application.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.api.endpoints import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router with prefix
app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Video Audio Extractor API"}

@app.on_event("startup")
async def startup_event():
    # Create necessary directories
    os.makedirs("temp", exist_ok=True)
    os.makedirs("output", exist_ok=True)