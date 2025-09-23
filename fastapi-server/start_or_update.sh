#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

echo "=== [1/4] Checking for Python 3 and pip... ==="
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "=== [2/4] Creating/updating virtual environment... ==="
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo "=== [3/4] Upgrading pip and installing/updating requirements... ==="
pip install --upgrade pip
pip install --upgrade -r requirements.txt

echo "=== [4/4] Starting FastAPI server... ==="
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug