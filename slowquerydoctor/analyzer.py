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

# Update the module-level function to support both old and new interfaces
def analyze_slow_queries(data, min_duration: float = 1000, top_n: int = 10):
    """
    Analyze slow queries and return sorted list by impact score.
    
    Supports two interfaces for backward compatibility:
    1. New: analyze_slow_queries(queries: List[Dict], min_duration) -> List[SlowQuery]
    2. Old: analyze_slow_queries(df: pd.DataFrame, top_n) -> Tuple[pd.DataFrame, Dict]
    
    Args:
        data: Either a DataFrame (old interface) or List[Dict] (new interface)
        min_duration: Minimum duration in ms (new interface only)
        top_n: Number of top queries to return (old interface only)
    
    Returns:
        Either List[SlowQuery] (new) or Tuple[pd.DataFrame, Dict] (old)
    """
    # Check if using old interface (DataFrame input)
    if isinstance(data, pd.DataFrame):
        # Old interface: return DataFrame and summary dict
        df = data
        if df.empty:
            logger.warning("Empty dataframe provided to analyzer")
            return pd.DataFrame(), {}

        logger.info(f"Analyzing {len(df)} query entries")

        # Normalize queries for better grouping
        df['normalized_query'] = df['query'].apply(normalize_query)

        # Group by normalized query
        query_stats = df.groupby('normalized_query').agg({
            'duration_ms': ['mean', 'max', 'min', 'count'],
            'query': 'first'  # Keep one example of the original query
        }).reset_index()

        query_stats.columns = ['normalized_query', 'avg_duration', 'max_duration',
                               'min_duration', 'frequency', 'example_query']

        # Calculate impact score (avg_duration * frequency)
        query_stats['impact_score'] = query_stats['avg_duration'] * query_stats['frequency']

        # Sort by impact score (not just avg_duration)
        top_slow = query_stats.sort_values('impact_score', ascending=False).head(top_n)

        # Summary statistics
        summary = {
            'total_queries': len(df),
            'unique_queries': len(query_stats),
            'avg_duration_overall': float(df['duration_ms'].mean()),
            'max_duration_overall': float(df['duration_ms'].max()),
            'min_duration_overall': float(df['duration_ms'].min()),
            'p50_duration': float(df['duration_ms'].quantile(0.50)),
            'p95_duration': float(df['duration_ms'].quantile(0.95)),
            'p99_duration': float(df['duration_ms'].quantile(0.99)),
            'total_time_spent': float(df['duration_ms'].sum())
        }

        logger.info(f"Found {len(query_stats)} unique query patterns, returning top {len(top_slow)}")
        return top_slow, summary
    
    else:
        # New interface: return List[SlowQuery]
        analyzer = SlowQueryAnalyzer()
        return analyzer.analyze_slow_queries(data, min_duration)
