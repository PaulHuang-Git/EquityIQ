from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class AnalysisJob(Base):
    """Analysis job status tracking"""
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True)          # UUID
    ticker = Column(String, nullable=False)
    status = Column(String, nullable=False)
    # status: pending | running | completed | failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)


class FinancialData(Base):
    """yfinance raw data cache (persistent)"""
    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    # data_type: price | financials | esg | info
    data = Column(JSON, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class AnalysisResult(Base):
    """Agent analysis result storage"""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False)
    job_id = Column(String, nullable=False)
    analysis_type = Column(String, nullable=False)
    # analysis_type: financial | esg | combined
    result = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    """Generated Markdown reports"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False)
    job_id = Column(String, nullable=False)
    report_path = Column(String, nullable=False)
    report_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
