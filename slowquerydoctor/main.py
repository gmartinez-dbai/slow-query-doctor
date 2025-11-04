"""
Main entry point for Slow Query Doctor CLI
"""

import argparse
import sys
import logging
from pathlib import Path

from .parser import parse_postgres_log
from .analyzer import run_slow_query_analysis
from .llm_client import LLMClient, LLMConfig
from .report_generator import ReportGenerator


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='Slow Query Doctor - AI-powered PostgreSQL slow query analyzer'
    )

    parser.add_argument(
        'log_file',
        type=str,
        help='Path to PostgreSQL slow query log file'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='reports/report.md',
        help='Output report path (default: reports/report.md)'
    )

    parser.add_argument(
        '--top-n',
        type=int,
        default=5,
        help='Number of top slow queries to analyze (default: 5)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose (debug) output for troubleshooting and progress tracking.'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        setup_logging()

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Analyzing {args.log_file}")

        # Parse logs
        df = parse_postgres_log(args.log_file)

        if df.empty:
            logger.warning("No slow queries found")
            return 0

        # Analyze queries
        try:
            top_queries, summary = run_slow_query_analysis(df, top_n=args.top_n)
        except ValueError as analysis_error:
            logger.warning(str(analysis_error))
            return 0

        if top_queries.empty:
            logger.warning("No slow queries met the analysis criteria")
            return 0

        # Generate AI recommendations
        logger.info("Generating recommendations...")
        config = LLMConfig()
        llm_client = LLMClient(config)

        queries_to_analyze = []
        for row in top_queries.itertuples(index=False):
            queries_to_analyze.append(
                {
                    'query_text': str(row.example_query),
                    'avg_duration': float(row.avg_duration),
                    'frequency': int(row.frequency)
                }
            )

        recommendations = llm_client.batch_generate_recommendations(queries_to_analyze)

        # Generate report
        report_gen = ReportGenerator(llm_client)
        report = report_gen.generate_markdown_report(
            top_queries, summary, recommendations
        )

        # Write output
        output_path = Path(args.output)
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


if __name__ == '__main__':
    sys.exit(main())
