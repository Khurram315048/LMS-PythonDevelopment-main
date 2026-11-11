import pytest

from core.exceptions import BusinessRuleError, ValidationError
from modules.teachers import service


def test_grade_thresholds():
    assert service.TeacherService._grade(85) == ("A", 4.0)
    assert service.TeacherService._grade(80) == ("A-", 3.7)
    assert service.TeacherService._grade(50) == ("C-", 1.7)
    assert service.TeacherService._grade(49) == ("F", 0.0)


def test_bulk_results_saves_all_students(monkeypatch):
    monkeypatch.setattr(
        service.TeacherModel, "is_section_owned_by_teacher",
        lambda section_id, teacher_id: True,
    )
    monkeypatch.setattr(
        service.TeacherModel, "get_attendance_meta",
        lambda section_id: {"course_id": 7, "semester": 3},
    )
    monkeypatch.setattr(
        service.TeacherModel, "get_grading_data",
        lambda course_id, section_id: [
            {"student_id": 11},
            {"student_id": 12},
        ],
    )

    saved = []
    monkeypatch.setattr(
        service.TeacherModel, "process_student_result",
        lambda *args: saved.append(args),
    )

    service.TeacherService.submit_bulk_results(
        teacher_id=4,
        section_id=9,
        form_data={
            "sessional_11": "18", "mids_11": "25", "final_11": "42",
            "sessional_12": "10", "mids_12": "20", "final_12": "30",
        },
    )

    assert [row[0] for row in saved] == [11, 12]


def test_bulk_results_rejects_unowned_section(monkeypatch):
    monkeypatch.setattr(
        service.TeacherModel, "is_section_owned_by_teacher",
        lambda section_id, teacher_id: False,
    )

    with pytest.raises(BusinessRuleError):
        service.TeacherService.submit_bulk_results(
            teacher_id=4,
            section_id=999,
            form_data={"sessional_11": "18"},
        )


def test_bulk_results_rejects_marks_out_of_range(monkeypatch):
    monkeypatch.setattr(
        service.TeacherModel, "is_section_owned_by_teacher",
        lambda section_id, teacher_id: True,
    )
    monkeypatch.setattr(
        service.TeacherModel, "get_attendance_meta",
        lambda section_id: {"course_id": 7, "semester": 3},
    )
    monkeypatch.setattr(
        service.TeacherModel, "get_grading_data",
        lambda course_id, section_id: [{"student_id": 11}],
    )

    with pytest.raises(BusinessRuleError):
        service.TeacherService.submit_bulk_results(
            teacher_id=4,
            section_id=9,
            form_data={
                "sessional_11": "21",
                "mids_11": "20",
                "final_11": "30",
            },
        )


def test_grade_submission_rejects_marks_above_total(monkeypatch):
    monkeypatch.setattr(
        service.TeacherModel, "is_section_owned_by_teacher",
        lambda section_id, teacher_id: True,
    )

    with pytest.raises(ValidationError):
        service.TeacherService.grade_submission(
            teacher_id=4,
            section_id=9,
            sub_id=12,
            marks=11,
            total=10,
            sub_type="assignment",
        )