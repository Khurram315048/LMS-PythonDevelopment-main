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
    # Keep chatbot excluded from the test application.
    from modules.admin.routes import router as admin_router
    from modules.auth.refresh import router as refresh_router
    from modules.auth.routes import router as auth_router
    from modules.files.routes import router as files_router
    from modules.notifications.websocket_routes import router as websocket_router
    from modules.students.routes import router as student_router
    from modules.teachers.routes import router as teacher_router

    test_app = FastAPI()
    test_app.add_middleware(
        SessionMiddleware,
        secret_key=os.environ["SECRET_KEY"],
        https_only=False,
        same_site="lax",
    )

    test_app.include_router(auth_router)  # Add this
    test_app.include_router(refresh_router)
    test_app.include_router(student_router)
    test_app.include_router(teacher_router)
    test_app.include_router(admin_router)
    test_app.include_router(files_router)
    test_app.include_router(websocket_router)

    return test_app


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client



