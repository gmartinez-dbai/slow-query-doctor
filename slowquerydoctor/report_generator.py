import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from .analyzer import SlowQuery
from .llm_client import LLMClient

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates comprehensive analysis reports with AI recommendations and anti-pattern detection."""

    def __init__(self, llm_client: LLMClient, output_dir: str = "reports"):
        self.llm_client = llm_client
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

    def generate_report(self, top_queries: List[SlowQuery], all_queries: List[SlowQuery]) -> str:
        """
        Generate a comprehensive slow query analysis report.

        Args:
            top_queries: Top slow queries to analyze in detail
            all_queries: All analyzed queries for summary statistics

        Returns:
            Formatted Markdown report
        """
        report = []

        # Header
        report.append("# 🩺 Slow Query Analysis Report")
        report.append(f"*Generated on {self._get_current_timestamp()}*\n")

        # Summary section
        report.append(self._generate_summary(all_queries))

        # Top queries analysis
        if top_queries:
            report.append("## 🐌 Top Slow Queries Analysis\n")

            for i, query in enumerate(top_queries, 1):
                report.append(self._generate_query_analysis(query, i))

        # Anti-pattern summary
        report.append(self._generate_antipattern_summary(all_queries))

        # Recommendations summary
        report.append(self._generate_recommendations_summary(all_queries))

        return "\n".join(report)

    def _generate_query_analysis(self, query: SlowQuery, rank: int) -> str:
        """Generate detailed analysis for a single query."""
        analysis = []

        # Query header
        analysis.append(f"### Query #{rank}: {self._get_query_title(query)}")
        analysis.append(f"**Impact Score**: {query.impact_score:.2f} | "
                       f"**Duration**: {query.duration:.2f}ms | "
                       f"**Frequency**: {query.frequency} | "
                       f"**Optimization Score**: {query.optimization_score:.1%}")
        analysis.append(f"**First seen**: {query.timestamp}\n")

        # Query code block
        analysis.append("```sql")
        analysis.append(query.normalized_query)
        analysis.append("```\n")

        # Anti-pattern analysis (if any issues found)
        if query.antipattern_matches:
            analysis.append("#### 🔍 Static Analysis Issues")
            analysis.append(query.static_analysis_report)

        # AI-powered recommendations
        try:
            ai_recommendation = self.llm_client.get_optimization_advice(
                query.normalized_query,
                query.duration,
                query.frequency
            )
            analysis.append("#### 🤖 AI-Powered Optimization Recommendations")
            analysis.append(ai_recommendation)
        except Exception as e:
            logger.warning(f"Failed to get AI recommendation for query {rank}: {e}")
            analysis.append("#### 🤖 AI Analysis")
            analysis.append("*AI analysis temporarily unavailable*")

        analysis.append("\n---\n")
        return "\n".join(analysis)

    def _generate_antipattern_summary(self, queries: List[SlowQuery]) -> str:
        """Generate summary of anti-patterns found across all queries."""
        summary = []
        summary.append("## 🚨 Anti-Pattern Analysis Summary\n")

        # Count anti-patterns across all queries
        pattern_counts = {}
        total_issues = 0
        queries_with_issues = 0

        for query in queries:
            if query.antipattern_matches:
                queries_with_issues += 1
                for match in query.antipattern_matches:
                    pattern_type = match.pattern_type.value.replace('_', ' ').title()
                    pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
                    total_issues += 1

        if total_issues == 0:
            summary.append("✅ **No anti-patterns detected** - Your queries follow good practices!")
            summary.append("")
            return "\n".join(summary)

        # Statistics
        summary.append(f"- **Total Issues Found**: {total_issues}")
        summary.append(f"- **Queries with Issues**: {queries_with_issues}/{len(queries)} ({queries_with_issues/len(queries)*100:.1f}%)")
        summary.append(f"- **Average Optimization Score**: {sum(q.optimization_score for q in queries)/len(queries):.1%}")
        summary.append("")

        # Most common anti-patterns
        if pattern_counts:
            summary.append("### Most Common Anti-Patterns")
            for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
                summary.append(f"- **{pattern}**: {count} occurrence{'s' if count > 1 else ''}")
            summary.append("")

        return "\n".join(summary)

    def _generate_recommendations_summary(self, queries: List[SlowQuery]) -> str:
        """Generate summary of key recommendations."""
        summary = []
        summary.append("## 💡 Key Recommendations\n")

        # Priority recommendations based on anti-patterns
        high_impact = [q for q in queries if q.optimization_score < 0.7]

        if high_impact:
            summary.append("### 🔥 High Priority")
            for query in high_impact[:3]:  # Top 3 high-impact queries
                summary.append(f"- **Query with impact score {query.impact_score:.0f}**: "
                              f"Optimization score {query.optimization_score:.1%} - "
                              f"{len(query.antipattern_matches)} anti-pattern{'s' if len(query.antipattern_matches) > 1 else ''} detected")
            summary.append("")

        # General recommendations
        summary.append("### 📋 General Recommendations")
        summary.append("1. **Index Analysis**: Review missing indexes for columns in WHERE clauses")
        summary.append("2. **Query Patterns**: Address anti-patterns identified in static analysis")
        summary.append("3. **Monitoring**: Set up regular monitoring for queries with high impact scores")
        summary.append("4. **Testing**: Validate optimizations in a staging environment first")
        summary.append("")

        return "\n".join(summary)

    def _get_current_timestamp(self) -> str:
        """Get the current timestamp as a formatted string."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _get_query_title(self, query: SlowQuery) -> str:
        """Generate a title for the query section in the report."""
        return f"Impact Score: {query.impact_score:.2f} | Duration: {query.duration:.2f} ms | Frequency: {query.frequency}"
