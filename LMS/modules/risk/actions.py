from sqlalchemy import select, func, case

from db.models.orm import StudentCourse, Course, Attendance
from modules.risk.features import build_features

TARGET=75         


def _attendance_by_course(session,student_id):
    rows=session.execute(
        select(
            Course.course_name,
            func.count(Attendance.attendance_id),
            func.sum(case((Attendance.attendance_status=="Present", 1), else_=0)),
        )
        .select_from(StudentCourse)
        .join(Course, Course.course_id==StudentCourse.course_id)
        .join(Attendance, Attendance.student_course_id==StudentCourse.student_course_id)
        .where(
            StudentCourse.student_id==student_id,
            StudentCourse.is_deleted==False,
            Attendance.is_deleted==False,
        )
        .group_by(Course.course_id,Course.course_name)
    ).all()
    return [(name, int(total), int(present or 0)) for name, total, present in rows if total]


def build_actions(session,student_id)->list[str]:
    actions=[]

    courses=_attendance_by_course(session,student_id)
    courses.sort(key=lambda c: c[2] / c[1])
    for name, total, present in courses:
        need=3 * total - 4 * present        
        if need <= 0:
            continue

        pct=present * 100 / total
        if need <= 30:
            actions.append(
                f"{name}: attend the next {need} classes in a row to reach {TARGET}% "
                f"attendance (now {pct:.0f}%).")
        else:
            actions.append(
                f"{name}: attendance is {pct:.0f}%. Please talk to your teacher about how to recover it.")

    
    f=build_features(session, [student_id]).get(student_id)
    if f:
        if f["fee_due_count"]:
            actions.append(
                f"You have {f['fee_due_count']} unpaid fee(s). Please contact the fee office.")
        if f["fail_count"]:
            actions.append(
                f"You have {f['fail_count']} failed subject(s). Check your retake options early.")
        if f["prev_gpa"] is not None and f["prev_gpa"] < 2.0:
            actions.append(
                f"Your last semester GPA was {f['prev_gpa']}. Meet your advisor to make a study plan.")
        if f["assignment_avg"] is not None and f["assignment_avg"] < 50:
            actions.append(
                f"Your assignments and quizzes average is {f['assignment_avg']:.0f}%. "
                "Submit pending work and ask your teacher for feedback.")

    return actions[:5]