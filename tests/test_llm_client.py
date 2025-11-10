"""Tests for LLM client functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from slowquerydoctor.llm_client import LLMClient, LLMConfig


class TestLLMClientOpenAI:
    """Test OpenAI provider functionality."""

    @patch("slowquerydoctor.llm_client.OpenAI")
    def test_openai_initialization(self, mock_openai_class):
        """Test OpenAI client initializes correctly."""
        config = LLMConfig(
            api_key="test-key",
            llm_provider="openai",
            openai_model="gpt-4o-mini",
        )
        client = LLMClient(config)

        assert client.provider == "openai"
        assert client.model == "gpt-4o-mini"
        mock_openai_class.assert_called_once()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "env-key"})
    @patch("slowquerydoctor.llm_client.OpenAI")
    def test_openai_env_api_key(self, mock_openai_class):
        """Test OpenAI uses environment variable for API key."""
        config = LLMConfig(llm_provider="openai")
        client = LLMClient(config)

        assert client.provider == "openai"
        mock_openai_class.assert_called_once()

    @patch("slowquerydoctor.llm_client.OpenAI", None)
    def test_openai_import_error(self):
        """Test error when OpenAI package not installed."""
        config = LLMConfig(llm_provider="openai", api_key="test")
        with pytest.raises(ImportError, match="openai package not installed"):
            LLMClient(config)

    @patch("slowquerydoctor.llm_client.OpenAI")
    def test_openai_generate_recommendations(self, mock_openai_class):
        """Test OpenAI recommendation generation."""
        # Setup mock response
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Add index on user_id"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        config = LLMConfig(
            api_key="test-key", llm_provider="openai", openai_model="gpt-4"
        )
        client = LLMClient(config)

        result = client.generate_recommendations(
            query_text="SELECT * FROM users WHERE id = 1",
            avg_duration=500.0,
            frequency=100,
        )

        assert result == "Add index on user_id"
        mock_client.chat.completions.create.assert_called_once()

    @patch("slowquerydoctor.llm_client.OpenAI")
    def test_openai_empty_response(self, mock_openai_class):
        """Test OpenAI handles None content gracefully."""
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = None
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        config = LLMConfig(api_key="test-key", llm_provider="openai")
        client = LLMClient(config)

        result = client.generate_recommendations(
            query_text="SELECT 1", avg_duration=10.0, frequency=1
        )

        assert result == ""


class TestLLMClientOllama:
    """Test Ollama provider functionality."""

    @patch("slowquerydoctor.llm_client.ollama")
    def test_ollama_initialization(self, mock_ollama):
        """Test Ollama client initializes correctly."""
        config = LLMConfig(llm_provider="ollama", ollama_model="llama2")
        client = LLMClient(config)

        assert client.provider == "ollama"
        assert client.model == "llama2"

    @patch("slowquerydoctor.llm_client.ollama", None)
    def test_ollama_import_error(self):
        """Test error when Ollama package not installed."""
        config = LLMConfig(llm_provider="ollama")
        with pytest.raises(ImportError, match="ollama package not installed"):
            LLMClient(config)

    @patch("slowquerydoctor.llm_client.ollama")
    def test_ollama_generate_recommendations(self, mock_ollama):
        """Test Ollama recommendation generation."""
        mock_ollama.chat.return_value = {
            "message": {"content": "Create index on email column"}
        }

        config = LLMConfig(llm_provider="ollama", ollama_model="llama2")
        client = LLMClient(config)

        result = client.generate_recommendations(
            query_text="SELECT * FROM users WHERE email = 'test@example.com'",
            avg_duration=1200.0,
            frequency=50,
        )

        assert result == "Create index on email column"
        mock_ollama.chat.assert_called_once()

    @patch("slowquerydoctor.llm_client.ollama")
    def test_ollama_custom_host(self, mock_ollama):
        """Test Ollama with custom host configuration."""
        mock_client = MagicMock()
        mock_ollama.Client.return_value = mock_client
        mock_client.chat.return_value = {
            "message": {"content": "Use prepared statements"}
        }

        config = LLMConfig(
            llm_provider="ollama",
            ollama_model="llama2",
            ollama_host="http://custom-host:11434",
        )
        client = LLMClient(config)

        result = client.generate_recommendations(
            query_text="SELECT * FROM orders", avg_duration=300.0, frequency=10
        )

        assert result == "Use prepared statements"
        mock_ollama.Client.assert_called_once_with(host="http://custom-host:11434")

    @patch("slowquerydoctor.llm_client.ollama")
    def test_ollama_malformed_response(self, mock_ollama):
        """Test Ollama handles malformed response gracefully."""
        mock_ollama.chat.return_value = {"no_message": "here"}

        config = LLMConfig(llm_provider="ollama")
        client = LLMClient(config)

        result = client.generate_recommendations(
            query_text="SELECT 1", avg_duration=10.0, frequency=1
        )

        assert result == ""

    @patch("slowquerydoctor.llm_client.ollama")
    def test_ollama_empty_content(self, mock_ollama):
        """Test Ollama handles empty content."""
        mock_ollama.chat.return_value = {"message": {"content": ""}}

        config = LLMConfig(llm_provider="ollama")
        client = LLMClient(config)

        result = client.generate_recommendations(
            query_text="SELECT 1", avg_duration=10.0, frequency=1
        )

        assert result == ""


class TestLLMClientCommon:
    """Test common LLM client functionality."""

    def test_invalid_provider(self):
        """Test error on invalid provider."""
        config = LLMConfig(llm_provider="unknown")
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            LLMClient(config)

    @patch("slowquerydoctor.llm_client.OpenAI")
    def test_batch_generate_recommendations(self, mock_openai_class):
        """Test batch recommendation generation."""
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Optimize query"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        config = LLMConfig(api_key="test-key", llm_provider="openai")
        client = LLMClient(config)

        queries = [
            {
                "query_text": "SELECT * FROM users",
                "avg_duration": 100.0,
                "frequency": 10,
            },
            {
                "query_text": "SELECT * FROM orders",
                "avg_duration": 200.0,
                "frequency": 5,
            },
        ]

        results = client.batch_generate_recommendations(queries)

        assert len(results) == 2
        assert all(r == "Optimize query" for r in results)
        assert mock_client.chat.completions.create.call_count == 2

    @patch("slowquerydoctor.llm_client.OpenAI")
    def test_error_handling(self, mock_openai_class):
        """Test error handling during recommendation generation."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client

        config = LLMConfig(api_key="test-key", llm_provider="openai")
        client = LLMClient(config)

        result = client.generate_recommendations(
            query_text="SELECT 1", avg_duration=10.0, frequency=1
        )

        assert "Error generating recommendations" in result
        assert "API Error" in result
