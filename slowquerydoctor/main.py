"""
Main entry point for Slow Query Doctor CLI
"""

import argparse
import sys
import logging
from pathlib import Path

from .parser import parse_postgres_log
from .analyzer import analyze_slow_queries
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

    args = parser.parse_args()
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
        top_queries, summary = analyze_slow_queries(df, top_n=args.top_n)

        # Generate AI recommendations
        logger.info("Generating recommendations...")
        config = LLMConfig()
        llm_client = LLMClient(config)

        queries_to_analyze = [
            {
                'query_text': row['example_query'],
                'avg_duration': row['avg_duration'],
                'frequency': row['frequency']
            }
            for _, row in top_queries.iterrows()
        ]

        recommendations = llm_client.batch_generate_recommendations(queries_to_analyze)

        # Generate report
        report_gen = ReportGenerator()
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
