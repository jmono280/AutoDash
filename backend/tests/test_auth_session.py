from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.core import dependencies
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.database import get_db
from app.routers import auth as auth_router
from app.services.auth_service import AuthService

EMAIL = "test.user@example.test"
PASSWORD = "test-password"
COOKIE = settings.REFRESH_COOKIE_NAME


class FakeUserRepo:
    def __init__(self):
        self.user = SimpleNamespace(
            email=EMAIL, hashed_password=hash_password(PASSWORD), is_active=True
        )

    async def get_by_email(self, db, email):
        return self.user if email == EMAIL else None


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(auth_router.router, prefix="/auth")
    repo = FakeUserRepo()

    async def no_db():
        yield None

    app.dependency_overrides[get_db] = no_db
    app.dependency_overrides[auth_router._service] = lambda: AuthService(repo=repo)
    return TestClient(app)


def _set_cookie(response) -> str:
    headers = [v for k, v in response.headers.multi_items() if k.lower() == "set-cookie"]
    assert len(headers) == 1, headers
    return headers[0]


def _login(client, remember_me):
    return client.post(
        "/auth/login", json={"email": EMAIL, "password": PASSWORD, "remember_me": remember_me}
    )


def test_login_with_remember_me_sets_persistent_httponly_cookie(client):
    res = _login(client, True)

    assert res.status_code == 200
    body = res.json()
    assert body["access_token"] and "refresh_token" not in body
    cookie = _set_cookie(res)
    assert cookie.startswith(f"{COOKIE}=")
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
    assert "Path=/" in cookie
    assert f"Max-Age={settings.REMEMBER_ME_EXPIRE_DAYS * 86400}" in cookie


def test_login_without_remember_me_sets_session_cookie(client):
    res = _login(client, False)

    assert res.status_code == 200
    cookie = _set_cookie(res)
    assert "HttpOnly" in cookie
    assert "Max-Age" not in cookie and "expires" not in cookie.lower()


def test_login_defaults_to_not_remembering(client):
    res = client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD})

    assert res.status_code == 200
    assert "Max-Age" not in _set_cookie(res)


def test_login_with_wrong_password_is_rejected_without_cookie(client):
    res = client.post("/auth/login", json={"email": EMAIL, "password": "nope"})

    assert res.status_code == 401
    assert "set-cookie" not in res.headers


@pytest.mark.parametrize("remember_me", [True, False])
def test_refresh_with_cookie_returns_access_token_and_keeps_persistence(client, remember_me):
    login_cookie = _set_cookie(_login(client, remember_me))
    token = login_cookie.split(";")[0].split("=", 1)[1]

    res = client.post("/auth/refresh", headers={"Cookie": f"{COOKIE}={token}"})

    assert res.status_code == 200
    assert res.json()["access_token"]
    rotated = _set_cookie(res)
    assert ("Max-Age" in rotated) is remember_me


def test_refresh_without_cookie_is_rejected(client):
    res = client.post("/auth/refresh")

    assert res.status_code == 401


def test_refresh_rejects_an_access_token(client):
    access = create_access_token({"sub": EMAIL})

    res = client.post("/auth/refresh", headers={"Cookie": f"{COOKIE}={access}"})

    assert res.status_code == 401


def test_refresh_ignores_token_in_body(client):
    refresh = create_refresh_token({"sub": EMAIL}, remember=True)

    res = client.post("/auth/refresh", json={"refresh_token": refresh})

    assert res.status_code == 401


def test_logout_clears_the_cookie(client):
    res = client.post("/auth/logout")

    assert res.status_code == 200
    cookie = _set_cookie(res)
    assert cookie.startswith(f'{COOKIE}=""') or cookie.startswith(f"{COOKIE}=;")
    assert "Max-Age=0" in cookie


class _FakeResult:
    def __init__(self, user):
        self._user = user

    def scalar_one_or_none(self):
        return self._user


class _FakeDb:
    async def execute(self, _stmt):
        return _FakeResult(SimpleNamespace(email=EMAIL, is_active=True))


@pytest.mark.anyio
async def test_current_user_accepts_access_token():
    user = await dependencies.get_current_user(create_access_token({"sub": EMAIL}), _FakeDb())

    assert user.email == EMAIL


@pytest.mark.anyio
async def test_current_user_rejects_refresh_token():
    refresh = create_refresh_token({"sub": EMAIL}, remember=True)

    with pytest.raises(HTTPException) as exc:
        await dependencies.get_current_user(refresh, _FakeDb())

    assert exc.value.status_code == 401
