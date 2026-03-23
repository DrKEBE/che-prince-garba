# run.py
import sys
from pathlib import Path

# Ajouter le répertoire courant au sys.path
sys.path.insert(0, str(Path(__file__).parent))

from backend.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)