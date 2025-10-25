import re
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_postgres_log(log_file_path: str) -> pd.DataFrame:
    """
    Parses PostgreSQL log file and extracts slow queries

    Args:
        log_file_path: Path to the PostgreSQL log file

    Returns:
        DataFrame with columns [timestamp, duration_ms, query]

    Raises:
        FileNotFoundError: If log file doesn't exist
        ValueError: If no slow query entries found
    """
    log_path = Path(log_file_path)
    if not log_path.exists():
        raise FileNotFoundError(f"Log file not found: {log_file_path}")

    logger.info(f"Parsing log file: {log_file_path}")

    # Read log file
    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        log_text = f.read()

    # Regex pattern for log_min_duration_statement entries
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*?duration: ([\d.]+) ms.*?statement: (.+?)(?=\n\d{4}-\d{2}-\d{2}|\Z)'

    matches = re.findall(pattern, log_text, re.DOTALL)

    if not matches:
        raise ValueError(
            "No slow query entries found. "
            "Ensure log_min_duration_statement is configured."
        )

    # Parse matches into DataFrame
    log_entries = []
    for match in matches:
        try:
            log_entries.append({
                'timestamp': pd.to_datetime(match[0]),
                'duration_ms': float(match[1]),
                'query': match[2].strip()
            })
        except Exception as e:
            logger.warning(f"Skipping malformed entry: {e}")
            continue

    df = pd.DataFrame(log_entries)
    logger.info(f"Parsed {len(df)} slow query entries")

    return df
