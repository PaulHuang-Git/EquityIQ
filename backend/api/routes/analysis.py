import asyncio
import logging
from typing import List

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from backend.api.ws_manager import set_progress
from backend.config.settings import settings
from backend.database import db_manager

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request/Response models ───────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    ticker: str


class AnalyzeResponse(BaseModel):
    job_id: str
    status: str
    ticker: str


class BatchAnalyzeResponse(BaseModel):
    job_ids: List[str]
    tickers: List[str]


# ── Background task ───────────────────────────────────────────────────────────

async def run_analysis(job_id: str, ticker: str) -> None:
    """Run the full LangGraph analysis pipeline in a thread executor."""
    from backend.workflow.graph import graph

    await db_manager.update_job_status(job_id, "running")
    set_progress(job_id, "data_collection", 5, f"Starting analysis for {ticker}…")

    try:
        initial_state = {
            "ticker": ticker.upper(),
            "job_id": job_id,
            "raw_financial_data": None,
            "raw_esg_data": None,
            "financial_analysis": None,
            "esg_analysis": None,
            "report_markdown": None,
            "report_path": None,
            "status": "pending",
            "error": None,
            "messages": [],
        }

        loop = asyncio.get_event_loop()
        final_state = await loop.run_in_executor(
            None, graph.invoke, initial_state
        )

        if final_state.get("error") or final_state.get("status") == "failed":
            error_msg = final_state.get("error", "Unknown error")
            await db_manager.update_job_status(job_id, "failed", error_msg)
            set_progress(job_id, "failed", 0, f"Failed: {error_msg}")
            return

        # Persist analysis results
        if final_state.get("financial_analysis"):
            await db_manager.save_analysis_result(
                ticker, job_id, "financial", final_state["financial_analysis"]
            )
        if final_state.get("esg_analysis"):
            await db_manager.save_analysis_result(
                ticker, job_id, "esg", final_state["esg_analysis"]
            )

        # Persist report
        report_markdown = final_state.get("report_markdown", "")
        report_path = final_state.get("report_path", f"reports/{ticker}_{job_id}.md")

        if report_markdown:
            try:
                await db_manager.save_report(ticker, job_id, report_path, report_markdown)
                logger.info(f"Report persisted to DB for {ticker}")
            except Exception as e:
                logger.error(f"Could not persist report to DB: {e}", exc_info=True)  # warning → error
        else:
            logger.warning(f"No report_markdown in final_state for {ticker}, report not saved to DB")



    except Exception as e:
        logger.error(f"run_analysis failed [{ticker}/{job_id}]: {e}", exc_info=True)
        await db_manager.update_job_status(job_id, "failed", str(e))
        set_progress(job_id, "failed", 0, f"Failed: {e}")


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/analyze", response_model=AnalyzeResponse)
async def start_analysis(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    ticker = request.ticker.upper().strip()
    if not ticker:
        raise HTTPException(status_code=400, detail="ticker is required")

    job_id = await db_manager.create_job(ticker)
    background_tasks.add_task(run_analysis, job_id, ticker)
    return AnalyzeResponse(job_id=job_id, status="pending", ticker=ticker)


@router.post("/analyze/batch", response_model=BatchAnalyzeResponse)
async def batch_analysis(background_tasks: BackgroundTasks):
    tickers = settings.default_tickers
    job_ids = []
    for ticker in tickers:
        job_id = await db_manager.create_job(ticker)
        background_tasks.add_task(run_analysis, job_id, ticker)
        job_ids.append(job_id)
    return BatchAnalyzeResponse(job_ids=job_ids, tickers=tickers)


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = await db_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/cache/{ticker}")
async def clear_cache(ticker: str):
    from backend.cache.redis_manager import cache_manager
    cache_manager.invalidate_ticker(ticker)
    return {"cleared": True, "ticker": ticker.upper()}
