import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates Markdown reports"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Report generator initialized with output dir: {output_dir}")

    def generate_markdown_report(
            self,
            top_queries: pd.DataFrame,
            summary: Dict,
            recommendations: Optional[list] = None
    ) -> str:
        """
        Generate a Markdown report

        Args:
            top_queries: DataFrame with top slow queries
            summary: Dictionary with summary statistics
            recommendations: Optional list of LLM recommendations

        Returns:
            Report text as string
        """
        lines = []

        # Header
        lines.append("# PostgreSQL Performance Analysis Report")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Summary
        lines.append("## Summary Statistics\n")
        lines.append(f"- **Total Queries Analyzed:** {summary['total_queries']}")
        lines.append(f"- **Unique Query Patterns:** {summary['unique_queries']}")
        lines.append(f"- **Average Duration:** {summary['avg_duration_overall']:.2f} ms")
        lines.append(f"- **Max Duration:** {summary['max_duration_overall']:.2f} ms")
        lines.append(f"- **P95 Duration:** {summary['p95_duration']:.2f} ms")
        lines.append(f"- **P99 Duration:** {summary['p99_duration']:.2f} ms")
        lines.append(f"- **Total Time Spent:** {summary['total_time_spent'] / 1000:.2f} seconds\n")

        # Top queries
        lines.append("## Top Slow Queries (by Impact)\n")

        for rank, (idx, row) in enumerate(top_queries.iterrows(), start=1):
            lines.append(f"### Query #{rank}\n")
            lines.append("```sql")
            lines.append(row['example_query'][:500])
            lines.append("```\n")
            lines.append(f"- **Average Duration:** {row['avg_duration']:.2f} ms")
            lines.append(f"- **Max Duration:** {row['max_duration']:.2f} ms")
            lines.append(f"- **Frequency:** {row['frequency']} executions")
            lines.append(f"- **Impact Score:** {row['impact_score']:.2f}\n")

            if recommendations and rank - 1 < len(recommendations):
                lines.append("**AI Recommendation:**\n")
                lines.append(f"{recommendations[rank - 1]}\n")

            lines.append("---\n")

        return "\n".join(lines)