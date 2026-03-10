from typing import Any, Dict, List, Optional, TypedDict


class FinancialAnalysisState(TypedDict):
    # Input
    ticker: str
    job_id: str

    # Agent 1 outputs
    raw_financial_data: Optional[Dict[str, Any]]   # company info + financials
    raw_esg_data: Optional[Dict[str, Any]]          # ESG scores

    # Agent 2 output
    financial_analysis: Optional[Dict[str, Any]]

    # Agent 3 output
    esg_analysis: Optional[Dict[str, Any]]
    report_markdown: Optional[str] 
    # Agent 4 output
    report_markdown: Optional[str]
    report_path: Optional[str]

    # Flow control
    status: str
    # pending | data_collection | financial_analysis | esg_scoring
    # | report_generation | completed | failed
    error: Optional[str]
    messages: List[str]
