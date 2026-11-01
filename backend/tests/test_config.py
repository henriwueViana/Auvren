
import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_accepts_hs256():
    settings = Settings(
        DATABASE_URL="sqlite:///./test.db",
        JWT_SECRET_KEY="a" * 64,
        JWT_ALGORITHM="HS256",
        GEMINI_API_KEY="test-api-key",
    )

    assert settings.JWT_ALGORITHM == "HS256"


def test_settings_rejects_unsupported_jwt_algorithm():
    with pytest.raises(
        ValidationError,
        match="Somente HS256 é permitido.",
    ):
        Settings(
            DATABASE_URL="sqlite:///./test.db",
            JWT_SECRET_KEY="a" * 64,
            JWT_ALGORITHM="HS512",
            GEMINI_API_KEY="test-api-key",
        )
