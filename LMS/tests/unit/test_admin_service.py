import pytest

from core.exceptions import BusinessRuleError, ValidationError
from modules.admin import service


def test_promotion_uses_pass_result(monkeypatch):
    monkeypatch.setattr(
        service.StudentModel,
        "get_result_by_id",
        lambda student_id: {"result_status": "Pass"},
    )

    promoted = []
    monkeypatch.setattr(
        service.StudentModel,
        "promote",
        lambda student_id: promoted.append(student_id),
    )

    service.AdminService.promote_student_to_next_semester(22)

    assert promoted == [22]


def test_promotion_rejects_fail_result(monkeypatch):
    monkeypatch.setattr(
        service.StudentModel,
        "get_result_by_id",
        lambda student_id: {"result_status": "Fail"},
    )

    promoted = []
    monkeypatch.setattr(
        service.StudentModel,
        "promote",
        lambda student_id: promoted.append(student_id),
    )

    with pytest.raises(BusinessRuleError):
        service.AdminService.promote_student_to_next_semester(22)

    assert promoted == []


def test_promotion_rejects_missing_result(monkeypatch):
    monkeypatch.setattr(
        service.StudentModel, "get_result_by_id", lambda student_id: None
    )

    with pytest.raises(BusinessRuleError):
        service.AdminService.promote_student_to_next_semester(22)


def test_enrollment_rejects_missing_section():
    with pytest.raises(ValidationError):
        service.AdminService.enroll_student_in_course(
            student_id=22,
            course_id=7,
            section_id=None,
        )