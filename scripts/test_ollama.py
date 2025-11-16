#!/usr/bin/env python3
"""
Test script to verify Ollama is working with Slow Query Doctor.

Usage:
    python scripts/test_ollama.py
    # or with uv:
    uv run python scripts/test_ollama.py
"""

import sys
import logging
from pathlib import Path

# Add the project root to sys.path before importing slowquerydoctor
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import slowquerydoctor modules
from slowquerydoctor.llm_client import LLMClient, LLMConfig  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_ollama_connection():
    """Test basic Ollama connection and model availability."""
    try:
        import ollama

        # Test direct ollama connection
        logger.info("Testing direct Ollama connection...")
        response = ollama.chat(
            model="arctic-text2sql-r1:7b",
            messages=[
                {"role": "user", "content": "Say 'Ollama is working' in one sentence."}
            ],
        )

        if hasattr(response, "message") and hasattr(response.message, "content"):
            logger.info(f"✅ Direct Ollama test: {response.message.content.strip()}")
        else:
            logger.info(f"✅ Direct Ollama test: {response}")

    except ImportError:
        logger.error("❌ Ollama package not installed. Run: pip install ollama")
        return False
    except Exception as e:
        logger.error(f"❌ Ollama connection failed: {e}")
        logger.error("Make sure Ollama is running: ollama serve")
        logger.error("And model is pulled: ollama pull arctic-text2sql-r1:7b")
        return False

    return True


def test_slow_query_doctor_ollama():
    """Test Slow Query Doctor's Ollama integration."""
    try:
        logger.info("Testing Slow Query Doctor Ollama integration...")

        config = LLMConfig(
            llm_provider="ollama", ollama_model="arctic-text2sql-r1:7b", max_tokens=100
        )

        client = LLMClient(config)

        # Test with a simple slow query
        test_query = (
            "SELECT * FROM users WHERE email LIKE '%@gmail.com' ORDER BY created_at"
        )

        recommendation = client.generate_recommendations(
            query_text=test_query, avg_duration=2500.0, frequency=25
        )

        if recommendation and "error" not in recommendation.lower():
            logger.info("✅ Slow Query Doctor + Ollama integration working!")
            logger.info(f"Sample recommendation: {recommendation[:100]}...")
            return True
        else:
            logger.error(f"❌ Integration test failed: {recommendation}")
            return False

    except Exception as e:
        logger.error(f"❌ Slow Query Doctor Ollama integration failed: {e}")
        return False


def main():
    """Run all Ollama tests."""
    logger.info("🔍 Testing Ollama setup for Slow Query Doctor...")

    # Test 1: Direct Ollama connection
    if not test_ollama_connection():
        logger.error("❌ Basic Ollama test failed. Check your setup.")
        return 1

    # Test 2: Slow Query Doctor integration
    if not test_slow_query_doctor_ollama():
        logger.error("❌ Slow Query Doctor integration test failed.")
        return 1

    logger.info("🎉 All tests passed! Ollama is ready for Slow Query Doctor.")
    logger.info("You can now run: python -m slowquerydoctor your_log_file.log")
    logger.info("Make sure your .slowquerydoctor.yml has: llm_provider: ollama")

    return 0


if __name__ == "__main__":
    sys.exit(main())
