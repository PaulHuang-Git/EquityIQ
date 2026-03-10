from crewai import Agent, Task, LLM

from backend.config.settings import settings

llm = LLM(
    model=f"ollama/{settings.ollama_model}",
    base_url=settings.ollama_base_url,
)

financial_analysis_agent = Agent(
    role="CFA-Level Financial Analyst",
    goal="Compute comprehensive financial KPIs and provide investment-grade analysis for {ticker}",
    backstory=(
        "You are a CFA charterholder with 15 years of experience in fundamental "
        "analysis. You excel at computing financial ratios, identifying trends, "
        "and providing institutional-quality investment insights."
    ),
    tools=[],
    llm=llm,
    verbose=True,
)

FINANCIAL_ANALYSIS_TASK_DESCRIPTION = """
You are analyzing stock ticker {ticker}.

Here is the raw financial data collected from Yahoo Finance:
{raw_financial_data}

Compute ALL of the following KPIs using the data above:

PROFITABILITY:
- Gross Margin = Gross Profit / Total Revenue
- Operating Margin = Operating Income / Total Revenue
- Net Profit Margin = Net Income / Total Revenue
- ROE = Net Income / Total Stockholders Equity
- ROA = Net Income / Total Assets

VALUATION (use values from company_info where available):
- P/E Ratio (trailingPE from info)
- P/B Ratio (priceToBook from info)
- EV/EBITDA (enterpriseToEbitda from info)

GROWTH (Year-over-Year, using most recent 2 years):
- Revenue Growth YoY = (Year1 - Year0) / abs(Year0)
- EPS Growth YoY = same formula using diluted EPS

LEVERAGE:
- Debt-to-Equity = Total Debt / Total Stockholders Equity
- Interest Coverage = EBIT / Interest Expense

LIQUIDITY:
- Current Ratio = Current Assets / Current Liabilities
- Quick Ratio = (Current Assets - Inventory) / Current Liabilities

CASH FLOW:
- Free Cash Flow = Operating Cash Flow - Capital Expenditure
- FCF Margin = Free Cash Flow / Total Revenue

MARKET:
- Beta (from info, key: beta)
- Dividend Yield (from info, key: dividendYield)

Return ONLY a valid JSON object with this exact structure:
{{
  "ticker": "{ticker}",
  "analysis_date": "today",
  "kpis": {{
    "profitability": {{
      "gross_margin": <float or null>,
      "operating_margin": <float or null>,
      "net_margin": <float or null>,
      "roe": <float or null>,
      "roa": <float or null>
    }},
    "valuation": {{
      "pe_ratio": <float or null>,
      "pb_ratio": <float or null>,
      "ev_ebitda": <float or null>
    }},
    "growth": {{
      "revenue_growth_yoy": <float or null>,
      "eps_growth_yoy": <float or null>
    }},
    "leverage": {{
      "debt_to_equity": <float or null>,
      "interest_coverage": <float or null>
    }},
    "liquidity": {{
      "current_ratio": <float or null>,
      "quick_ratio": <float or null>
    }},
    "cash_flow": {{
      "free_cash_flow": <float or null>,
      "fcf_margin": <float or null>
    }},
    "market": {{
      "beta": <float or null>,
      "dividend_yield": <float or null>
    }}
  }},
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "overall_financial_score": <float 1-10>,
  "analyst_commentary": "..."
}}
"""

financial_analysis_task = Task(
    description=FINANCIAL_ANALYSIS_TASK_DESCRIPTION,
    agent=financial_analysis_agent,
    expected_output="Valid JSON string with complete KPI analysis for {ticker}",
)
