"""
WebSocket connection manager and in-memory progress store.
Progress updates are written from sync LangGraph nodes (via set_progress)
and read by the async WebSocket endpoint.
CPython's GIL makes simple dict reads/writes thread-safe.
"""
from typing import Dict, List

from fastapi import WebSocket

# job_id -> {"step": str, "progress": int, "message": str}
_progress_store: Dict[str, dict] = {}


def set_progress(job_id: str, step: str, progress: int, message: str) -> None:
    """Called from sync workflow nodes to broadcast progress."""
    _progress_store[job_id] = {
        "step": step,
        "progress": progress,
        "message": message,
    }


def get_progress(job_id: str) -> dict | None:
    return _progress_store.get(job_id)


class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, List[WebSocket]] = {}

    async def connect(self, job_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.setdefault(job_id, []).append(websocket)

    def disconnect(self, job_id: str, websocket: WebSocket) -> None:
        connections = self.active.get(job_id, [])
        try:
            connections.remove(websocket)
        except ValueError:
            pass


manager = ConnectionManager()
