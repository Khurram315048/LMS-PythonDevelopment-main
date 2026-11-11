import os

# Set this before importing application modules that load core.config.
os.environ.setdefault(
    "SECRET_KEY",
    "test-only-secret-key-that-is-at-least-32-characters",
)
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("COOKIE_SECURE", "false")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware


@pytest.fixture
def app():
    # Include application routers except the chatbot router.
    from modules.admin.routes import router as admin_router
    from modules.students.routes import router as student_router
    from modules.teachers.routes import router as teacher_router

    test_app = FastAPI()
    test_app.add_middleware(
        SessionMiddleware,
        secret_key=os.environ["SECRET_KEY"],
        https_only=False,
    )

    test_app.include_router(student_router)
    test_app.include_router(teacher_router)
    test_app.include_router(admin_router)

    return test_app


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client