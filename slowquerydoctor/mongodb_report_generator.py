"""
MongoDB Report Generator Module

This module provides specialized report generation for MongoDB slow query analysis,
including detailed performance insights, optimization recommendations, and
comprehensive collection-level analysis.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure

    matplotlib_available = True
except ImportError:
    plt = None
    mdates = None
    Figure = None
    matplotlib_available = False

from .mongodb_config import MongoDBConfig

logger = logging.getLogger(__name__)


class MongoDBReportGenerator:
    """Generates comprehensive reports for MongoDB slow query analysis."""

    def __init__(self, config: MongoDBConfig):
        self.config = config
        self.report_timestamp = datetime.now()

    def generate_json_report(
        self, analysis_data: Dict[str, Any], output_path: str
    ) -> bool:
        """
        Generate JSON format report.

        Args:
            analysis_data: Complete analysis results
            output_path: Path to save the report

        Returns:
            True if report was generated successfully
        """
        try:
            report = self._create_base_report(analysis_data)

            with open(output_path, "w") as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"JSON report generated: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate JSON report: {e}")
            return False

    def generate_markdown_report(
        self, analysis_data: Dict[str, Any], output_path: str
    ) -> bool:
        """
        Generate Markdown format report.

        Args:
            analysis_data: Complete analysis results
            output_path: Path to save the report

        Returns:
            True if report was generated successfully
        """
        try:
            markdown_content = self._create_markdown_content(analysis_data)

            with open(output_path, "w") as f:
                f.write(markdown_content)

            logger.info(f"Markdown report generated: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate Markdown report: {e}")
            return False

    def generate_html_report(
        self, analysis_data: Dict[str, Any], output_path: str
    ) -> bool:
        """
        Generate HTML format report with enhanced visualization.

        Args:
            analysis_data: Complete analysis results
            output_path: Path to save the report

        Returns:
            True if report was generated successfully
        """
        try:
            html_content = self._create_html_content(analysis_data)

            with open(output_path, "w") as f:
                f.write(html_content)

            logger.info(f"HTML report generated: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            return False

    def _create_base_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create base report structure."""
        return {
            "metadata": {
                "generated_at": self.report_timestamp.isoformat(),
                "database_name": analysis_data.get("database_name", "unknown"),
                "analysis_timestamp": analysis_data.get("analysis_timestamp"),
                "configuration": self._get_config_summary(),
                "tool_version": "1.0.0",
            },
            "executive_summary": self._create_executive_summary(analysis_data),
            "slow_queries": analysis_data.get("slow_queries", []),
            "collection_analyses": analysis_data.get("collection_analyses", []),
            "summary_statistics": analysis_data.get("summary", {}),
            "recommendations": analysis_data.get("recommendations", []),
            "appendix": self._create_appendix(analysis_data),
        }

    def _get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for the report."""
        summary: Dict[str, Any] = {}

        if self.config.thresholds:
            summary["thresholds"] = {
                "slow_threshold_ms": self.config.thresholds.slow_threshold_ms,
                "very_slow_threshold_ms": self.config.thresholds.very_slow_threshold_ms,
                "critical_threshold_ms": self.config.thresholds.critical_threshold_ms,
            }

        if self.config.analysis:
            summary["analysis_settings"] = {
                "normalize_queries": self.config.analysis.normalize_queries,
                "group_similar_queries": self.config.analysis.group_similar_queries,
                "analyze_collections": self.config.analysis.analyze_collections,
            }

        return summary

    def _create_executive_summary(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create executive summary section."""
        summary_stats = analysis_data.get("summary", {})
        slow_queries = analysis_data.get("slow_queries", [])

        # Calculate key metrics
        total_queries = summary_stats.get("total_slow_queries", 0)
        total_executions = summary_stats.get("total_executions", 0)
        avg_duration = summary_stats.get("avg_duration_ms", 0)
        collections_affected = summary_stats.get("collections_affected", 0)

        # Categorize queries by severity
        critical_queries = len(
            [q for q in slow_queries if q.get("impact_score", 0) > 70]
        )
        high_impact_queries = len(
            [q for q in slow_queries if 50 <= q.get("impact_score", 0) <= 70]
        )

        # Identify most problematic areas
        collection_impact: Dict[str, float] = {}
        operation_impact: Dict[str, float] = {}

        for query in slow_queries:
            collection = query.get("collection", "unknown")
            operation = query.get("operation_type", "unknown")
            impact = query.get("impact_score", 0)
            frequency = query.get("frequency", 1)

            collection_impact[collection] = (
                collection_impact.get(collection, 0.0) + impact * frequency
            )
            operation_impact[operation] = (
                operation_impact.get(operation, 0.0) + impact * frequency
            )

        most_problematic_collection = (
            max(collection_impact.items(), key=lambda x: x[1])[0]
            if collection_impact
            else None
        )
        most_problematic_operation = (
            max(operation_impact.items(), key=lambda x: x[1])[0]
            if operation_impact
            else None
        )

        return {
            "overview": {
                "total_slow_query_patterns": total_queries,
                "total_executions_analyzed": total_executions,
                "average_query_duration_ms": round(avg_duration, 2),
                "collections_affected": collections_affected,
                "analysis_period": "Last 60 minutes",  # Default from config
            },
            "severity_breakdown": {
                "critical_queries": critical_queries,
                "high_impact_queries": high_impact_queries,
                "medium_impact_queries": total_queries
                - critical_queries
                - high_impact_queries,
            },
            "problem_areas": {
                "most_problematic_collection": most_problematic_collection,
                "most_problematic_operation": most_problematic_operation,
                "primary_issues": self._identify_primary_issues(slow_queries),
            },
            "key_findings": self._generate_key_findings(analysis_data),
        }

    def _identify_primary_issues(self, slow_queries: List[Dict[str, Any]]) -> List[str]:
        """Identify primary performance issues."""
        issues: List[str] = []

        # Check for collection scans
        collscan_count = len(
            [q for q in slow_queries if "COLLSCAN" in q.get("planSummary", "")]
        )
        if collscan_count > len(slow_queries) * 0.3:
            issues.append(f"Excessive collection scans ({collscan_count} patterns)")

        # Check for high examination ratios
        high_exam_ratio = len(
            [
                q
                for q in slow_queries
                if q.get("returned_docs", 1) > 0
                and q.get("examined_docs", 0) / q.get("returned_docs", 1) > 10
            ]
        )
        if high_exam_ratio > 0:
            high_ratio_count = high_exam_ratio
            message = (
                f"Inefficient queries with high examination ratios "
                f"({high_ratio_count} patterns)"
            )
            issues.append(message)

        # Check for missing indexes
        no_index_usage = len(
            [q for q in slow_queries if "IXSCAN" not in q.get("planSummary", "")]
        )
        if no_index_usage > len(slow_queries) * 0.4:
            issues.append(
                f"Poor index utilization ({no_index_usage} patterns "
                f"without index usage)"
            )

        # Check for slow aggregations
        slow_aggregations = len(
            [
                q
                for q in slow_queries
                if q.get("operation_type") == "aggregate"
                and q.get("duration_ms", 0) > 1000
            ]
        )
        if slow_aggregations > 0:
            issues.append(f"Slow aggregation pipelines ({slow_aggregations} patterns)")

        return issues[:5]  # Return top 5 issues

    def _generate_key_findings(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate key findings from the analysis."""
        findings: List[str] = []

        slow_queries = analysis_data.get("slow_queries", [])
        summary = analysis_data.get("summary", {})

        # Performance findings
        avg_duration = summary.get("avg_duration_ms", 0)
        if avg_duration > 1000:
            msg = (
                f"Average query duration of {avg_duration:.1f}ms indicates "
                f"significant performance issues"
            )
            findings.append(msg)
        elif avg_duration > 500:
            msg = (
                f"Average query duration of {avg_duration:.1f}ms suggests "
                f"room for optimization"
            )
            findings.append(msg)

        # Efficiency findings
        avg_efficiency = summary.get("avg_efficiency_score", 0)
        if avg_efficiency < 0.3:
            findings.append(
                "Low average efficiency score indicates poor query optimization"
            )

        # Frequency findings
        high_frequency_queries = [
            q for q in slow_queries if q.get("frequency", 0) > 100
        ]
        if high_frequency_queries:
            findings.append(
                f"{len(high_frequency_queries)} query patterns executed "
                f"frequently - high optimization priority"
            )

        # Operation type findings
        most_common_op = summary.get("most_common_operation", "")
        if most_common_op == "aggregate":
            findings.append(
                "Aggregation operations dominate slow queries - "
                "focus on pipeline optimization"
            )
        elif most_common_op == "find":
            findings.append(
                "Find operations are primary slow queries - "
                "focus on indexing strategy"
            )

        return findings

    def _create_appendix(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create appendix with additional technical details."""
        return {
            "methodology": {
                "data_collection": (
                    "MongoDB profiler integration with system.profile collection"
                ),
                "analysis_approach": (
                    "Pattern-based query grouping with statistical analysis"
                ),
                "scoring_algorithm": (
                    "Weighted combination of duration, efficiency, and impact metrics"
                ),
            },
            "glossary": {
                "Collection Scan (COLLSCAN)": (
                    "Query execution that examines every document in a collection"
                ),
                "Index Scan (IXSCAN)": (
                    "Query execution that uses an index to locate documents"
                ),
                "Efficiency Score": (
                    "Ratio-based metric measuring query selectivity and index usage"
                ),
                "Impact Score": (
                    "Weighted score combining duration, frequency, and resource usage"
                ),
                "Query Shape": (
                    "Normalized query pattern with literal values "
                    "replaced by placeholders"
                ),
            },
            "optimization_guide": self._create_optimization_guide(),
        }

    def _create_optimization_guide(self) -> Dict[str, Any]:
        """Create optimization guide section."""
        return {
            "indexing_strategy": [
                "Create indexes on frequently queried fields",
                "Use compound indexes for multi-field queries",
                "Consider index intersection for complex queries",
                "Monitor index usage with explain() plans",
            ],
            "query_optimization": [
                "Use specific field projections to reduce data transfer",
                "Optimize aggregation pipeline stage ordering",
                "Use appropriate query operators for data types",
                "Implement pagination for large result sets",
            ],
            "schema_design": [
                "Design schema to support common query patterns",
                "Consider denormalization for read-heavy workloads",
                "Use appropriate data types for query efficiency",
                "Implement proper field naming conventions",
            ],
            "monitoring": [
                "Enable database profiling for performance monitoring",
                "Set appropriate slow operation thresholds",
                "Regularly review query performance metrics",
                "Implement automated alerting for performance degradation",
            ],
        }

    def _create_markdown_content(self, analysis_data: Dict[str, Any]) -> str:
        """Create Markdown report content."""
        report = self._create_base_report(analysis_data)
        markdown_parts: List[str] = []

        # Header
        markdown_parts.append("# MongoDB Slow Query Analysis Report")
        markdown_parts.append(f"**Generated:** {report['metadata']['generated_at']}")
        markdown_parts.append(f"**Database:** {report['metadata']['database_name']}")
        markdown_parts.append("")

        # Executive Summary
        exec_summary = report["executive_summary"]
        markdown_parts.append("## Executive Summary")
        markdown_parts.append("")

        overview = exec_summary["overview"]
        markdown_parts.append("### Overview")
        markdown_parts.append(
            f"- **Total Slow Query Patterns:** {overview['total_slow_query_patterns']}"
        )
        markdown_parts.append(
            f"- **Total Executions Analyzed:** {overview['total_executions_analyzed']}"
        )
        markdown_parts.append(
            f"- **Average Query Duration:** {overview['average_query_duration_ms']}ms"
        )
        markdown_parts.append(
            f"- **Collections Affected:** {overview['collections_affected']}"
        )
        markdown_parts.append("")

        # Severity Breakdown
        severity = exec_summary["severity_breakdown"]
        markdown_parts.append("### Severity Breakdown")
        markdown_parts.append(f"- **Critical Queries:** {severity['critical_queries']}")
        markdown_parts.append(
            f"- **High Impact Queries:** {severity['high_impact_queries']}"
        )
        markdown_parts.append(
            f"- **Medium Impact Queries:** {severity['medium_impact_queries']}"
        )
        markdown_parts.append("")

        # Key Findings
        if exec_summary["key_findings"]:
            markdown_parts.append("### Key Findings")
            for finding in exec_summary["key_findings"]:
                markdown_parts.append(f"- {finding}")
            markdown_parts.append("")

        # Slow Queries Section
        if report["slow_queries"]:
            markdown_parts.append("## Slow Query Analysis")
            markdown_parts.append("")

            for i, query in enumerate(report["slow_queries"][:10], 1):  # Top 10
                markdown_parts.append(f"### Query Pattern #{i}")
                markdown_parts.append(
                    f"**Collection:** `{query['database']}.{query['collection']}`"
                )
                markdown_parts.append(f"**Operation:** {query['operation_type']}")
                markdown_parts.append(
                    f"**Average Duration:** {query['avg_duration_ms']:.1f}ms"
                )
                markdown_parts.append(f"**Frequency:** {query['frequency']} executions")
                markdown_parts.append(
                    f"**Impact Score:** {query['impact_score']:.1f}/100"
                )
                markdown_parts.append(
                    f"**Efficiency Score:** {query['efficiency_score']:.2f}/1.0"
                )

                if query["optimization_suggestions"]:
                    markdown_parts.append("**Optimization Suggestions:**")
                    for suggestion in query["optimization_suggestions"]:
                        markdown_parts.append(f"- {suggestion}")

                markdown_parts.append("")

        # Recommendations
        if report["recommendations"]:
            markdown_parts.append("## Recommendations")
            markdown_parts.append("")
            for i, recommendation in enumerate(report["recommendations"], 1):
                markdown_parts.append(f"{i}. {recommendation}")
            markdown_parts.append("")

        # Collection Analysis
        if report["collection_analyses"]:
            markdown_parts.append("## Collection Analysis")
            markdown_parts.append("")

            for collection in report["collection_analyses"]:
                name = collection["collection_name"]
                markdown_parts.append(f"### {name}")
                markdown_parts.append(
                    f"- **Document Count:** {collection.get('document_count', 'N/A'):,}"
                )
                markdown_parts.append(
                    f"- **Storage Size:** {collection.get('storage_size', 0):,} bytes"
                )
                markdown_parts.append(
                    f"- **Index Count:** {collection.get('index_count', 0)}"
                )
                markdown_parts.append(
                    f"- **Recent Slow Queries:** "
                    f"{collection.get('recent_slow_queries', 0)}"
                )

                if collection.get("optimization_recommendations"):
                    markdown_parts.append("**Recommendations:**")
                    for rec in collection["optimization_recommendations"]:
                        markdown_parts.append(f"- {rec}")

                markdown_parts.append("")

        return "\n".join(markdown_parts)

    def _create_html_content(self, analysis_data: Dict[str, Any]) -> str:
        """Create HTML report content with enhanced styling."""
        report = self._create_base_report(analysis_data)

        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MongoDB Slow Query Analysis Report</title>
    <style>
        body {{ font-family: sans-serif; margin: 0; padding: 20px;
               background-color: #f5f5f5; }}
        .container {{
            max-width: 1200px; margin: 0 auto; background: white;
            padding: 30px; border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50; border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .metadata {{
            background: #ecf0f1; padding: 15px; border-radius: 5px;
            margin-bottom: 20px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin: 20px 0;
        }}
        .summary-card {{
            background: #fff; border: 1px solid #ddd;
            border-radius: 5px; padding: 15px;
        }}
        .summary-card h4 {{ margin-top: 0; color: #2c3e50; }}
        .metric {{ font-size: 24px; font-weight: bold; color: #3498db; }}
        .query-card {{
            background: #f8f9fa; border: 1px solid #e9ecef;
            border-radius: 5px; padding: 20px; margin: 15px 0;
        }}
        .severity-critical {{ border-left: 5px solid #e74c3c; }}
        .severity-high {{ border-left: 5px solid #f39c12; }}
        .severity-medium {{ border-left: 5px solid #f1c40f; }}
        .suggestions {{
            background: #d5f4e6; border: 1px solid #27ae60;
            border-radius: 3px; padding: 10px; margin: 10px 0;
        }}
        .suggestions ul {{ margin: 5px 0; padding-left: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; font-weight: 600; }}
        .code {{ font-family: monospace; background: #f4f4f4;
                padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
        """

        content_parts: List[str] = []

        # Header
        content_parts.append("<h1>MongoDB Slow Query Analysis Report</h1>")
        content_parts.append("<div class='metadata'>")
        content_parts.append(
            f"<strong>Generated:</strong> {report['metadata']['generated_at']}<br>"
        )
        content_parts.append(
            f"<strong>Database:</strong> {report['metadata']['database_name']}<br>"
        )
        analysis_period = report["executive_summary"]["overview"]["analysis_period"]
        content_parts.append(f"<strong>Analysis Period:</strong> {analysis_period}")
        content_parts.append("</div>")

        # Executive Summary
        exec_summary = report["executive_summary"]
        content_parts.append("<h2>Executive Summary</h2>")

        content_parts.append("<div class='summary-grid'>")

        # Overview metrics
        overview = exec_summary["overview"]
        content_parts.append("<div class='summary-card'>")
        content_parts.append("<h4>Query Analysis</h4>")
        content_parts.append(
            f"<div class='metric'>{overview['total_slow_query_patterns']}</div>"
        )
        content_parts.append("Slow Query Patterns<br>")
        executions = overview["total_executions_analyzed"]
        content_parts.append(f"<div class='metric'>{executions:,}</div>")
        content_parts.append("Total Executions")
        content_parts.append("</div>")

        content_parts.append("<div class='summary-card'>")
        content_parts.append("<h4>Performance</h4>")
        avg_duration = overview["average_query_duration_ms"]
        content_parts.append(f"<div class='metric'>{avg_duration:.1f}ms</div>")
        content_parts.append("Average Duration<br>")
        content_parts.append(
            f"<div class='metric'>{overview['collections_affected']}</div>"
        )
        content_parts.append("Collections Affected")
        content_parts.append("</div>")

        # Severity breakdown
        severity = exec_summary["severity_breakdown"]
        content_parts.append("<div class='summary-card'>")
        content_parts.append("<h4>Severity Distribution</h4>")
        critical_span = (
            f"<span class='metric' style='color: #e74c3c;'>"
            f"{severity['critical_queries']}</span>"
        )
        content_parts.append(f"Critical: {critical_span}<br>")
        high_span = (
            f"<span class='metric' style='color: #f39c12;'>"
            f"{severity['high_impact_queries']}</span>"
        )
        content_parts.append(f"High: {high_span}<br>")
        medium_span = (
            f"<span class='metric' style='color: #2ecc71;'>"
            f"{severity['medium_impact_queries']}</span>"
        )
        content_parts.append(f"Medium: {medium_span}")
        content_parts.append("</div>")

        content_parts.append("</div>")  # End summary-grid

        # Key Findings
        if exec_summary["key_findings"]:
            content_parts.append("<h3>Key Findings</h3>")
            content_parts.append("<ul>")
            for finding in exec_summary["key_findings"]:
                content_parts.append(f"<li>{finding}</li>")
            content_parts.append("</ul>")

        # Slow Queries
        if report["slow_queries"]:
            content_parts.append("<h2>Top Slow Query Patterns</h2>")

            for i, query in enumerate(report["slow_queries"][:10], 1):
                # Determine severity class
                impact_score = query.get("impact_score", 0)
                if impact_score > 70:
                    severity_class = "severity-critical"
                elif impact_score > 50:
                    severity_class = "severity-high"
                else:
                    severity_class = "severity-medium"

                content_parts.append(f"<div class='query-card {severity_class}'>")
                content_parts.append(f"<h3>Query Pattern #{i}</h3>")

                content_parts.append("<table>")
                collection_cell = "<span class='code'>{}.{}</span>".format(
                    query["database"], query["collection"]
                )
                content_parts.append(
                    f"<tr><td><strong>Collection</strong></td>"
                    f"<td>{collection_cell}</td></tr>"
                )
                content_parts.append(
                    f"<tr><td><strong>Operation</strong></td>"
                    f"<td>{query['operation_type']}</td></tr>"
                )
                duration_cell = f"{query['avg_duration_ms']:.1f}ms"
                content_parts.append(
                    f"<tr><td><strong>Average Duration</strong></td>"
                    f"<td>{duration_cell}</td></tr>"
                )
                frequency_cell = f"{query['frequency']:,} executions"
                content_parts.append(
                    f"<tr><td><strong>Frequency</strong></td>"
                    f"<td>{frequency_cell}</td></tr>"
                )
                impact_cell = f"{query['impact_score']:.1f}/100"
                content_parts.append(
                    f"<tr><td><strong>Impact Score</strong></td>"
                    f"<td>{impact_cell}</td></tr>"
                )
                efficiency_cell = f"{query['efficiency_score']:.2f}/1.0"
                content_parts.append(
                    f"<tr><td><strong>Efficiency Score</strong></td>"
                    f"<td>{efficiency_cell}</td></tr>"
                )
                if query.get("planSummary"):
                    plan_cell = f"<span class='code'>{query['planSummary']}</span>"
                    content_parts.append(
                        f"<tr><td><strong>Execution Plan</strong></td>"
                        f"<td>{plan_cell}</td></tr>"
                    )
                content_parts.append("</table>")

                if query.get("optimization_suggestions"):
                    content_parts.append("<div class='suggestions'>")
                    content_parts.append(
                        "<strong>💡 Optimization Suggestions:</strong>"
                    )
                    content_parts.append("<ul>")
                    for suggestion in query["optimization_suggestions"]:
                        content_parts.append(f"<li>{suggestion}</li>")
                    content_parts.append("</ul>")
                    content_parts.append("</div>")

                content_parts.append("</div>")

        # Recommendations
        if report["recommendations"]:
            content_parts.append("<h2>Database-Level Recommendations</h2>")
            content_parts.append("<ol>")
            for recommendation in report["recommendations"]:
                content_parts.append(f"<li>{recommendation}</li>")
            content_parts.append("</ol>")

        return html_template.format(content="\n".join(content_parts))

    def generate_charts(
        self, analysis_data: Dict[str, Any], output_dir: str
    ) -> List[str]:
        """
        Generate performance charts and visualizations.

        Args:
            analysis_data: Complete analysis results
            output_dir: Directory to save chart files

        Returns:
            List of generated chart file paths
        """
        if not matplotlib_available:
            logger.warning("Matplotlib not available for chart generation")
            return []

        chart_files: List[str] = []
        slow_queries = analysis_data.get("slow_queries", [])

        if not slow_queries:
            logger.warning("No slow queries data available for chart generation")
            return chart_files

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            # Duration vs Frequency scatter plot
            chart_file = self._create_duration_frequency_chart(
                slow_queries, output_path
            )
            if chart_file:
                chart_files.append(chart_file)

            # Impact score distribution
            chart_file = self._create_impact_distribution_chart(
                slow_queries, output_path
            )
            if chart_file:
                chart_files.append(chart_file)

            # Collection performance comparison
            chart_file = self._create_collection_comparison_chart(
                slow_queries, output_path
            )
            if chart_file:
                chart_files.append(chart_file)

        except Exception as e:
            logger.error(f"Error generating charts: {e}")

        return chart_files

    def _create_duration_frequency_chart(
        self, slow_queries: List[Dict[str, Any]], output_path: Path
    ) -> Optional[str]:
        """Create duration vs frequency scatter plot."""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            durations = [q.get("avg_duration_ms", 0) for q in slow_queries]
            frequencies = [q.get("frequency", 0) for q in slow_queries]
            impact_scores = [q.get("impact_score", 0) for q in slow_queries]

            scatter = ax.scatter(
                durations, frequencies, c=impact_scores, cmap="YlOrRd", alpha=0.7, s=60
            )

            ax.set_xlabel("Average Duration (ms)")
            ax.set_ylabel("Execution Frequency")
            ax.set_title("Query Duration vs Frequency (colored by Impact Score)")

            plt.colorbar(scatter, label="Impact Score")
            plt.tight_layout()

            chart_path = output_path / "duration_frequency_scatter.png"
            plt.savefig(chart_path, dpi=300, bbox_inches="tight")
            plt.close()

            return str(chart_path)

        except Exception as e:
            logger.error(f"Error creating duration/frequency chart: {e}")
            return None

    def _create_impact_distribution_chart(
        self, slow_queries: List[Dict[str, Any]], output_path: Path
    ) -> Optional[str]:
        """Create impact score distribution histogram."""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            impact_scores = [q.get("impact_score", 0) for q in slow_queries]

            ax.hist(
                impact_scores, bins=20, alpha=0.7, color="steelblue", edgecolor="black"
            )
            ax.set_xlabel("Impact Score")
            ax.set_ylabel("Number of Query Patterns")
            ax.set_title("Distribution of Query Impact Scores")
            ax.grid(True, alpha=0.3)

            plt.tight_layout()

            chart_path = output_path / "impact_score_distribution.png"
            plt.savefig(chart_path, dpi=300, bbox_inches="tight")
            plt.close()

            return str(chart_path)

        except Exception as e:
            logger.error(f"Error creating impact distribution chart: {e}")
            return None

    def _create_collection_comparison_chart(
        self, slow_queries: List[Dict[str, Any]], output_path: Path
    ) -> Optional[str]:
        """Create collection performance comparison bar chart."""
        try:
            # Aggregate data by collection
            collection_data = {}
            for query in slow_queries:
                collection = query.get("collection", "unknown")
                if collection not in collection_data:
                    collection_data[collection] = {
                        "total_duration": 0,
                        "total_frequency": 0,
                        "query_count": 0,
                    }

                collection_data[collection]["total_duration"] += query.get(
                    "total_duration_ms", 0
                )
                collection_data[collection]["total_frequency"] += query.get(
                    "frequency", 0
                )
                collection_data[collection]["query_count"] += 1

            if len(collection_data) < 2:
                return None  # Need at least 2 collections for comparison

            # Sort by total duration
            sorted_collections = sorted(
                collection_data.items(),
                key=lambda x: x[1]["total_duration"],
                reverse=True,
            )[
                :10
            ]  # Top 10 collections

            collections = [item[0] for item in sorted_collections]
            durations = [item[1]["total_duration"] for item in sorted_collections]

            fig, ax = plt.subplots(figsize=(12, 6))

            bars = ax.bar(collections, durations, color="coral", alpha=0.7)
            ax.set_xlabel("Collection")
            ax.set_ylabel("Total Duration (ms)")
            ax.set_title("Total Query Duration by Collection")

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45, ha="right")

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{int(height):,}ms",
                    ha="center",
                    va="bottom",
                )

            plt.tight_layout()

            chart_path = output_path / "collection_performance_comparison.png"
            plt.savefig(chart_path, dpi=300, bbox_inches="tight")
            plt.close()

            return str(chart_path)

        except Exception as e:
            logger.error(f"Error creating collection comparison chart: {e}")
            return None
