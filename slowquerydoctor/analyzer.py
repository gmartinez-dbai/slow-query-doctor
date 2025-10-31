import hashlib
import pandas as pd
import re
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from .antipatterns import StaticQueryRewriter, AntiPatternMatch

logger = logging.getLogger(__name__)


def normalize_query(query: str) -> str:
    """
    Normalizes SQL query by removing literals for better grouping

    Args:
        query: Raw SQL query string

    Returns:
        Normalized query string
    """
    try:
        # Replace string literals
        query = re.sub(r"'[^']*'", "'?'", query)
        # Replace numeric literals
        query = re.sub(r'\b\d+\b', '?', query)
        # Replace IN clauses with multiple values
        query = re.sub(r'IN\s*\([^)]+\)', 'IN (?)', query, flags=re.IGNORECASE)
        # Normalize whitespace
        query = ' '.join(query.split())
        return query.lower()
    except Exception as e:
        logger.warning(f"Error normalizing query: {e}")
        return query.lower()


@dataclass
class SlowQuery:
    """Represents a slow query with analysis metadata."""
    raw_query: str
    normalized_query: str
    duration: float
    timestamp: str
    frequency: int = 1
    impact_score: float = 0.0
    query_hash: str = ""
    
    # Add anti-pattern analysis fields - use field(default_factory) to avoid mutable default
    antipattern_matches: List[AntiPatternMatch] = field(default_factory=list)
    optimization_score: float = 1.0
    static_analysis_report: str = ""

class SlowQueryAnalyzer:
    """Analyzes slow queries and calculates impact scores."""
    
    def __init__(self):
        self.query_rewriter = StaticQueryRewriter()
    
    def analyze_slow_queries(
        self, 
        queries: List[Dict], 
        min_duration: float = 1000
    ) -> List[SlowQuery]:
        """
        Analyze slow queries and calculate impact scores with anti-pattern detection.
        
        Args:
            queries: List of query dicts from log parser
            min_duration: Minimum duration in ms to consider slow
            
        Returns:
            List of analyzed SlowQuery objects sorted by impact score
        """
        if not queries:
            return []
        
        # Filter queries by minimum duration
        slow_queries = [q for q in queries if q.get('duration', 0) >= min_duration]
        
        if not slow_queries:
            return []
        
        # Group queries by normalized form
        query_groups = defaultdict(list)
        
        for query in slow_queries:
            normalized = normalize_query(query['statement'])
            query_hash = hashlib.md5(normalized.encode()).hexdigest()
            
            query_groups[query_hash].append({
                'raw': query['statement'],
                'normalized': normalized,
                'duration': query['duration'],
                'timestamp': query['timestamp'],
                'hash': query_hash
            })
        
        # Create SlowQuery objects with analysis
        analyzed_queries = []
        
        for query_hash, group in query_groups.items():
            # Calculate aggregated metrics
            durations = [q['duration'] for q in group]
            frequency = len(group)
            avg_duration = sum(durations) / frequency
            
            # Calculate impact score
            impact_score = avg_duration * frequency
            
            # Perform anti-pattern analysis on the normalized query
            representative_query = group[0]['normalized']
            antipattern_matches, static_report = self.query_rewriter.analyze_query(representative_query)
            optimization_score = self.query_rewriter.get_optimization_score(antipattern_matches)
            
            slow_query = SlowQuery(
                raw_query=group[0]['raw'],
                normalized_query=representative_query,
                duration=avg_duration,
                timestamp=group[0]['timestamp'],
                frequency=frequency,
                impact_score=impact_score,
                query_hash=query_hash,
                antipattern_matches=antipattern_matches or [],
                optimization_score=optimization_score,
                static_analysis_report=static_report
            )
            
            analyzed_queries.append(slow_query)
        
        # Sort by impact score (descending)
        return sorted(analyzed_queries, key=lambda q: q.impact_score, reverse=True)

# Update the module-level function
def analyze_slow_queries(queries: List[Dict], min_duration: float = 1000) -> List[SlowQuery]:
    """Analyze slow queries and return sorted list by impact score."""
    analyzer = SlowQueryAnalyzer()
    return analyzer.analyze_slow_queries(queries, min_duration)
