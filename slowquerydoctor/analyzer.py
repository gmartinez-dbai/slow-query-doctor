import pandas as pd
import re
import logging
from typing import Tuple, Dict

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


def analyze_slow_queries(df: pd.DataFrame, top_n: int = 5) -> Tuple[pd.DataFrame, Dict]:
    """
    Analyzes parsed log data and returns top issues

    Args:
        df: DataFrame with columns [timestamp, duration_ms, query]
        top_n: Number of top slow queries to return

    Returns:
        Tuple of (top_slow_queries_df, summary_stats)
    """
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