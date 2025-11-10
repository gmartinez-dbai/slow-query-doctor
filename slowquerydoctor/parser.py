import re
import pandas as pd
import logging
from tqdm import tqdm
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
    Parses database log file and extracts slow queries (currently PostgreSQL format)

    Args:
        log_file_path: Path to the database log file
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
        with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            log_text = f.read()
        # Improved regex for multi-line queries and edge cases
        pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}).*?duration: ([\d.]+) ms.*?statement: ([\s\S]+?)(?=\n\d{4}-\d{2}-\d{2} |\Z)"
        matches = re.findall(pattern, log_text, re.DOTALL)
        if not matches:
            logger.warning(
                "No slow query entries matched the expected pattern. Check your log format and log_min_duration_statement setting."
            )
            print(
                "No slow query entries matched the expected pattern. Check your log format and log_min_duration_statement setting."
            )
            raise ValueError(
                "No slow query entries found. "
                "Ensure log_min_duration_statement is configured."
            )
        log_entries = []
        # Always show progress bar, even for small files
        for idx, match in enumerate(
            tqdm(
                matches,
                desc="Parsing log entries",
                unit="entry",
                mininterval=0.1,
                miniters=1,
            )
        ):
            if idx > 0 and idx % 100 == 0:
                print(f"Examined {idx} log entries...")
                logger.info(f"Examined {idx} log entries...")
            try:
                log_entries.append(
                    {
                        "timestamp": pd.to_datetime(match[0]),
                        "duration_ms": float(match[1]),
                        "query": match[2].strip(),
                    }
                )
            except Exception as e:
                logger.warning(f"Skipping malformed entry: {e}")
                continue
        df = pd.DataFrame(log_entries)
        logger.info(f"Parsed {len(df)} slow query entries (plain)")
        return df

    elif log_format == "csv":
        # Expecting CSV with columns: timestamp,duration_ms,query
        with open(
            log_file_path, newline="", encoding="utf-8", errors="ignore"
        ) as csvfile:
            reader = list(csv.DictReader(csvfile))
            total = len(reader)
            if total == 0:
                logger.warning("CSV log file is empty or missing required columns.")
                print("CSV log file is empty or missing required columns.")
                raise ValueError("No slow query entries found in CSV log.")
            rows = []
            for idx, row in enumerate(
                tqdm(
                    reader,
                    desc="Parsing CSV log entries",
                    unit="entry",
                    mininterval=0.1,
                    miniters=1,
                )
            ):
                if idx > 0 and idx % 100 == 0:
                    print(f"Examined {idx} CSV log entries...")
                    logger.info(f"Examined {idx} CSV log entries...")
                if "timestamp" in row and "duration_ms" in row and "query" in row:
                    rows.append(row)
        if not rows:
            logger.warning("No valid slow query entries found in CSV log.")
            print("No valid slow query entries found in CSV log.")
            raise ValueError("No slow query entries found in CSV log.")
        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["duration_ms"] = df["duration_ms"].astype(float)
        logger.info(f"Parsed {len(df)} slow query entries (csv)")
        return df

    elif log_format == "json":
        # Expecting JSON lines: {"timestamp":..., "duration_ms":..., "query":...}
        log_entries = []
        with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            total = len(lines)
            if total == 0:
                logger.warning("JSON log file is empty.")
                print("JSON log file is empty.")
                raise ValueError("No slow query entries found in JSON log.")
            for idx, line in enumerate(
                tqdm(
                    lines,
                    desc="Parsing JSON log entries",
                    unit="entry",
                    mininterval=0.1,
                    miniters=1,
                )
            ):
                if idx > 0 and idx % 100 == 0:
                    print(f"Examined {idx} JSON log entries...")
                    logger.info(f"Examined {idx} JSON log entries...")
                try:
                    entry = json.loads(line)
                    if (
                        "timestamp" in entry
                        and "duration_ms" in entry
                        and "query" in entry
                    ):
                        log_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Skipping malformed JSON line: {e}")
        if not log_entries:
            logger.warning("No valid slow query entries found in JSON log.")
            print("No valid slow query entries found in JSON log.")
            raise ValueError("No slow query entries found in JSON log.")
        df = pd.DataFrame(log_entries)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["duration_ms"] = df["duration_ms"].astype(float)
        logger.info(f"Parsed {len(df)} slow query entries (json)")
        return df

    else:
        raise ValueError(f"Unsupported log format: {log_format}")
