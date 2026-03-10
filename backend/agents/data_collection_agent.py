from crewai import Agent, Task, LLM

from backend.config.settings import settings
from backend.tools.esg_tool import ESGTool
from backend.tools.yahoo_finance_tool import YahooFinanceTool

llm = LLM(
    model=f"ollama/{settings.ollama_model}",
    base_url=settings.ollama_base_url,
    extra_body={"think": False}
)

data_collection_agent = Agent(
    role="Senior Financial Data Analyst",
    goal="Fetch comprehensive and accurate financial and ESG data for {ticker}",
    backstory=(
        "You are an expert in financial data acquisition with deep knowledge "
        "of market data sources. You retrieve clean, structured data from "
        "Yahoo Finance for downstream analysis."
    ),
    tools=[YahooFinanceTool(), ESGTool()],
    llm=llm,
    verbose=True,
)

DATA_COLLECTION_TASK_DESCRIPTION = """
For stock ticker {ticker}, collect ALL of the following data using the available tools:

1. Company info and key statistics — use Yahoo Finance Tool with data_type="info"
2. Stock price history (1 year, daily OHLCV) — use Yahoo Finance Tool with data_type="price"
3. Income Statement (annual) — use Yahoo Finance Tool with data_type="income_stmt"
4. Balance Sheet (annual) — use Yahoo Finance Tool with data_type="balance_sheet"
5. Cash Flow Statement (annual) — use Yahoo Finance Tool with data_type="cashflow"
6. ESG Sustainability scores — use ESG Data Tool with ticker="{ticker}"

After collecting all data, combine everything into a single JSON response with this structure:
{{
  "company_info": {{...}},
  "price_history": [...],
  "income_statement": {{...}},
  "balance_sheet": {{...}},
  "cash_flow": {{...}},
  "esg_data": {{...}}
}}

Return only the JSON, no extra text.
"""

data_collection_task = Task(
    description=DATA_COLLECTION_TASK_DESCRIPTION,
    agent=data_collection_agent,
    expected_output="Complete JSON string with all financial and ESG raw data for {ticker}",
)
