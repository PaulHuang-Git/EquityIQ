from crewai import Agent, Task, LLM

from backend.config.settings import settings
from backend.tools.report_tool import ReportTool

llm = LLM(
    model=f"ollama/{settings.ollama_model}",
    base_url=settings.ollama_base_url,
)

report_generation_agent = Agent(
    role="Senior Investment Report Writer",
    goal="Synthesize all analysis into a professional Markdown investment report for {ticker}",
    backstory=(
        "You are an expert financial writer with experience producing "
        "institutional-grade investment research reports. You combine "
        "quantitative data with qualitative insights to create clear, "
        "actionable investment reports."
    ),
    #tools=[ReportTool()],
    tools=[],
    llm=llm,
    verbose=True,
)

REPORT_GENERATION_TASK_DESCRIPTION = """
Generate a comprehensive Markdown investment report for {ticker}.

COMPANY INFO:
{company_info}

FINANCIAL ANALYSIS:
{financial_analysis}

ESG ANALYSIS:
{esg_analysis}

JOB ID: {job_id}

Write the full report following this exact Markdown structure:

# Investment Analysis Report: {ticker} — [COMPANY NAME FROM INFO]

> **Generated**: [TODAY'S DATE] | **Model**: qwen3.5:35b-a3b | **System**: Multi-Agent Financial Analyzer

---

## Executive Summary

[3 paragraphs: company overview, financial performance highlights, ESG sustainability rating]

## Company Overview

| Item | Details |
|------|---------|
| Sector | ... |
| Industry | ... |
| Market Cap | ... |
| Employees | ... |
| Website | ... |

## Financial Performance Analysis

### Key Financial KPIs

| Category | Metric | Value | Notes |
|----------|--------|-------|-------|
| Profitability | Gross Margin | X.X% | ... |
| Profitability | Operating Margin | X.X% | ... |
| Profitability | Net Margin | X.X% | ... |
| Profitability | ROE | X.X% | ... |
| Profitability | ROA | X.X% | ... |
| Valuation | P/E Ratio | X.X | ... |
| Valuation | P/B Ratio | X.X | ... |
| Valuation | EV/EBITDA | X.X | ... |
| Growth | Revenue Growth YoY | X.X% | ... |
| Growth | EPS Growth YoY | X.X% | ... |
| Leverage | Debt-to-Equity | X.X | ... |
| Leverage | Interest Coverage | X.X | ... |
| Liquidity | Current Ratio | X.X | ... |
| Liquidity | Quick Ratio | X.X | ... |
| Cash Flow | Free Cash Flow | $X.XB | ... |
| Cash Flow | FCF Margin | X.X% | ... |
| Market | Beta | X.X | ... |
| Market | Dividend Yield | X.X% | ... |

### Profitability Analysis

[Narrative analysis of profitability metrics and trends]

### Valuation Analysis

[Narrative on whether the stock appears over/under/fairly valued]

### Balance Sheet Health

[Analysis of leverage, liquidity, and financial stability]

### Cash Flow Analysis

[Analysis of FCF generation and quality of earnings]

## ESG Risk Assessment

### ESG Scores Overview

| Metric | Score | Risk Level |
|--------|-------|-----------|
| Total ESG Risk | ... | ... |
| Environmental | ... | ... |
| Social | ... | ... |
| Governance | ... | ... |
| Controversy Level | .../5 | ... |

### Environmental Risk

[Analysis of environmental risk exposure and management]

### Social Risk

[Analysis of social risk factors]

### Governance Risk

[Analysis of governance structure and quality]

### Key ESG Risks

[Bullet points of top ESG risks]

## Investment Considerations

### Strengths

[Bullet points from financial analysis strengths]

### Risks & Weaknesses

[Bullet points from financial analysis weaknesses + ESG risks]

## Analyst Verdict

**Overall Score**: X.X / 10

**Assessment**: [Underweight / Neutral / Overweight]

[2-3 sentence justification of the verdict]

---

*Disclaimer: AI-generated report for informational purposes only. Not investment advice.*

Return ONLY the complete Markdown report. No extra text, no file paths, no tool calls.
"""

report_generation_task = Task(
    description=REPORT_GENERATION_TASK_DESCRIPTION,
    agent=report_generation_agent,
    expected_output="The complete Markdown investment report as a string", 
)
