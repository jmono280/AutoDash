import os

# Settings require these at import time; tests never reach the real services.
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

import pytest  # noqa: E402


@pytest.fixture
def anyio_backend():
    return "asyncio"
