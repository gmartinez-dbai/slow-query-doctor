import hashlib  # This import is used for generating query hashes
import logging  # This import is used for logging warnings and info
import math  # This import is used for mathematical computations
import re  # this import is used for regular expressions
from collections import defaultdict  # This import is used for grouping queries
from dataclasses import dataclass, field  # This import is used for data classes
from typing import (
    Any,
    Dict,
    List,
    Sequence,
    Tuple,
    TypedDict,
    Union,
    cast,
)  # This import is used for type hinting

import pandas as pd  # This import is used for data manipulation and analysis

from .antipatterns import (
    StaticQueryRewriter,
    AntiPatternMatch,
)  # This import is used for query rewriting and anti-pattern detection

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
        query = re.sub(r"\b\d+\b", "?", query)
        # Replace IN clauses with multiple values
        query = re.sub(r"IN\s*\([^)]+\)", "IN (?)", query, flags=re.IGNORECASE)
        # Normalize whitespace
        query = " ".join(query.split())
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
    max_duration: float = 0.0
    min_duration: float = 0.0
    total_duration: float = 0.0
    first_seen: str = ""
    last_seen: str = ""
    frequency: int = 1
    impact_score: float = 0.0
    query_hash: str = ""

    # Add anti-pattern analysis fields
    antipattern_matches: List[AntiPatternMatch] = field(
        default_factory=lambda: cast(List[AntiPatternMatch], [])
    )
    optimization_score: float = 1.0
    static_analysis_report: str = ""


class QueryRecord(TypedDict):
    """Represents a raw query record from logs."""

    statement: str
    duration: float
    timestamp: str


class NormalizedQueryRecord(TypedDict):
    """Represents a normalized query record."""

    raw: str
    normalized: str
    duration: float
    timestamp: str
    hash: str


class SlowQueryAnalyzer:
    """Analyzes slow queries and calculates impact scores."""

    def __init__(self) -> None:
        self.query_rewriter = StaticQueryRewriter()  # Initialize the query rewriter

    def analyze_slow_queries(
        self, queries: Sequence[QueryRecord], min_duration: float = 1000
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

        slow_queries: List[QueryRecord] = [
            query for query in queries if query["duration"] >= min_duration
        ]

        if not slow_queries:
            return []

        query_groups: defaultdict[str, List[NormalizedQueryRecord]] = defaultdict(list)

        for query in slow_queries:
            normalized = normalize_query(query["statement"])
            query_hash = hashlib.md5(normalized.encode()).hexdigest()

            record: NormalizedQueryRecord = {
                "raw": query["statement"],
                "normalized": normalized,
                "duration": float(query["duration"]),
                "timestamp": str(query["timestamp"]),
                "hash": query_hash,
            }
            query_groups[query_hash].append(record)

        analyzed_queries: List[SlowQuery] = []

        for query_hash, group in query_groups.items():
            durations: List[float] = [q["duration"] for q in group]
            frequency = len(group)
            avg_duration = sum(durations) / frequency
            total_duration = sum(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            timestamps = [q["timestamp"] for q in group]
            first_seen = min(timestamps)
            last_seen = max(timestamps)

            impact_score = avg_duration * frequency

            representative_query = group[0]["normalized"]
            antipattern_matches, static_report = self.query_rewriter.analyze_query(
                representative_query
            )
            optimization_score = self.query_rewriter.get_optimization_score(
                antipattern_matches
            )

            slow_query = SlowQuery(
                raw_query=group[0]["raw"],
                normalized_query=representative_query,
                duration=avg_duration,
                timestamp=first_seen,
                frequency=frequency,
                impact_score=impact_score,
                query_hash=query_hash,
                antipattern_matches=antipattern_matches or [],
                optimization_score=optimization_score,
                static_analysis_report=static_report,
                max_duration=max_duration,
                min_duration=min_duration,
                total_duration=total_duration,
                first_seen=first_seen,
                last_seen=last_seen,
            )

            analyzed_queries.append(slow_query)

        return sorted(
            analyzed_queries, key=lambda query: query.impact_score, reverse=True
        )


def _compute_percentile(values: Sequence[float], percentile: float) -> float:
    if not values:
        return 0.0

    sorted_vals = sorted(values)
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])

    position = (len(sorted_vals) - 1) * percentile
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    lower_val = sorted_vals[lower_index]
    upper_val = sorted_vals[upper_index]

    if lower_index == upper_index:
        return float(lower_val)

    weight = position - lower_index
    return float(lower_val + (upper_val - lower_val) * weight)


def _build_summary(
    durations: Sequence[float], analyzed_queries: List[SlowQuery]
) -> Dict[str, float]:
    duration_list = list(durations)

    if not duration_list:
        return {
            "total_queries": 0.0,
            "unique_queries": 0.0,
            "avg_duration_overall": 0.0,
            "max_duration_overall": 0.0,
            "p95_duration": 0.0,
            "p99_duration": 0.0,
            "total_time_spent": 0.0,
        }

    total_time = float(sum(duration_list))
    total_queries = len(duration_list)

    return {
        "total_queries": float(total_queries),
        "unique_queries": float(len(analyzed_queries)),
        "avg_duration_overall": total_time / total_queries,
        "max_duration_overall": float(max(duration_list)),
        "p95_duration": _compute_percentile(duration_list, 0.95),
        "p99_duration": _compute_percentile(duration_list, 0.99),
        "total_time_spent": total_time,
    }


def _build_dataframe(queries: List[SlowQuery]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for query in queries:
        rows.append(
            {
                "normalized_query": query.normalized_query,
                "example_query": query.raw_query,
                "avg_duration": query.duration,
                "max_duration": query.max_duration,
                "min_duration": query.min_duration,
                "total_duration": query.total_duration,
                "frequency": query.frequency,
                "impact_score": query.impact_score,
                "first_seen": query.first_seen,
                "last_seen": query.last_seen,
                "optimization_score": query.optimization_score,
                "static_analysis_report": query.static_analysis_report,
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "normalized_query",
                "example_query",
                "avg_duration",
                "max_duration",
                "min_duration",
                "total_duration",
                "frequency",
                "impact_score",
                "first_seen",
                "last_seen",
                "optimization_score",
                "static_analysis_report",
            ]
        )

    return pd.DataFrame(rows)


def run_slow_query_analysis(
    data: Union[pd.DataFrame, Sequence[QueryRecord]],
    top_n: int = 5,
    min_duration: float = 0.0,
) -> Union[List[SlowQuery], Tuple[pd.DataFrame, Dict[str, float]]]:
    """Analyze slow queries.

    If a list of query dicts is provided, returns a list of SlowQuery objects
    for backward compatibility. If a DataFrame is provided, returns a tuple of
    (top_queries_df, summary_dict) suitable for reporting.
    """

    analyzer = SlowQueryAnalyzer()

    # Backward compatibility path for iterable query records
    if isinstance(data, Sequence) and not isinstance(data, pd.DataFrame):
        return analyzer.analyze_slow_queries(list(data), min_duration)

    # DataFrame path
    log_df = data

    if getattr(log_df, "empty", True):
        raise ValueError("No log entries available for analysis.")

    columns = set(map(str, getattr(log_df, "columns", [])))
    required_columns = {"timestamp", "duration_ms", "query"}
    if not required_columns.issubset(columns):
        missing = required_columns - columns
        raise ValueError(f"Log DataFrame missing required columns: {missing}")

    to_dict_method = getattr(log_df, "to_dict", None)
    if not callable(to_dict_method):
        raise ValueError("Log DataFrame cannot be converted to records for analysis.")

    raw_records = to_dict_method(orient="records")
    records = cast(List[Dict[str, Any]], raw_records or [])

    query_dicts: List[QueryRecord] = []
    durations_for_summary: List[float] = []

    for entry in records:

        try:
            duration = float(entry["duration_ms"])
        except (KeyError, TypeError, ValueError):
            continue

        if duration < min_duration:
            continue

        timestamp = entry.get("timestamp")
        query_text = entry.get("query")

        if timestamp is None or query_text is None:
            continue

        record: QueryRecord = {
            "statement": str(query_text),
            "duration": duration,
            "timestamp": str(timestamp),
        }

        query_dicts.append(record)
        durations_for_summary.append(duration)

    if not query_dicts:
        raise ValueError("No slow query entries meet the minimum duration threshold.")

    analyzed_queries = analyzer.analyze_slow_queries(query_dicts, min_duration)

    if not analyzed_queries:
        raise ValueError("No slow queries matched the analysis criteria.")

    summary = _build_summary(durations_for_summary, analyzed_queries)

    result_df = _build_dataframe(analyzed_queries)
    result_df = result_df.sort_values("impact_score", ascending=False)

    if top_n > 0:
        result_df = result_df.head(top_n)

    result_df = result_df.reset_index(drop=True)

    return result_df, summary
