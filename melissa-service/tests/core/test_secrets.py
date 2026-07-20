import pytest
import os
from unittest.mock import patch
from app.core.secrets import get_secret, set_secret

def test_get_secret_from_keyring():
    with patch("keyring.get_password", return_value="fake_key"):
        assert get_secret("OPENAI_API_KEY") == "fake_key"

def test_get_secret_from_env():
    with patch("keyring.get_password", return_value=None):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env_key"}):
            assert get_secret("OPENAI_API_KEY") == "env_key"

def test_get_secret_not_found():
    with patch("keyring.get_password", return_value=None):
        with patch.dict(os.environ, {}, clear=True):
            assert get_secret("OPENAI_API_KEY") is None

def test_set_secret():
    with patch("keyring.set_password") as mock_set:
        set_secret("TEST_KEY", "test_value")
        mock_set.assert_called_once_with("melissa-service", "TEST_KEY", "test_value")
