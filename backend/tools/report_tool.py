import logging
from datetime import datetime
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ReportInput(BaseModel):
    ticker: str = Field(description="Stock ticker symbol")
    content: str = Field(description="Full Markdown report content")
    job_id: str = Field(description="Analysis job UUID")


class ReportTool(BaseTool):
    name: str = "Report Save Tool"
    description: str = (
        "Save the completed Markdown investment report to disk. "
        "Provide ticker, full markdown content, and job_id. "
        "Returns the file path where the report was saved."
    )
    args_schema: Type[BaseModel] = ReportInput

    def _run(self, ticker: str, content: str, job_id: str) -> str:
        ticker = ticker.upper()
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        reports_dir = Path(__file__).parent.parent / "outputs" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{ticker}_{date_str}.md"
        filepath = reports_dir / filename

        try:
            filepath.write_text(content, encoding="utf-8")
            logger.info(f"Report saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save report for {ticker}: {e}")
            return f"ERROR: {e}"
