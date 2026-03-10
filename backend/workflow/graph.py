import json
import logging
import re
from typing import Any, Dict

from crewai import Crew, Process, Task
from langgraph.graph import END, START, StateGraph

from backend.workflow.state import FinancialAnalysisState

logger = logging.getLogger(__name__)


# ── Utility ──────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> Dict[str, Any]:
    """Robustly extract a JSON object from LLM output."""
    if not text:
        return {}
    text = text.strip()

    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Markdown code block
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Outermost JSON object
    match = re.search(r"(\{[\s\S]+\})", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    logger.warning("Could not parse JSON from LLM output; storing raw text.")
    return {"raw_output": text}


def _kickoff(agent, task_description: str, expected_output: str, inputs: dict) -> str:
    """Create a single-agent crew, kickoff, and return raw string output."""
    task = Task(
        description=task_description,
        agent=agent,
        expected_output=expected_output,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    result = crew.kickoff(inputs=inputs)
    return result.raw if hasattr(result, "raw") else str(result)


def _set_progress(job_id: str, step: str, progress: int, message: str):
    """Update in-memory progress store (thread-safe via CPython GIL)."""
    try:
        from backend.api.ws_manager import set_progress
        set_progress(job_id, step, progress, message)
    except Exception:
        pass  # WS manager may not be initialised in standalone runs


# ── Node functions ────────────────────────────────────────────────────────────

def data_collection_node(state: FinancialAnalysisState) -> dict:
    from backend.agents.data_collection_agent import (
        DATA_COLLECTION_TASK_DESCRIPTION,
        data_collection_agent,
    )

    ticker = state["ticker"]
    job_id = state["job_id"]
    _set_progress(job_id, "data_collection", 10, f"Collecting data for {ticker}…")

    try:
        raw = _kickoff(
            data_collection_agent,
            DATA_COLLECTION_TASK_DESCRIPTION,
            "Complete JSON with all financial and ESG raw data",
            {"ticker": ticker},
        )
        parsed = _extract_json(raw)

        return {
            "raw_financial_data": parsed,
            "raw_esg_data": parsed.get("esg_data", {}),
            "status": "financial_analysis",
            "messages": state.get("messages", []) + [f"Data collected for {ticker}"],
        }
    except Exception as e:
        logger.error(f"data_collection_node failed: {e}")
        return {
            "error": str(e),
            "status": "failed",
            "messages": state.get("messages", []) + [f"Data collection failed: {e}"],
        }


def financial_analysis_node(state: FinancialAnalysisState) -> dict:
    from backend.agents.financial_analysis_agent import (
        FINANCIAL_ANALYSIS_TASK_DESCRIPTION,
        financial_analysis_agent,
    )

    ticker = state["ticker"]
    job_id = state["job_id"]
    _set_progress(job_id, "financial_analysis", 35, f"Computing KPIs for {ticker}…")

    raw_data = state.get("raw_financial_data") or {}
    # Limit payload size to avoid overflowing context window
    raw_data_str = json.dumps(raw_data, default=str)[:12_000]

    try:
        raw = _kickoff(
            financial_analysis_agent,
            FINANCIAL_ANALYSIS_TASK_DESCRIPTION,
            "Valid JSON string with complete KPI analysis",
            {"ticker": ticker, "raw_financial_data": raw_data_str},
        )
        analysis = _extract_json(raw)

        return {
            "financial_analysis": analysis,
            "status": "esg_scoring",
            "messages": state.get("messages", []) + [f"Financial analysis complete for {ticker}"],
        }
    except Exception as e:
        logger.error(f"financial_analysis_node failed: {e}")
        return {
            "error": str(e),
            "status": "failed",
            "messages": state.get("messages", []) + [f"Financial analysis failed: {e}"],
        }


def esg_scoring_node(state: FinancialAnalysisState) -> dict:
    from backend.agents.esg_scoring_agent import (
        ESG_SCORING_TASK_DESCRIPTION,
        esg_scoring_agent,
    )

    ticker = state["ticker"]
    job_id = state["job_id"]
    _set_progress(job_id, "esg_scoring", 60, f"Assessing ESG risk for {ticker}…")

    raw_esg = state.get("raw_esg_data") or {}
    raw_esg_str = json.dumps(raw_esg, default=str)[:4_000]

    try:
        raw = _kickoff(
            esg_scoring_agent,
            ESG_SCORING_TASK_DESCRIPTION,
            "Valid JSON string with complete ESG analysis",
            {"ticker": ticker, "raw_esg_data": raw_esg_str},
        )
        analysis = _extract_json(raw)

        return {
            "esg_analysis": analysis,
            "status": "report_generation",
            "messages": state.get("messages", []) + [f"ESG analysis complete for {ticker}"],
        }
    except Exception as e:
        logger.error(f"esg_scoring_node failed: {e}")
        return {
            "error": str(e),
            "status": "failed",
            "messages": state.get("messages", []) + [f"ESG scoring failed: {e}"],
        }


def report_generation_node(state: FinancialAnalysisState) -> dict:
    from backend.agents.report_generation_agent import (
        REPORT_GENERATION_TASK_DESCRIPTION,
        report_generation_agent,
    )

    ticker = state["ticker"]
    job_id = state["job_id"]
    _set_progress(job_id, "report_generation", 80, f"Writing investment report for {ticker}…")

    raw_data = state.get("raw_financial_data") or {}
    company_info = json.dumps(raw_data.get("company_info", {}), default=str)[:3_000]
    financial_analysis = json.dumps(state.get("financial_analysis") or {}, default=str)[:4_000]
    esg_analysis = json.dumps(state.get("esg_analysis") or {}, default=str)[:3_000]

    try:
        report_content = _kickoff(
            report_generation_agent,
            REPORT_GENERATION_TASK_DESCRIPTION,
            "The complete Markdown investment report as a string",  # ← 改這裡
            {
                "ticker": ticker,
                "job_id": job_id,
                "company_info": company_info,
                "financial_analysis": financial_analysis,
                "esg_analysis": esg_analysis,
            },
        )
        report_content = report_content.strip()

        # ── Node 自己負責存檔，不依賴 LLM ──────────────────
        from pathlib import Path
        save_dir = Path("reports")
        save_dir.mkdir(parents=True, exist_ok=True)
        report_path = str(save_dir / f"{ticker}_{job_id}.md")
        Path(report_path).write_text(report_content, encoding="utf-8")
        logger.info(f"Report saved to disk: {report_path}")
        # ────────────────────────────────────────────────────

        _set_progress(job_id, "completed", 100, f"Report ready for {ticker}")

        return {
            "report_path": report_path,
            "report_markdown": report_content,   # ← 同時存入 state
            "status": "completed",
            "messages": state.get("messages", []) + [f"Report generated: {report_path}"],
        }
    except Exception as e:
        logger.error(f"report_generation_node failed: {e}")
        return {
            "error": str(e),
            "status": "failed",
            "messages": state.get("messages", []) + [f"Report generation failed: {e}"],
        }

def error_handler_node(state: FinancialAnalysisState) -> dict:
    error = state.get("error", "Unknown error")
    job_id = state.get("job_id", "")
    ticker = state.get("ticker", "")
    logger.error(f"Pipeline error [{ticker}/{job_id}]: {error}")
    _set_progress(job_id, "failed", 0, f"Analysis failed: {error}")
    return {"status": "failed"}


# ── Conditional routing ───────────────────────────────────────────────────────

def should_continue(state: FinancialAnalysisState) -> str:
    return "error" if state.get("error") else "continue"


# ── Build graph ───────────────────────────────────────────────────────────────

builder = StateGraph(FinancialAnalysisState)

builder.add_node("data_collection", data_collection_node)
builder.add_node("financial_analysis", financial_analysis_node)
builder.add_node("esg_scoring", esg_scoring_node)
builder.add_node("report_generation", report_generation_node)
builder.add_node("error_handler", error_handler_node)

builder.add_edge(START, "data_collection")
builder.add_conditional_edges(
    "data_collection", should_continue,
    {"continue": "financial_analysis", "error": "error_handler"},
)
builder.add_conditional_edges(
    "financial_analysis", should_continue,
    {"continue": "esg_scoring", "error": "error_handler"},
)
builder.add_conditional_edges(
    "esg_scoring", should_continue,
    {"continue": "report_generation", "error": "error_handler"},
)
builder.add_edge("report_generation", END)
builder.add_edge("error_handler", END)

graph = builder.compile()
