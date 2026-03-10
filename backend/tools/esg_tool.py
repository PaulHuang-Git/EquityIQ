import json
import logging
from typing import Type

import yfinance as yf
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Phase 2 reserved ESG KPI fields (all null in Phase 1)
_PHASE2_KPIS = {
    "co2_emissions_tonnes": None,
    "carbon_intensity": None,
    "renewable_energy_pct": None,
    "water_consumption": None,
    "waste_recycling_rate": None,
    "employee_turnover_rate": None,
    "lost_time_injury_rate": None,
    "gender_pay_gap": None,
    "women_in_leadership_pct": None,
    "independent_directors_pct": None,
    "board_diversity_pct": None,
    "audit_committee_quality": None,
}


class ESGInput(BaseModel):
    ticker: str = Field(description="Stock ticker symbol, e.g. AAPL")


class ESGTool(BaseTool):
    name: str = "ESG Data Tool"
    description: str = (
        "Fetch ESG sustainability risk scores from Yahoo Finance (Sustainalytics). "
        "Returns total ESG risk score, Environmental/Social/Governance sub-scores, "
        "risk level classification, controversy level, and peer comparison data. "
        "Lower scores indicate lower ESG risk (better sustainability)."
    )
    args_schema: Type[BaseModel] = ESGInput

    def _run(self, ticker: str) -> str:
        from backend.cache.redis_manager import cache_manager
        from backend.config.settings import settings

        ticker = ticker.upper()

        # Check L1 cache
        cached = cache_manager.get_raw_data(ticker, "esg")
        if cached:
            logger.info(f"Cache HIT: {ticker}/esg")
            return json.dumps(cached)

        logger.info(f"Cache MISS: fetching {ticker}/esg from Yahoo Finance")
        try:
            stock = yf.Ticker(ticker)
            sustainability = stock.sustainability

            if sustainability is None or (
                hasattr(sustainability, "empty") and sustainability.empty
            ):
                data = {
                    "ticker": ticker,
                    "esg_available": False,
                    "total_esg_risk_score": None,
                    "environment_score": None,
                    "social_score": None,
                    "governance_score": None,
                    "esg_risk_level": None,
                    "controversy_level": None,
                    "peer_count": None,
                    "peer_percentile": None,
                    "phase2_kpis": _PHASE2_KPIS.copy(),
                }
            else:
                def safe_get(df, key):
                    try:
                        if key in df.index:
                            val = df.loc[key, "Value"] if "Value" in df.columns else df.loc[key].iloc[0]
                            if val is None:
                                return None
                            # Check for NaN
                            try:
                                import math
                                if math.isnan(float(val)):
                                    return None
                            except (TypeError, ValueError):
                                pass
                            try:
                                return float(val)
                            except (TypeError, ValueError):
                                return str(val)
                        return None
                    except Exception:
                        return None

                s = sustainability
                data = {
                    "ticker": ticker,
                    "esg_available": True,
                    "total_esg_risk_score": safe_get(s, "totalEsg"),
                    "environment_score": safe_get(s, "environmentScore"),
                    "social_score": safe_get(s, "socialScore"),
                    "governance_score": safe_get(s, "governanceScore"),
                    "esg_risk_level": safe_get(s, "esgPerformance"),
                    "controversy_level": safe_get(s, "highestControversy"),
                    "peer_count": safe_get(s, "peerCount"),
                    "peer_percentile": safe_get(s, "peerEsgScorePerformance"),
                    "phase2_kpis": _PHASE2_KPIS.copy(),
                }

            cache_manager.cache_raw_data(
                ticker, "esg", data, settings.redis_ttl_financials
            )
            return json.dumps(data)

        except Exception as e:
            logger.error(f"ESGTool error [{ticker}]: {e}")
            return json.dumps(
                {
                    "error": str(e),
                    "ticker": ticker,
                    "esg_available": False,
                    "phase2_kpis": _PHASE2_KPIS.copy(),
                }
            )
