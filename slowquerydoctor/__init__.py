"""
Slow Query Doctor - AI-powered database performance analyzer
Currently supports PostgreSQL with MySQL/SQL Server planned for v0.4.0
"""

__version__ = "0.1.6"

from .parser import parse_postgres_log
from .analyzer import run_slow_query_analysis, normalize_query
from .llm_client import LLMClient, LLMConfig
from .report_generator import ReportGenerator
from .antipatterns import AntiPatternDetector, StaticQueryRewriter, AntiPatternMatch, AntiPatternType

__all__ = [
    'parse_postgres_log',
    'run_slow_query_analysis',
    'normalize_query',
    'LLMClient', 
    'LLMConfig',
    'ReportGenerator',
    'AntiPatternDetector',
    'StaticQueryRewriter',
    'AntiPatternMatch',
    'AntiPatternType',
]
