"""
Full sequential CrewAI crew for running all 4 agents in one shot.
Used as an alternative to the LangGraph workflow for simple batch runs.
"""
from crewai import Crew, Process

from backend.agents.data_collection_agent import (
    data_collection_agent,
    data_collection_task,
)
from backend.agents.esg_scoring_agent import esg_scoring_agent, esg_scoring_task
from backend.agents.financial_analysis_agent import (
    financial_analysis_agent,
    financial_analysis_task,
)
from backend.agents.report_generation_agent import (
    report_generation_agent,
    report_generation_task,
)

financial_crew = Crew(
    agents=[
        data_collection_agent,
        financial_analysis_agent,
        esg_scoring_agent,
        report_generation_agent,
    ],
    tasks=[
        data_collection_task,
        financial_analysis_task,
        esg_scoring_task,
        report_generation_task,
    ],
    process=Process.sequential,
    verbose=True,
)
