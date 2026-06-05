from unittest.mock import MagicMock, patch
from src.generators.llm_client import GroqClient


class TestGroqClient:
    def test_generate_documentation_returns_content(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "# Docs\n\nGenerated content."
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        llm = GroqClient(api_key="fake-key")
        llm.client = mock_client

        result = llm.generate_documentation("Write docs")
        assert result == "# Docs\n\nGenerated content."
        mock_client.chat.completions.create.assert_called_once()

    def test_generate_uses_correct_model(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "ok"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        llm = GroqClient(api_key="fake-key", model="mixtral-8x7b-32768")
        llm.client = mock_client
        llm.generate_documentation("test")

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "mixtral-8x7b-32768"

    def test_generate_returns_empty_on_empty_response(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = None
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        llm = GroqClient(api_key="fake-key")
        llm.client = mock_client

        result = llm.generate_documentation("test")
        assert result == ""
