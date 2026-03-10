"""
Backend startup entry point.
Run from the project root:  python backend/run.py
Or from the backend dir:    python run.py
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path so 'backend.*' imports work
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import uvicorn
from backend.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )
