import re
import pandas as pd
import logging
from pathlib import Path
import yaml
import json
import csv

logger = logging.getLogger(__name__)

def load_config(config_path: str = ".slowquerydoctor.yml") -> dict:
    """Load YAML config file if present."""
    path = Path(config_path)
    if path.exists():
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

def parse_postgres_log(log_file_path: str, log_format: str = "plain") -> pd.DataFrame:
    """
    Parses PostgreSQL log file and extracts slow queries

    Args:
        log_file_path: Path to the PostgreSQL log file
        log_format: 'plain', 'csv', or 'json'

    Returns:
        DataFrame with columns [timestamp, duration_ms, query]

    Raises:
        FileNotFoundError: If log file doesn't exist
        ValueError: If no slow query entries found
    """
    log_path = Path(log_file_path)
    if not log_path.exists():
        raise FileNotFoundError(f"Log file not found: {log_file_path}")

    logger.info(f"Parsing log file: {log_file_path} (format: {log_format})")

    if log_format == "plain":
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_text = f.read()
        # Improved regex for multi-line queries and edge cases
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*?duration: ([\d.]+) ms.*?statement: ([\s\S]+?)(?=\n\d{4}-\d{2}-\d{2} |\Z)'
        matches = re.findall(pattern, log_text, re.DOTALL)
        if not matches:
            raise ValueError(
                "No slow query entries found. "
                "Ensure log_min_duration_statement is configured."
            )
        log_entries = []
        for idx, match in enumerate(matches, 1):
            try:
                log_entries.append({
                    'timestamp': pd.to_datetime(match[0]),
                    'duration_ms': float(match[1]),
                    'query': match[2].strip()
                })
                if idx % 1000 == 0:
                    logger.info(f"Parsed {idx} log entries so far...")
            except Exception as e:
                logger.warning(f"Skipping malformed entry: {e}")
                continue
        df = pd.DataFrame(log_entries)
        logger.info(f"Parsed {len(df)} slow query entries (plain)")
        return df

    elif log_format == "csv":
        # Expecting CSV with columns: timestamp,duration_ms,query
        with open(log_file_path, newline='', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = [row for row in reader if 'timestamp' in row and 'duration_ms' in row and 'query' in row]
        if not rows:
            raise ValueError("No slow query entries found in CSV log.")
        df = pd.DataFrame(rows)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['duration_ms'] = df['duration_ms'].astype(float)
        logger.info(f"Parsed {len(df)} slow query entries (csv)")
        return df

    elif log_format == "json":
        # Expecting JSON lines: {"timestamp":..., "duration_ms":..., "query":...}
        log_entries = []
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if 'timestamp' in entry and 'duration_ms' in entry and 'query' in entry:
                        log_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Skipping malformed JSON line: {e}")
        if not log_entries:
            raise ValueError("No slow query entries found in JSON log.")
        df = pd.DataFrame(log_entries)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['duration_ms'] = df['duration_ms'].astype(float)
        logger.info(f"Parsed {len(df)} slow query entries (json)")
        return df

    else:
        raise ValueError(f"Unsupported log format: {log_format}")
