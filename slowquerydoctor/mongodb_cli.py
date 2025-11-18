#!/usr/bin/env python3
"""
MongoDB Slow Query Doctor CLI

Command-line interface for MongoDB slow query detection and analysis.
"""

import argparse
import json
import logging
import sys
from typing import List, Optional

from slowquerydoctor.mongodb_analyzer import MongoDBSlowQueryDetector
from slowquerydoctor.mongodb_config import (
    MongoDBConfig,
    load_mongodb_config,
    create_sample_config_file,
)
from slowquerydoctor.mongodb_report_generator import MongoDBReportGenerator


def setup_logging(log_level: str, log_file: Optional[str] = None) -> None:
    """Set up logging configuration."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))  # type: ignore[arg-type]

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def analyze_command(args: argparse.Namespace) -> int:
    """Execute MongoDB slow query analysis."""
    try:
        # Load configuration
        config = load_mongodb_config(args.config)

        # Setup logging
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
            generate_reports(all_reports, args.output, args.format, config)

        logger.info("Analysis completed successfully")
        return 0

    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def generate_reports(
    reports_data: dict, output_path: str, formats: List[str], config: MongoDBConfig
) -> None:
    """Generate reports in specified formats."""
    logger = logging.getLogger(__name__)

    for database_name, report_data in reports_data.items():
        generator = MongoDBReportGenerator(config)

        for fmt in formats:
            if fmt == "json":
                filename = f"{output_path}/{database_name}_analysis.json"
                success = generator.generate_json_report(report_data, filename)
            elif fmt == "markdown":
                filename = f"{output_path}/{database_name}_analysis.md"
                success = generator.generate_markdown_report(report_data, filename)
            elif fmt == "html":
                filename = f"{output_path}/{database_name}_analysis.html"
                success = generator.generate_html_report(report_data, filename)
            else:
                logger.warning(f"Unsupported format: {fmt}")
                continue

            if success:
                print(f"Generated {fmt.upper()} report: {filename}")
            else:
                logger.error(
                    f"Failed to generate {fmt.upper()} report for {database_name}"
                )


def config_command(args: argparse.Namespace) -> int:
    """Handle configuration management commands."""
    try:
        if args.config_action == "create":
            if create_sample_config_file(args.output or "mongodb_config.yml"):
                output_path = args.output or "mongodb_config.yml"
                print(f"Sample configuration created: {output_path}")
                return 0
            else:
                print("Failed to create sample configuration", file=sys.stderr)
                return 1

        elif args.config_action == "validate":
            config = load_mongodb_config(args.config)
            issues = config.validate()

            if not issues:
                print("✅ Configuration is valid")
                return 0
            else:
                print("❌ Configuration validation failed:")
                for issue in issues:
                    print(f"  - {issue}")
                return 1

        elif args.config_action == "show":
            config = load_mongodb_config(args.config)
            config_dict = config.to_dict()

            if args.format and "json" in args.format:
                print(json.dumps(config_dict, indent=2, default=str))
            else:
                # Pretty print configuration
                print("=== MongoDB Configuration ===")
                print(f"Connection: {config.get_effective_connection_string()}")
                print(f"Databases: {config.databases_to_monitor}")
                if config.thresholds:
                    print(f"Slow Threshold: {config.thresholds.slow_threshold_ms}ms")
                    critical_ms = config.thresholds.critical_threshold_ms
                    print(f"Critical Threshold: {critical_ms}ms")
                if config.profiling:
                    print(f"Profiling Level: {config.profiling.profiling_level}")
                print(f"Log Level: {config.log_level}")

            return 0

        # Default case if no action matches
        print("Unknown configuration action", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1


def monitor_command(args: argparse.Namespace) -> int:
    """Execute continuous monitoring mode."""
    try:
        config = load_mongodb_config(args.config)
        setup_logging(config.log_level, config.log_file)
        logger = logging.getLogger(__name__)

        logger.info("Starting continuous monitoring mode")

        # Create detector
        connection_string = config.get_effective_connection_string()
        detector = MongoDBSlowQueryDetector(connection_string, config.thresholds)

        if not detector.initialize():
            logger.error("Failed to initialize MongoDB detector")
            return 1

        # Enable profiling
        databases = config.databases_to_monitor or [args.database]
        if not databases:
            logger.error("No databases specified for monitoring")
            return 1

        if not detector.start_monitoring(databases):
            logger.error("Failed to enable profiling")
            return 1

        logger.info(f"Monitoring enabled for databases: {databases}")

        # Monitoring loop
        import time

        interval = args.interval * 60  # Convert to seconds

        try:
            while True:
                logger.info("Running periodic analysis...")

                for database_name in databases:
                    try:
                        slow_queries = detector.detect_slow_queries(
                            database_name, time_window_minutes=args.interval
                        )

                        if slow_queries:
                            logger.warning(
                                f"Found {len(slow_queries)} slow query patterns "
                                f"in {database_name}"
                            )

                            # Print critical queries
                            critical_queries = [
                                q for q in slow_queries if q.impact_score > 70
                            ]

                            if critical_queries:
                                print(f"\n🚨 CRITICAL SLOW QUERIES in {database_name}:")
                                for query in critical_queries[:3]:
                                    op = query.operation_type
                                    col = query.collection
                                    print(f"  - {op} on {col}")
                                    duration = query.avg_duration_ms
                                    print(f"    Duration: {duration:.1f}ms")
                                    print(f"    Frequency: {query.frequency}")
                                    print(f"    Impact: {query.impact_score:.1f}/100")
                        else:
                            logger.info(f"No slow queries detected in {database_name}")

                    except Exception as e:
                        logger.error(f"Error analyzing {database_name}: {e}")

                # Wait for next interval
                logger.info(f"Waiting {args.interval} minutes until next analysis...")
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            return 0

    except Exception as e:
        print(f"Monitoring error: {e}", file=sys.stderr)
        return 1


def test_connection_command(args: argparse.Namespace) -> int:
    """Test MongoDB connection."""
    try:
        config = load_mongodb_config(args.config)
        setup_logging("INFO")

        connection_string = config.get_effective_connection_string()
        detector = MongoDBSlowQueryDetector(connection_string, config.thresholds)

        print("Testing MongoDB connection...")
        if detector.initialize():
            print("✅ Connection successful")

            # Test profiling capabilities
            if config.databases_to_monitor:
                print(f"Testing profiling on: {config.databases_to_monitor[0]}")
                if detector.profiler.enable_profiling(
                    config.databases_to_monitor[0], level=0
                ):
                    print("✅ Profiling test successful")
                else:
                    print("❌ Profiling test failed")

            return 0
        else:
            print("❌ Connection failed")
            return 1

    except Exception as e:
        print(f"Connection test error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    desc = "MongoDB Slow Query Doctor - Detect and analyze slow MongoDB queries"
    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create sample configuration
  %(prog)s config create --output my_config.yml

  # Analyze with custom configuration
  %(prog)s analyze --config my_config.yml --database myapp

  # Generate HTML report
  %(prog)s analyze --database myapp --output ./reports --format html

  # Start continuous monitoring
  %(prog)s monitor --config my_config.yml --interval 10
  # Test connection
  %(prog)s test-connection --config my_config.yml
        """,
    )

    # Global options
    parser.add_argument(
        "--config", "-c", default=None, help="Configuration file path (YAML format)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze slow queries in MongoDB database"
    )
    analyze_parser.add_argument("--database", "-d", help="Database name to analyze")
    analyze_parser.add_argument("--output", "-o", help="Output directory for reports")
    analyze_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "markdown", "html"],
        nargs="+",
        default=["json"],
        help="Report format(s) to generate",
    )
    analyze_parser.add_argument(
        "--enable-profiling",
        action="store_true",
        help="Enable MongoDB profiling before analysis",
    )
    analyze_parser.add_argument(
        "--skip-collection-analysis",
        action="store_true",
        help="Skip detailed collection-level analysis",
    )

    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_parser.add_argument(
        "config_action",
        choices=["create", "validate", "show"],
        help="Configuration action to perform",
    )
    config_parser.add_argument("--output", "-o", help="Output file for create action")
    config_parser.add_argument(
        "--format",
        "-f",
        choices=["yaml", "json"],
        nargs="+",
        default=["yaml"],
        help="Output format for show action",
    )

    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Continuous monitoring mode")
    monitor_parser.add_argument("--database", "-d", help="Database name to monitor")
    monitor_parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=5,
        help="Analysis interval in minutes (default: 5)",
    )

    # Test connection command
    subparsers.add_parser(
        "test-connection", help="Test MongoDB connection and profiling"
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == "analyze":
        return analyze_command(args)
    elif args.command == "config":
        return config_command(args)
    elif args.command == "monitor":
        return monitor_command(args)
    elif args.command == "test-connection":
        return test_connection_command(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
