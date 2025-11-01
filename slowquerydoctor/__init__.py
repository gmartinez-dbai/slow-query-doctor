"""
Slow Query Doctor - AI-powered PostgreSQL performance analyzer
"""

__version__ = "0.1.5"

from .parser import parse_postgres_log
from .analyzer import analyze_slow_queries, normalize_query
from .llm_client import LLMClient, LLMConfig
from .report_generator import ReportGenerator
from .antipatterns import AntiPatternDetector, StaticQueryRewriter, AntiPatternMatch, AntiPatternType

__all__ = [
    'parse_postgres_log',
    'analyze_slow_queries',
    'normalize_query',
    'LLMClient', 
    'LLMConfig',
    'ReportGenerator',
    'AntiPatternDetector',
    'StaticQueryRewriter',
    'AntiPatternMatch',
    'AntiPatternType',
]
