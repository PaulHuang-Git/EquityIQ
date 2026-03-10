from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from pathlib import Path
from datetime import datetime
import uuid
import logging

from backend.database.models import Base, AnalysisJob, AnalysisResult, Report
from backend.config.settings import settings

logger = logging.getLogger(__name__)

# Ensure database directory exists
_db_path = Path(settings.sqlite_db_path)
_db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(
    f"sqlite+aiosqlite:///{settings.sqlite_db_path}",
    echo=False,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


async def create_job(ticker: str) -> str:
    job_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        job = AnalysisJob(id=job_id, ticker=ticker.upper(), status="pending")
        session.add(job)
        await session.commit()
    return job_id


async def update_job_status(job_id: str, status: str, error_message: str = None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AnalysisJob).where(AnalysisJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        if job:
            job.status = status
            if error_message:
                job.error_message = error_message
            if status in ("completed", "failed"):
                job.completed_at = datetime.utcnow()
            await session.commit()


async def get_job(job_id: str) -> dict | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AnalysisJob).where(AnalysisJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return None
        return {
            "job_id": job.id,
            "ticker": job.ticker,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
        }


async def save_analysis_result(
    ticker: str, job_id: str, analysis_type: str, result: dict
):
    async with AsyncSessionLocal() as session:
        ar = AnalysisResult(
            ticker=ticker.upper(),
            job_id=job_id,
            analysis_type=analysis_type,
            result=result,
        )
        session.add(ar)
        await session.commit()


async def save_report(
    ticker: str, job_id: str, report_path: str, report_content: str
):
    async with AsyncSessionLocal() as session:
        report = Report(
            ticker=ticker.upper(),
            job_id=job_id,
            report_path=report_path,
            report_content=report_content,
        )
        session.add(report)
        await session.commit()


async def get_all_reports() -> list:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Report).order_by(Report.created_at.desc())
        )
        reports = result.scalars().all()
        return [
            {
                "id": r.id,
                "ticker": r.ticker,
                "job_id": r.job_id,
                "report_path": r.report_path,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reports
        ]


async def get_reports_by_ticker(ticker: str) -> list:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Report)
            .where(Report.ticker == ticker.upper())
            .order_by(Report.created_at.desc())
        )
        reports = result.scalars().all()
        return [
            {
                "id": r.id,
                "ticker": r.ticker,
                "job_id": r.job_id,
                "report_path": r.report_path,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reports
        ]


async def get_latest_report(ticker: str) -> dict | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Report)
            .where(Report.ticker == ticker.upper())
            .order_by(Report.created_at.desc())
            .limit(1)
        )
        report = result.scalar_one_or_none()
        if not report:
            return None
        return {
            "id": report.id,
            "ticker": report.ticker,
            "job_id": report.job_id,
            "report_path": report.report_path,
            "report_content": report.report_content,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }
