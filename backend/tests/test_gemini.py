
import json
from unittest.mock import patch, MagicMock

import pytest

from app.integrations.gemini import analyze_ticket
from app.core.config import settings


VALID_RESPONSE = {
    "category": "access",
    "priority": "high",
    "justification": "O usuário não consegue acessar o sistema.",
}


@patch("app.integrations.gemini.client.models.generate_content")
def test_analyze_ticket_returns_valid_json(mock_generate):
    mock_response = MagicMock()
    mock_response.text = json.dumps(VALID_RESPONSE)
    mock_generate.return_value = mock_response

    result = analyze_ticket(
        "Erro de acesso",
        "Não consigo entrar no sistema.",
    )

    assert result == VALID_RESPONSE
    mock_generate.assert_called_once()


@patch("app.integrations.gemini.client.models.generate_content")
def test_analyze_ticket_raises_error_when_response_is_empty(mock_generate):
    mock_response = MagicMock()
    mock_response.text = None
    mock_generate.return_value = mock_response

    with pytest.raises(
        ValueError,
        match="O Gemini retornou uma resposta vazia.",
    ):
        analyze_ticket(
            "Erro de acesso",
            "Não consigo entrar no sistema.",
        )


@patch("app.integrations.gemini.client.models.generate_content")
def test_analyze_ticket_raises_error_when_json_is_invalid(mock_generate):
    mock_response = MagicMock()
    mock_response.text = "{json inválido"
    mock_generate.return_value = mock_response

    with pytest.raises(json.JSONDecodeError):
        analyze_ticket(
            "Erro de acesso",
            "Não consigo entrar no sistema.",
        )


@patch("app.integrations.gemini.client.models.generate_content")
def test_analyze_ticket_propagates_api_error(mock_generate):
    mock_generate.side_effect = RuntimeError("Erro de conexão com o Gemini")

    with pytest.raises(
        RuntimeError,
        match="Erro de conexão com o Gemini",
    ):
        analyze_ticket(
            "Erro de acesso",
            "Não consigo entrar no sistema.",
        )


@patch("app.integrations.gemini.client.models.generate_content")
def test_analyze_ticket_uses_expected_configuration(mock_generate):
    mock_response = MagicMock()
    mock_response.text = json.dumps(VALID_RESPONSE)
    mock_generate.return_value = mock_response

    analyze_ticket(
        "Erro de acesso",
        "Não consigo entrar no sistema.",
    )

    kwargs = mock_generate.call_args.kwargs

    assert kwargs["model"] == settings.GEMINI_MODEL
    assert "Título: Erro de acesso" in kwargs["contents"]
    assert "Descrição: Não consigo entrar no sistema." in kwargs["contents"]
    assert kwargs["config"].response_mime_type == "application/json"
    assert kwargs["config"].temperature == 0.2
