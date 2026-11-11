import pytest

from core.exceptions import BusinessRuleError
from modules.students import service


def test_fyp_requires_semester_seven_or_later(monkeypatch):
    monkeypatch.setattr(
        service.StudentModel,
        "get_current_semester",
        lambda student_id: 6,
    )

    with pytest.raises(BusinessRuleError):
        service.StudentService.check_fyp_semester(student_id=20)


def test_fyp_is_available_from_semester_seven(monkeypatch):
    monkeypatch.setattr(
        service.StudentModel,
        "get_current_semester",
        lambda student_id: 7,
    )

    service.StudentService.check_fyp_semester(student_id=20)


def test_summer_registration_accepts_open_status(monkeypatch):
    monkeypatch.setattr(
        service.StudentModel,
        "get_latest_summer_semester",
        lambda: {
            "summer_semesters_id": 5,
            "status": "Open",
        },
    )

    calls = []
    monkeypatch.setattr(
        service.StudentModel,
        "add_summer_subject",
        lambda student_id, subject_id, summer_id: calls.append(
            (student_id, subject_id, summer_id)
        ),
    )

    service.StudentService.handle_summer_registration(
        student_id=20,
        subject_id=101,
    )

    assert calls == [(20, 101, 5)]