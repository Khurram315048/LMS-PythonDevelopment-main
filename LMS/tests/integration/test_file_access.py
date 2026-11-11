import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.files.routes import router as files_router


@pytest.fixture
def file_client():
    app = FastAPI()
    app.include_router(files_router)
    with TestClient(app) as client:
        yield client


@pytest.mark.parametrize(
    "path",
    [
        "/files/submission/1",
        "/files/fyp/1",
        "/files/voucher/1",
    ],
)
def test_private_file_requires_authentication(file_client, path):
    response = file_client.get(path)
    assert response.status_code == 401


def test_private_file_rejects_invalid_token(file_client):
    response = file_client.get(
        "/files/fyp/1",
        cookies={"access_token": "not-a-valid-token"},
    )
    assert response.status_code == 401


def test_file_route_rejects_unknown_file_kind(file_client):
    response = file_client.get(
        "/files/unknown/1",
        cookies={"access_token": "not-a-valid-token"},
    )
    # FastAPI validates the Literal path parameter before route execution.
    assert response.status_code in (401, 422)