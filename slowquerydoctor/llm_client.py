import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
try:
    import ollama
except ImportError:
    ollama = None

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM client"""

    api_key: Optional[str] = None
    llm_provider: str = "openai"  # 'openai' or 'ollama'
    openai_model: str = "gpt-4o-mini"
    ollama_model: str = "llama2"
    ollama_host: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 300
    timeout: int = 30


class LLMClient:
    """Client for interacting with OpenAI or Ollama API"""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.provider = self.config.llm_provider.lower()
        self._ollama_client = None

        if self.provider == "openai":
            if OpenAI is None:
                raise ImportError("openai package not installed")
            api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                    "or pass it in LLMConfig."
                )
            self.client = OpenAI(api_key=api_key, timeout=self.config.timeout)
            self.model = self.config.openai_model
            logger.info(f"Initialized OpenAI client with model: {self.model}")
        elif self.provider == "ollama":
            if ollama is None:
                raise ImportError("ollama package not installed")
            if self.config.ollama_host and hasattr(ollama, "Client"):
                try:
                    self._ollama_client = ollama.Client(host=self.config.ollama_host)
                    logger.info(
                        "Initialized Ollama client with custom host: %s",
                        self.config.ollama_host,
                    )
                except (
                    Exception
                ) as client_error:  # pragma: no cover - network dependent
                    logger.warning(
                        "Failed to initialize Ollama client with host %s (%s). Falling back to default host.",
                        self.config.ollama_host,
                        client_error,
                    )
                    self._ollama_client = None
            self.model = self.config.ollama_model
            logger.info(f"Initialized Ollama client with model: {self.model}")
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def generate_recommendations(
        self,
        query_text: str,
        avg_duration: float,
        frequency: int,
        max_duration: Optional[float] = None,
        impact_score: Optional[float] = None,
    ) -> str:
        """
        Uses LLM to analyze query and suggest optimizations
        """
        try:
            prompt = self._build_prompt(
                query_text, avg_duration, frequency, max_duration, impact_score
            )
            logger.debug(
                f"Requesting recommendations for query (avg: {avg_duration:.2f}ms)"
            )
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
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
                recommendation = response.choices[0].message.content or ""
                logger.info("Successfully generated recommendations (OpenAI)")
                return recommendation
            elif self.provider == "ollama":
                chat_target = self._ollama_client or ollama
                response = chat_target.chat(  # type: ignore[attr-defined]
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                )
                logger.debug(f"Ollama response type: {type(response)}")
                logger.debug(f"Ollama response: {response}")

                # Type-safe response parsing
                content: str = ""
                # Ollama Python SDK returns ChatResponse objects with .message.content attributes
                if hasattr(response, "message") and hasattr(
                    response.message, "content"
                ):
                    raw_content = response.message.content
                    logger.debug(f"Raw content (ChatResponse): {raw_content}")
                    if isinstance(raw_content, str):
                        content = raw_content.strip()
                # Fallback for dict-style responses (mocked tests)
                elif isinstance(response, dict):
                    message = response.get("message")  # type: ignore[union-attr]
                    logger.debug(f"Message (dict): {message}")
                    if isinstance(message, dict):
                        raw_content = message.get("content")  # type: ignore[union-attr]
                        logger.debug(f"Raw content (dict): {raw_content}")
                        if isinstance(raw_content, str):
                            content = raw_content.strip()

                if content:
                    logger.info(
                        f"Successfully generated Ollama recommendations ({len(content)} chars)"
                    )
                else:
                    logger.warning("Ollama returned empty content")

                return content
            else:  # pragma: no cover - defensive
                raise ValueError(f"Unhandled LLM provider: {self.provider}")
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

    def batch_generate_recommendations(
        self, queries: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate recommendations for multiple queries

        Args:
            queries: List of dicts with keys: query_text, avg_duration, frequency

        Returns:
            List of recommendation strings
        """
        recommendations: List[str] = []

        for i, query_info in enumerate(queries):
            logger.info(f"Processing query {i + 1}/{len(queries)}")

            rec = self.generate_recommendations(
                query_text=str(query_info.get("query_text", "")),
                avg_duration=float(query_info.get("avg_duration", 0)),
                frequency=int(query_info.get("frequency", 0)),
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
