from openai import OpenAI
import os
import logging
from typing import Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM client"""

    api_key: Optional[str] = None
    model: str = "gpt-4o-mini"  # More cost-effective default
    temperature: float = 0.3
    max_tokens: int = 300
    timeout: int = 30


class LLMClient:
    """Client for interacting with OpenAI API"""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()

        # Get API key from config or environment
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass it in LLMConfig."
            )

        self.client = OpenAI(api_key=api_key, timeout=self.config.timeout)
        logger.info(f"Initialized LLM client with model: {self.config.model}")

    def generate_recommendations(
        self,
        query_text: str,
        avg_duration: float,
        frequency: int,
        max_duration: Optional[float] = None,
        impact_score: Optional[float] = None,
    ) -> str:
        """
        Uses GPT to analyze query and suggest optimizations

        Args:
            query_text: SQL query to analyze
            avg_duration: Average execution duration in ms
            frequency: Number of times query was executed
            max_duration: Maximum execution duration in ms
            impact_score: Calculated impact score

        Returns:
            Optimization recommendations as string
        """
        try:
            prompt = self._build_prompt(
                query_text, avg_duration, frequency, max_duration, impact_score
            )

            logger.debug(
                f"Requesting recommendations for query (avg: {avg_duration:.2f}ms)"
            )

            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a PostgreSQL performance optimization expert.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

            recommendation = response.choices[0].message.content
            logger.info("Successfully generated recommendations")
            return recommendation

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return f"Error generating recommendations: {str(e)}"

    def _build_prompt(
        self,
        query_text: str,
        avg_duration: float,
        frequency: int,
        max_duration: Optional[float],
        impact_score: Optional[float],
    ) -> str:
        """Builds the prompt for the LLM"""

        stats = [
            f"Average Duration: {avg_duration:.2f} ms",
            f"Execution Frequency: {frequency} times",
        ]

        if max_duration:
            stats.append(f"Max Duration: {max_duration:.2f} ms")

        if impact_score:
            stats.append(f"Impact Score: {impact_score:.2f}")

        stats_text = "\n".join(stats)

        prompt = f"""You are a PostgreSQL database performance expert.

Analyze this slow-running query:

Query: {query_text}

Statistics:
{stats_text}

Provide:
1. Most likely root cause of slowness
2. Specific, actionable optimization recommendation (e.g., add index, rewrite query)
3. Estimated performance impact (e.g., "30-50% faster")

Keep response concise and under 150 words."""

        return prompt

    def batch_generate_recommendations(self, queries: list[Dict]) -> list[str]:
        """
        Generate recommendations for multiple queries

        Args:
            queries: List of dicts with keys: query_text, avg_duration, frequency

        Returns:
            List of recommendation strings
        """
        recommendations = []

        for i, query_info in enumerate(queries):
            logger.info(f"Processing query {i + 1}/{len(queries)}")

            rec = self.generate_recommendations(
                query_text=query_info["query_text"],
                avg_duration=query_info["avg_duration"],
                frequency=query_info["frequency"],
                max_duration=query_info.get("max_duration"),
                impact_score=query_info.get("impact_score"),
            )
            recommendations.append(rec)

        return recommendations


# Backward compatibility - keep the original function
_default_client = None


def generate_recommendations(
    query_text: str, avg_duration: float, frequency: int
) -> str:
    """
    Legacy function for backward compatibility
    Uses GPT to analyze query and suggest optimizations
    """
    global _default_client

    if _default_client is None:
        _default_client = LLMClient()

    return _default_client.generate_recommendations(query_text, avg_duration, frequency)
