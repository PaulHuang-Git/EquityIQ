from fastapi import APIRouter, HTTPException

from backend.database import db_manager

router = APIRouter()


@router.get("/reports")
async def list_reports():
    return await db_manager.get_all_reports()


@router.get("/reports/{ticker}")
async def get_latest_report(ticker: str):
    report = await db_manager.get_latest_report(ticker.upper())
    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"No report found for {ticker.upper()}",
        )
    return report


@router.get("/reports/{ticker}/history")
async def get_report_history(ticker: str):
    reports = await db_manager.get_reports_by_ticker(ticker.upper())
    return reports
