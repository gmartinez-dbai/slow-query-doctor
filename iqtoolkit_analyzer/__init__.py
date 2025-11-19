"""
Iqtoolkit Analyzer - AI-powered multi-database performance analyzer

Database Support: 
  - PostgreSQL ✓ (Production Ready)
  - MongoDB ✓ (Production Ready) 
  - MySQL (Planned v0.4.0)
  - SQL Server (Planned v0.4.0)

AI Providers:
  - v0.2.2a1: OpenAI integration (requires OPENAI_API_KEY)
  - v0.2.3+: Configurable (Ollama privacy-first, OpenAI optional)

Self-hosted, privacy-first, 100% open source.
"""

__version__ = "0.2.2a1"

from .parser import parse_postgres_log
from .analyzer import run_slow_query_analysis, normalize_query
from .llm_client import LLMClient, LLMConfig
from .report_generator import ReportGenerator
from .antipatterns import (
    AntiPatternDetector,
    StaticQueryRewriter,
    AntiPatternMatch,
    AntiPatternType,
)

__all__ = [
    "parse_postgres_log",
    "run_slow_query_analysis",
    "normalize_query",
    "LLMClient",
    "LLMConfig",
    "ReportGenerator",
    "AntiPatternDetector",
    "StaticQueryRewriter",
    "AntiPatternMatch",
    "AntiPatternType",
]
