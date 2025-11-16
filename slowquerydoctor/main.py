"""
Main entry point for Slow Query Doctor CLI
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .parser import parse_postgres_log, load_config
from .analyzer import run_slow_query_analysis
from .llm_client import LLMClient, LLMConfig
from .report_generator import ReportGenerator

# MongoDB imports
from .mongodb_analyzer import MongoDBSlowQueryDetector
from .mongodb_config import load_mongodb_config
from .mongodb_report_generator import MongoDBReportGenerator


def postgresql_command(args: argparse.Namespace) -> int:
    """Execute PostgreSQL slow query analysis."""
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        setup_logging(
            args.log_level if hasattr(args, "log_level") else "INFO",
            args.log_file if hasattr(args, "log_file") else None,
        )

    logger = logging.getLogger(__name__)

    user_config = load_config()
    log_format = user_config.get("log_format") or "plain"
    configured_top_n = int(user_config.get("top_n") or args.top_n)
    configured_output = user_config.get("output") or args.output

    llm_defaults = LLMConfig()
    llm_config = LLMConfig(
        api_key=user_config.get("openai_api_key", llm_defaults.api_key),
        llm_provider=user_config.get("llm_provider", llm_defaults.llm_provider),
        openai_model=user_config.get("openai_model", llm_defaults.openai_model),
        ollama_model=user_config.get("ollama_model", llm_defaults.ollama_model),
        ollama_host=user_config.get("ollama_host", llm_defaults.ollama_host),
        temperature=float(user_config.get("llm_temperature", llm_defaults.temperature)),
        max_tokens=int(user_config.get("max_tokens", llm_defaults.max_tokens)),
        timeout=int(user_config.get("llm_timeout", llm_defaults.timeout)),
    )

    try:
        logger.info(f"Analyzing {args.log_file}")

        # Parse logs
        df = parse_postgres_log(args.log_file, log_format=log_format)

        if df.empty:
            logger.warning("No slow queries found")
            return 0

        # Analyze queries
        try:
            result = run_slow_query_analysis(df, top_n=configured_top_n)
        except ValueError as analysis_error:
            logger.warning(str(analysis_error))
            return 0

        # Type narrowing for DataFrame path
        if isinstance(result, tuple):
            top_queries, summary = result
            if len(top_queries) == 0:
                logger.warning("No slow queries met the analysis criteria")
                return 0
        else:
            logger.error("Unexpected return type from analysis")
            return 1

        # Generate AI recommendations
        logger.info("Generating recommendations...")
        llm_client = LLMClient(llm_config)

        queries_to_analyze: List[Dict[str, Any]] = []
        for row in top_queries.itertuples(index=False):
            queries_to_analyze.append(
                {
                    "query_text": str(row.example_query),
                    "avg_duration": float(row.avg_duration),
                    "frequency": int(row.frequency),
                }
            )

        recommendations = llm_client.batch_generate_recommendations(queries_to_analyze)

        # Generate report
        report_gen = ReportGenerator(llm_client)
        report = report_gen.generate_markdown_report(
            top_queries, summary, recommendations
        )

        # Write output
        output_path = Path(configured_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report)

        print(f"✅ Report saved to: {output_path}")
        logger.info("Analysis complete!")
        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


def mongodb_command(args: argparse.Namespace) -> int:
    """Execute MongoDB slow query analysis."""
    try:
        # Load configuration
        config = load_mongodb_config(args.config)

        # Setup logging
        if args.verbose:
            setup_logging("DEBUG", config.log_file)
        else:
            setup_logging(config.log_level, config.log_file)

        logger = logging.getLogger(__name__)

        logger.info("Starting MongoDB slow query analysis")
        logger.info(f"Target databases: {config.databases_to_monitor}")

        # Create detector
        connection_string = config.get_effective_connection_string()
        detector = MongoDBSlowQueryDetector(connection_string, config.thresholds)

        # Initialize detector
        if not detector.initialize():
            logger.error("Failed to initialize MongoDB detector")
            return 1

        # Start monitoring if requested
        if args.enable_profiling and config.databases_to_monitor:
            logger.info("Enabling profiling on target databases")
            if not detector.start_monitoring(config.databases_to_monitor):
                logger.warning("Failed to enable profiling on some databases")

        # Analyze each database
        all_reports = {}
        for database_name in config.databases_to_monitor or [args.database]:
            if not database_name:
                logger.error("No database specified for analysis")
                return 1

            logger.info(f"Analyzing database: {database_name}")

            # Generate comprehensive report
            report = detector.generate_comprehensive_report(
                database_name,
                include_collection_analysis=not args.skip_collection_analysis,
            )

            all_reports[database_name] = report

            # Print summary to console
            summary = report.get("summary", {})
            print(f"\n=== Analysis Summary for {database_name} ===")
            print(f"Slow Query Patterns: {summary.get('total_slow_queries', 0)}")
            print(f"Total Executions: {summary.get('total_executions', 0):,}")
            print(f"Average Duration: {summary.get('avg_duration_ms', 0):.1f}ms")
            print(f"Collections Affected: {summary.get('collections_affected', 0)}")
            print(
                f"Most Common Operation: {summary.get('most_common_operation', 'N/A')}"
            )

            # Show top recommendations
            recommendations = report.get("recommendations", [])
            if recommendations:
                print("\nTop Recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"{i}. {rec}")

        # Generate reports if output specified
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)

            report_gen = MongoDBReportGenerator(config)
            for database_name, report in all_reports.items():

                # Generate requested formats
                for format_type in args.format:
                    if format_type == "html":
                        html_path = output_dir / f"{database_name}_report.html"
                        if report_gen.generate_html_report(report, str(html_path)):
                            print(f"✅ HTML report saved to: {html_path}")
                        else:
                            print("❌ Failed to generate")
                            print(f"HTML report for {database_name}")

                    elif format_type == "markdown":
                        md_path = output_dir / f"{database_name}_report.md"
                        if report_gen.generate_markdown_report(report, str(md_path)):
                            print(f"✅ Markdown report saved to: {md_path}")
                        else:
                            print("❌ Failed to generate")
                            print(f"Markdown report for {database_name}")

                    elif format_type == "json":
                        json_path = output_dir / f"{database_name}_report.json"
                        if report_gen.generate_json_report(report, str(json_path)):
                            print(f"✅ JSON report saved to: {json_path}")
                        else:
                            print("❌ Failed to generate JSON")
                            print(f"JSON report for {database_name}")

        return 0

    except Exception as e:
        logging.getLogger(__name__).error(f"MongoDB analysis error: {e}")
        return 1


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Configure logging"""
    log_level = getattr(logging, level.upper(), logging.INFO)

    handlers: List[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def main() -> int:
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Slow Query Doctor - AI-powered database slow query analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze PostgreSQL log file
  %(prog)s postgresql /path/to/slow.log

  # Analyze MongoDB database
  %(prog)s mongodb --database myapp --config mongodb_config.yml

  # Generate HTML report for MongoDB
  %(prog)s mongodb --database myapp --output ./reports --format html
        """,
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) output for troubleshooting and progress tracking.",
    )

    # Create subparsers for different database types
    subparsers = parser.add_subparsers(
        dest="database_type", help="Database type to analyze"
    )

    # PostgreSQL subcommand
    pg_parser = subparsers.add_parser(
        "postgresql",
        aliases=["pg", "postgres"],
        help="Analyze PostgreSQL slow query logs",
    )
    pg_parser.add_argument(
        "log_file",
        type=str,
        help="Path to PostgreSQL slow query log file",
    )
    pg_parser.add_argument(
        "--output",
        type=str,
        default="reports/report.md",
        help="Output report path (default: reports/report.md)",
    )
    pg_parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top slow queries to analyze (default: 5)",
    )

    # MongoDB subcommand
    mongo_parser = subparsers.add_parser(
        "mongodb", aliases=["mongo"], help="Analyze MongoDB slow queries"
    )
    mongo_parser.add_argument("--database", "-d", help="Database name to analyze")
    mongo_parser.add_argument(
        "--config", "-c", default=None, help="Configuration file path (YAML format)"
    )
    mongo_parser.add_argument("--output", "-o", help="Output directory for reports")
    mongo_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "markdown", "html"],
        nargs="+",
        default=["json"],
        help="Report format(s) to generate",
    )
    mongo_parser.add_argument(
        "--enable-profiling",
        action="store_true",
        help="Enable MongoDB profiling before analysis",
    )
    mongo_parser.add_argument(
        "--skip-collection-analysis",
        action="store_true",
        help="Skip detailed collection-level analysis",
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle case where no subcommand is provided - show help
    if not args.database_type:
        parser.print_help()
        return 1

    # Dispatch to appropriate handler
    if args.database_type in ["postgresql", "pg", "postgres"]:
        return postgresql_command(args)
    elif args.database_type in ["mongodb", "mongo"]:
        return mongodb_command(args)
    else:
        print(f"Unknown database type: {args.database_type}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
