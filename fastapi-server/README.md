# Video Audio Extractor

## Overview
The Video Audio Extractor is a FastAPI application designed to extract audio from video files. It utilizes the yt-dlp library for audio extraction and provides a simple API for communication with a browser extension.

## Project Structure
```
fastapi-server/
├── app/
│   ├── main.py              # Entry point of the FastAPI application
│   ├── api/
│   │   ├── endpoints.py     # API endpoints for audio extraction
│   │   └── models.py        # Pydantic models for request/response schemas
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   └── extractor.py     # Audio extraction logic using yt-dlp
│   └── utils/
│       └── file_handler.py  # Utility functions for file operations
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Setup Instructions
1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd fastapi-server
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the FastAPI server:**
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## Usage
- The FastAPI server exposes the following endpoints:
  - `POST /api/v1/extract-audio`: Upload a video file to extract audio.
  - `GET /api/v1/status/{job_id}`: Check the status of the audio extraction.
  - `GET /api/v1/download/{job_id}`: Download the extracted audio file.

## Browser Extension
The browser extension communicates with this FastAPI server to facilitate audio extraction from videos detected on web pages. Ensure that the extension is configured to point to the correct server URL.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.