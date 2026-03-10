import json
import logging
from typing import Type

import yfinance as yf
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class YahooFinanceInput(BaseModel):
    ticker: str = Field(description="Stock ticker symbol, e.g. AAPL")
    data_type: str = Field(
        description=(
            "Type of data to fetch: "
            "'info' for company info and key statistics, "
            "'price' for 1-year daily price history (OHLCV), "
            "'income_stmt' for annual income statement, "
            "'balance_sheet' for annual balance sheet, "
            "'cashflow' for annual cash flow statement"
        )
    )


class YahooFinanceTool(BaseTool):
    name: str = "Yahoo Finance Tool"
    description: str = (
        "Fetch financial data from Yahoo Finance for a given stock ticker. "
        "Supports data_type: info | price | income_stmt | balance_sheet | cashflow. "
        "Results are cached in Redis for performance."
    )
    args_schema: Type[BaseModel] = YahooFinanceInput

    def _run(self, ticker: str, data_type: str) -> str:
        from backend.cache.redis_manager import cache_manager
        from backend.config.settings import settings

        ticker = ticker.upper()

        # Check L1 Redis cache first
        cached = cache_manager.get_raw_data(ticker, data_type)
        if cached:
            logger.info(f"Cache HIT: {ticker}/{data_type}")
            return json.dumps(cached)

        logger.info(f"Cache MISS: fetching {ticker}/{data_type} from Yahoo Finance")
        try:
            stock = yf.Ticker(ticker)

            if data_type == "info":
                data = stock.info or {}

            elif data_type == "price":
                hist = stock.history(period="1y")
                if hist.empty:
                    return json.dumps({"error": "No price data available", "ticker": ticker})
                hist.index = hist.index.astype(str)
                data = hist.reset_index().to_dict("records")

            elif data_type == "income_stmt":
                df = stock.income_stmt
                if df is None or df.empty:
                    return json.dumps({"error": "No income statement available", "ticker": ticker})
                data = {
                    str(col): {
                        str(idx): (float(val) if val == val else None)
                        for idx, val in df[col].items()
                    }
                    for col in df.columns
                }

            elif data_type == "balance_sheet":
                df = stock.balance_sheet
                if df is None or df.empty:
                    return json.dumps({"error": "No balance sheet available", "ticker": ticker})
                data = {
                    str(col): {
                        str(idx): (float(val) if val == val else None)
                        for idx, val in df[col].items()
                    }
                    for col in df.columns
                }

            elif data_type == "cashflow":
                df = stock.cashflow
                if df is None or df.empty:
                    return json.dumps({"error": "No cashflow data available", "ticker": ticker})
                data = {
                    str(col): {
                        str(idx): (float(val) if val == val else None)
                        for idx, val in df[col].items()
                    }
                    for col in df.columns
                }

            else:
                return json.dumps({"error": f"Unknown data_type: {data_type}"})

            # Cache result with appropriate TTL
            ttl = (
                settings.redis_ttl_price
                if data_type == "price"
                else settings.redis_ttl_financials
            )
            cache_manager.cache_raw_data(ticker, data_type, data, ttl)
            return json.dumps(data, default=str)

        except Exception as e:
            logger.error(f"YahooFinanceTool error [{ticker}/{data_type}]: {e}")
            return json.dumps({"error": str(e), "ticker": ticker, "data_type": data_type})
