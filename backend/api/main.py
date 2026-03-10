import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.analysis import router as analysis_router
from backend.api.routes.reports import router as reports_router
from backend.api.ws_manager import get_progress, manager
from backend.cache.redis_manager import cache_manager
from backend.config.settings import settings
from backend.database.db_manager import init_db

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    cache_manager.enable_llm_cache()
    logger.info("Application started")
    yield
    # Shutdown
    logger.info("Application shutting down")


app = FastAPI(
    title="Multi-Agent Financial Analyzer",
    version="1.0.0",
    description="AI-powered financial analysis using LangGraph + CrewAI",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/api/v1/health")
async def health_check():
    # Check Redis
    redis_ok = False
    try:
        from backend.cache.redis_manager import cache_manager as cm
        if cm._redis_client:
            cm._redis_client.ping()
            redis_ok = True
    except Exception:
        pass

    # Check Ollama
    ollama_ok = False
    try:
        import httpx
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{settings.ollama_base_url}/api/tags")
            ollama_ok = r.status_code == 200
    except Exception:
        pass

    return {
        "status": "ok",
        "redis": "ok" if redis_ok else "unavailable",
        "ollama": "ok" if ollama_ok else "unavailable",
    }


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(job_id, websocket)
    last_step = None
    try:
        while True:
            progress = get_progress(job_id)
            if progress:
                current_step = progress.get("step")
                if current_step != last_step:
                    await websocket.send_json(progress)
                    last_step = current_step
                    if current_step in ("completed", "failed"):
                        break
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(job_id, websocket)
