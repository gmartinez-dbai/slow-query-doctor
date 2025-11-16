"""
Slow Query Doctor - AI-powered database performance analyzer

Database Support: PostgreSQL (MySQL/SQL Server in v0.4.0)
AI Providers:
  - v0.1.x: OpenAI GPT only (requires OPENAI_API_KEY)
  - v0.2.0+: Configurable (Ollama default, OpenAI optional)
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
