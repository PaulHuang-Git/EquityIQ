from crewai import Agent, Task, LLM

from backend.config.settings import settings
from backend.tools.esg_tool import ESGTool

llm = LLM(
    model=f"ollama/{settings.ollama_model}",
    base_url=settings.ollama_base_url,
)

esg_scoring_agent = Agent(
    role="ESG Risk Analyst",
    goal="Extract, analyze and interpret ESG risk data, providing actionable insights for {ticker}",
    backstory=(
        "You specialize in sustainable finance and ESG risk assessment. "
        "With deep knowledge of Sustainalytics methodology and ESG frameworks, "
        "you provide institutional-grade ESG analysis for investment decisions."
    ),
    tools=[ESGTool()],
    llm=llm,
    verbose=True,
)

ESG_SCORING_TASK_DESCRIPTION = """
For stock ticker {ticker}, analyze the ESG risk data provided below.

RAW ESG DATA:
{raw_esg_data}

Provide a comprehensive ESG risk assessment covering:

1. Score interpretation for each dimension (E, S, G)
2. Risk level classification based on total score:
   - Negligible: < 10
   - Low: 10-20
   - Medium: 20-30
   - High: 30-40
   - Severe: > 40
3. Peer comparison context
4. Controversy level assessment (scale 0-5, 5 = highest controversy)
5. Key ESG risks specific to this company's sector
6. Investment implications

Return ONLY a valid JSON object with this exact structure:
{{
  "ticker": "{ticker}",
  "scores": {{
    "total_esg_risk_score": <float or null>,
    "environment_score": <float or null>,
    "social_score": <float or null>,
    "governance_score": <float or null>,
    "risk_level": "<Negligible|Low|Medium|High|Severe|Unknown>",
    "controversy_level": <int or null>
  }},
  "peer_comparison": {{
    "peer_count": <int or null>,
    "peer_percentile": <float or null>
  }},
  "environmental_risk": "...",
  "social_risk": "...",
  "governance_risk": "...",
  "key_esg_risks": ["...", "..."],
  "investment_implications": "...",
  "esg_score_normalized": <float 0-10>,
  "phase2_kpis": {{
    "co2_emissions_tonnes": null,
    "carbon_intensity": null,
    "renewable_energy_pct": null,
    "water_consumption": null,
    "waste_recycling_rate": null,
    "employee_turnover_rate": null,
    "lost_time_injury_rate": null,
    "gender_pay_gap": null,
    "women_in_leadership_pct": null,
    "independent_directors_pct": null,
    "board_diversity_pct": null,
    "audit_committee_quality": null
  }}
}}
"""

esg_scoring_task = Task(
    description=ESG_SCORING_TASK_DESCRIPTION,
    agent=esg_scoring_agent,
    expected_output="Valid JSON string with complete ESG analysis for {ticker}",
)
