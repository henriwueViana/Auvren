
from unittest.mock import MagicMock, patch

from app.core.database import get_db


def test_get_db_returns_session():
    mock_session = MagicMock()

    with patch("app.core.database.SessionLocal", return_value=mock_session):
        generator = get_db()
        db = next(generator)

        assert db is mock_session

        generator.close()

        mock_session.close.assert_called_once()


def test_get_db_closes_session_after_exception():
    mock_session = MagicMock()

    with patch("app.core.database.SessionLocal", return_value=mock_session):
        generator = get_db()
        next(generator)

        try:
            generator.throw(RuntimeError("Erro de teste"))
        except RuntimeError:
            pass

        mock_session.close.assert_called_once()
