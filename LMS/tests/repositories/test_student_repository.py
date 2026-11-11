import os

import pytest


pytestmark = pytest.mark.skipif(
    not os.getenv("LMS_TEST_DATABASE_URL"),
    reason="Set up an isolated LMS test database before repository tests.",
)


def test_student_repository_suite_requires_test_database():
    # Add fixture-backed repository tests here once the test database,
    # schema setup, and cleanup strategy are configured.
    assert os.environ["LMS_TEST_DATABASE_URL"]