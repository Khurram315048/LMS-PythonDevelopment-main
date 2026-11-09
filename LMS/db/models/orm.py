from sqlalchemy import (
    Column,Integer,SmallInteger,String,Text,Boolean,Date,Time,DateTime,
    TIMESTAMP,Numeric,Enum,ForeignKey,UniqueConstraint,CheckConstraint,
    Index,text,func,
)
from sqlalchemy.dialects.mysql import YEAR, TINYINT
from sqlalchemy.orm import declarative_base,relationship

Base=declarative_base()

OPTS={
    "mysql_engine":"InnoDB",
    "mysql_charset":"utf8mb4",
    "mysql_collate":"utf8mb4_general_ci",
}
OPTS_0900={
    "mysql_engine":"InnoDB",
    "mysql_charset":"utf8mb4",
    "mysql_collate":"utf8mb4_0900_ai_ci",
}



class UserRole(Base):
    __tablename__="users_role"
    __table_args__=(OPTS,)

    role_id=Column(Integer, primary_key=True, autoincrement=True)
    role_type=Column(String(100), nullable=False, unique=True)
    is_deleted=Column(Boolean, nullable=False, default=False, server_default=text("0"))

    users=relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (OPTS,)

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("users_role.role_id"), nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    role = relationship("UserRole", back_populates="users")
    admin = relationship("Admin", back_populates="user", uselist=False, passive_deletes=True)
    student = relationship("Student", back_populates="user", uselist=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False)
    complaints = relationship("ComplaintSuggestion", back_populates="user")
    notifications_sent = relationship("Notification", back_populates="sender", passive_deletes=True)
    reset_otps = relationship("ResetOtp", back_populates="user", passive_deletes=True)


class Admin(Base):
    __tablename__ = "admins"
    __table_args__ = (OPTS,)

    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    contact = Column(String(100))
    email = Column(String(100), unique=True)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    user = relationship("User", back_populates="admin")


class ResetOtp(Base):
    __tablename__ = "reset_otps"
    __table_args__ = (OPTS_0900,)

    otp_id = Column(Integer, primary_key=True, autoincrement=True)
    otp_num = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    otp_expire = Column(DateTime)
    otp_attempts = Column(Integer, default=0, server_default=text("0"))
    otp_used = Column(Integer, default=0, server_default=text("0"))
    create_at = Column(DateTime, server_default=func.current_timestamp())

    user = relationship("User", back_populates="reset_otps")



class Program(Base):
    __tablename__ = "programs"
    __table_args__ = (OPTS,)

    program_id = Column(Integer, primary_key=True, autoincrement=True)
    program_name = Column(String(100), nullable=False, unique=True)
    program_coordinator = Column(String(100), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    courses = relationship("Course", back_populates="program")
    sections = relationship("Section", back_populates="program")
    students = relationship("Student", back_populates="program")
    exams = relationship("Exam", back_populates="program")
    student_fees = relationship("StudentFee", back_populates="program")
    pdf_configurations = relationship("PdfConfiguration", back_populates="program")


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (OPTS,)

    course_id = Column(Integer, primary_key=True, autoincrement=True)
    course_name = Column(String(100), nullable=False)
    course_type = Column(String(50), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.program_id"), nullable=False, index=True)
    credit_hours = Column(Integer)
    no_of_lectures = Column(Integer)
    assignments_enabled = Column(Boolean, default=True, server_default=text("1"))
    quizzes_enabled = Column(Boolean, default=True, server_default=text("1"))
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    program = relationship("Program", back_populates="courses")
    sections = relationship("Section", back_populates="course")
    schedules = relationship("CourseSchedule", back_populates="course")
    teacher_courses = relationship("TeacherCourse", back_populates="course")
    student_courses = relationship("StudentCourse", back_populates="course")
    attendance_logs = relationship("CourseAttendanceLog", back_populates="course")
    submissions = relationship("StudentSubmission", back_populates="course")
    notifications = relationship("Notification", back_populates="related_course", passive_deletes=True)
    improvements = relationship("StudentImprovement", back_populates="course")
    fail_subjects = relationship("StudentFailSubject", back_populates="course")
    summer_registrations = relationship("SummerRegistration", back_populates="course", passive_deletes=True)


class Section(Base):
    __tablename__ = "sections"
    __table_args__ = (OPTS,)

    section_id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False, index=True)
    section_name = Column(String(50), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.program_id"), nullable=False, index=True)
    semester = Column(Integer, nullable=False)
    assignments_enabled = Column(Boolean, default=True, server_default=text("1"))
    quizzes_enabled = Column(Boolean, default=True, server_default=text("1"))
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    course = relationship("Course", back_populates="sections")
    program = relationship("Program", back_populates="sections")
    schedules = relationship("CourseSchedule", back_populates="section")
    student_sections = relationship("StudentSection", back_populates="section")
    submissions = relationship("StudentSubmission", back_populates="section")


class CourseSchedule(Base):
    __tablename__ = "course_schedule"
    __table_args__ = (OPTS,)

    course_schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    day_of_week = Column(Enum("Monday", "Tuesday", "Wednesday", "Thursday", "Friday"))
    start_time = Column(Time)
    end_time = Column(Time)
    location = Column(String(100))
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False, index=True)
    section_id = Column(Integer, ForeignKey("sections.section_id"), index=True)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    course = relationship("Course", back_populates="schedules")
    section = relationship("Section", back_populates="schedules")
    attendance_records = relationship("Attendance", back_populates="course_schedule")
    attendance_logs = relationship("CourseAttendanceLog", back_populates="course_schedule")



class Student(Base):
    __tablename__ = "students"
    __table_args__ = (OPTS,)

    student_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    contact = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    last_qualification = Column(String(100))
    program_id = Column(Integer, ForeignKey("programs.program_id"), nullable=False, index=True)
    admission_session = Column(String(50))
    admission_date = Column(Date)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    current_semester = Column(Integer, default=1, server_default=text("1"))

    user = relationship("User", back_populates="student")
    program = relationship("Program", back_populates="students")
    student_courses = relationship("StudentCourse", back_populates="student")
    student_sections = relationship("StudentSection", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")
    submissions = relationship("StudentSubmission", back_populates="student")
    fyp_groups = relationship("FypGroup", back_populates="student")
    fees = relationship("StudentFee", back_populates="student")
    results = relationship("StudentResult", back_populates="student")
    improvements = relationship("StudentImprovement", back_populates="student")
    fail_subjects = relationship("StudentFailSubject", back_populates="student")
    freeze_requests = relationship("SemesterFreezeStudent", back_populates="student")
    summer_registrations = relationship("SummerRegistration", back_populates="student", passive_deletes=True)


class StudentCourse(Base):
    __tablename__ = "student_course"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="unique_student_course"),
        OPTS,
    )

    student_course_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    student = relationship("Student", back_populates="student_courses")
    course = relationship("Course", back_populates="student_courses")
    attendance_records = relationship("Attendance", back_populates="student_course")
    result_mark = relationship("StudentResultMarks", back_populates="student_course", uselist=False)


class StudentSection(Base):
    __tablename__ = "student_section"
    __table_args__ = (
        UniqueConstraint("student_id", "section_id", name="unique_student_section"),
        OPTS,
    )

    student_section_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    section_id = Column(Integer, ForeignKey("sections.section_id"), nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    student = relationship("Student", back_populates="student_sections")
    section = relationship("Section", back_populates="student_sections")


class StudentFailSubject(Base):
    __tablename__ = "student_fail_subjects"
    __table_args__ = (OPTS,)

    student_fail_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False, index=True)
    status = Column(Enum("Pending", "Approved", "Rejected"), nullable=False,
                    default="Pending", server_default="Pending")
    create_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    student = relationship("Student", back_populates="fail_subjects")
    course = relationship("Course", back_populates="fail_subjects")


class StudentImprovement(Base):
    __tablename__ = "student_improvement"
  
    __table_args__ = (
        UniqueConstraint("student_id",name="unique_student_improvement"),
        OPTS,
    )

    improvement_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False, index=True)
    status = Column(Enum("Pending", "Approved", "Rejected"), nullable=False,
                    default="Pending", server_default="Pending")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    student = relationship("Student", back_populates="improvements")
    course = relationship("Course", back_populates="improvements")


class SemesterFreezeStudent(Base):
    __tablename__ = "semester_freeze_students"
    __table_args__ = (OPTS,)

    freeze_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    semester = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum("Pending", "Approved", "Rejected"), default="Pending", server_default="Pending")
    applied_date = Column(DateTime, server_default=func.current_timestamp())
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    student = relationship("Student", back_populates="freeze_requests")



class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("student_course_id", "course_schedule_id", "attendance_date", name="uq_att"),
        Index("idx_attendance_date", "attendance_date"),
        OPTS,
    )

    attendance_id = Column(Integer, primary_key=True, autoincrement=True)
    student_course_id = Column(Integer, ForeignKey("student_course.student_course_id"), nullable=False, index=True)
    course_schedule_id = Column(Integer, ForeignKey("course_schedule.course_schedule_id"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False)
    attendance_status = Column(Enum("Present", "Absent"), default="Absent", server_default="Absent")
    student_id = Column(Integer, ForeignKey("students.student_id"), index=True)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    student_course = relationship("StudentCourse", back_populates="attendance_records")
    course_schedule = relationship("CourseSchedule", back_populates="attendance_records")
    student = relationship("Student", back_populates="attendance_records")


class CourseAttendanceLog(Base):
    __tablename__ = "course_attendance_log"
    __table_args__ = (OPTS,)

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False, index=True)
    course_schedule_id = Column(Integer, ForeignKey("course_schedule.course_schedule_id"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False)
    total_students = Column(Integer, default=0, server_default=text("0"))
    total_present = Column(Integer, default=0, server_default=text("0"))
    total_absent = Column(Integer, default=0, server_default=text("0"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    semester = Column(Integer)

    teacher = relationship("Teacher", back_populates="attendance_logs")
    course = relationship("Course", back_populates="attendance_logs")
    course_schedule = relationship("CourseSchedule", back_populates="attendance_logs")



class Teacher(Base):
    __tablename__ = "teachers"
    __table_args__ = (OPTS,)

    teacher_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    contact_num = Column(String(100), nullable=False)
    qualification = Column(String(100))
    joining_date = Column(Date)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    user = relationship("User", back_populates="teacher")
    teacher_courses = relationship("TeacherCourse", back_populates="teacher")
    fyp_groups = relationship("FypGroup", back_populates="teacher")
    attendance_logs = relationship("CourseAttendanceLog", back_populates="teacher")
    salaries = relationship("TeacherSalary", back_populates="teacher")


class TeacherCourse(Base):
    __tablename__ = "teacher_course"
    __table_args__ = (OPTS,)

    teacher_course_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    teacher = relationship("Teacher", back_populates="teacher_courses")
    course = relationship("Course", back_populates="teacher_courses")


class TeacherSalary(Base):
    __tablename__ = "teacher_salary"
    __table_args__ = (OPTS,)

    salary_id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"), nullable=False, index=True)
    month = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)
    basic_salary = Column(Numeric(10, 2), nullable=False)
    bonus = Column(Numeric(10, 2), default=0, server_default=text("0.00"))
    deductions = Column(Numeric(10, 2), default=0, server_default=text("0.00"))
    status = Column(Enum("Pending", "Paid"), default="Pending", server_default="Pending")
    is_deleted = Column(TINYINT, default=0, server_default=text("0"))  # tinyint (not tinyint(1)) in DB

    teacher = relationship("Teacher", back_populates="salaries")



class FypGroup(Base):
    __tablename__ = "fyp_groups"
    __table_args__ = (OPTS,)

    fyp_id = Column(Integer, primary_key=True, autoincrement=True)
    project_title = Column(Text, nullable=False)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"), index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    status = Column(Enum("In Progress", "Approved", "Completed", "Rejected"), nullable=False,
                    default="In Progress", server_default="In Progress")
    progress = Column(Integer, default=0, server_default=text("0"))
    last_submission = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    teacher = relationship("Teacher", back_populates="fyp_groups")
    student = relationship("Student", back_populates="fyp_groups")
    messages = relationship("FypMessage", back_populates="fyp", passive_deletes=True)


class FypMessage(Base):
    __tablename__ = "fyp_messages"
    __table_args__ = (OPTS,)

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    fyp_id = Column(Integer, ForeignKey("fyp_groups.fyp_id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id = Column(Integer, nullable=False)
    student_id = Column(Integer, nullable=False)
    sender_role = Column(Enum("teacher", "student"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    fyp = relationship("FypGroup", back_populates="messages")



class Exam(Base):
    __tablename__ = "exams"
    __table_args__ = (
        CheckConstraint("exam_semester between 1 and 8", name="exams_chk_1"),
        OPTS,
    )

    exam_id = Column(Integer, primary_key=True, autoincrement=True)
    program_id = Column(Integer, ForeignKey("programs.program_id"), nullable=False, index=True)
    exam_category = Column(Enum("Mid", "Final"), nullable=False)
    exam_date = Column(Date, nullable=False)
    exam_semester = Column(TINYINT(unsigned=True), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    location = Column(String(100))
    mode = Column(Enum("Online", "On Campus"), nullable=False)
    status = Column(Enum("Concluded", "Ongoing"), nullable=False,
                    default="Ongoing", server_default="Ongoing")
    is_deleted = Column(Integer, nullable=False, default=0, server_default=text("0"))  # int in DB

    program = relationship("Program", back_populates="exams")


class StudentResult(Base):
    __tablename__ = "student_results"
    __table_args__ = (
        UniqueConstraint("student_id", "student_semester", name="unique_student_semester"),
        CheckConstraint("overall_gpa between 0.00 and 4.00", name="student_results_chk_1"),
        Index("idx_student_semester", "student_id", "student_semester"),
        OPTS,
    )

    student_result_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    student_semester = Column(Integer, nullable=False)
    overall_gpa = Column(Numeric(3, 2), nullable=False)
    result_status = Column(Enum("Pass", "Fail"), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    student = relationship("Student", back_populates="results")
    marks = relationship("StudentResultMarks", back_populates="student_result")


class StudentResultMarks(Base):
    __tablename__ = "student_result_marks"
    
    __table_args__ = (
        UniqueConstraint("student_course_id", name="uq_scm"),
        OPTS,
    )

    marks_id = Column(Integer, primary_key=True, autoincrement=True)
    student_course_id = Column(Integer, ForeignKey("student_course.student_course_id"), nullable=False)
    student_result_id = Column(Integer, ForeignKey("student_results.student_result_id"), nullable=False, index=True)
    total_marks = Column(Integer, default=0, server_default=text("0"))
    student_grade = Column(String(10), nullable=False)
    status = Column(String(50), nullable=False)
    student_semester = Column(Integer)
    sessional_marks = Column(Integer, default=0, server_default=text("0"))
    mid_marks = Column(Integer, default=0, server_default=text("0"))
    final_marks = Column(Integer, default=0, server_default=text("0"))
    subject_gpa = Column(Numeric(3, 2), default=0, server_default=text("0.00"))
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    student_course = relationship("StudentCourse", back_populates="result_mark")
    student_result = relationship("StudentResult", back_populates="marks")



class StudentSubmission(Base):
    __tablename__ = "student_submissions"
    __table_args__ = (OPTS,)

    submission_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), index=True)
    section_id = Column(Integer, ForeignKey("sections.section_id"), index=True)
    file_path = Column(String(255))
    submission_type = Column(Enum("assignment", "quiz"))
    upload_date = Column(DateTime, server_default=func.current_timestamp())
    submission_status = Column(Enum("Best", "Average", "Worst", "Pending"),
                               default="Pending", server_default="Pending")
    marks = Column(Integer)
    total_marks = Column(Integer)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    student = relationship("Student", back_populates="submissions")
    course = relationship("Course", back_populates="submissions")
    section = relationship("Section", back_populates="submissions")


class StudentFee(Base):
    __tablename__ = "student_fees"
    __table_args__ = (OPTS,)

    student_fees_id = Column(Integer, primary_key=True, autoincrement=True)
    fee_amount = Column(Numeric(10, 2), nullable=False)
    fee_status = Column(Enum("paid", "due"), default="due", server_default="due")
    update_date = Column(TIMESTAMP, nullable=False,
                         server_default=text("CURRENT_TIMESTAMP"),
                         onupdate=func.current_timestamp())  
    voucher_front_pic = Column(String(255))
    voucher_back_pic = Column(String(255))
    program_id = Column(Integer, ForeignKey("programs.program_id"), nullable=False, index=True)
    fee_month = Column(String(20))
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    program = relationship("Program", back_populates="student_fees")
    student = relationship("Student", back_populates="fees")



class Semester(Base):
    __tablename__ = "semester"
    __table_args__ = (OPTS,)

    semester_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    year = Column(YEAR, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    summer_semesters = relationship("SummerSemester", back_populates="previous_semester", passive_deletes=True)


class SummerSemester(Base):
    __tablename__ = "summer_semesters"
    __table_args__ = (OPTS,)

    summer_semesters_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    year = Column(YEAR)
    start_date = Column(Date)
    end_date = Column(Date)
    previous_semester_id = Column(
        Integer,
        ForeignKey("semester.semester_id", ondelete="SET NULL", onupdate="CASCADE"),
        index=True,
    )
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    status = Column(Enum("Open", "Closed"), nullable=False, default="Open", server_default="Open")
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    previous_semester = relationship("Semester", back_populates="summer_semesters")
    registrations = relationship("SummerRegistration", back_populates="summer_semester", passive_deletes=True)


class SummerRegistration(Base):
    __tablename__ = "summer_registration"
    __table_args__ = (OPTS,)

    registration_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE", onupdate="CASCADE"),
                        nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id", ondelete="CASCADE", onupdate="CASCADE"),
                       nullable=False, index=True)
    summer_semesters_id = Column(
        Integer,
        ForeignKey("summer_semesters.summer_semesters_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False, index=True,
    )
    registration_date = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    student = relationship("Student", back_populates="summer_registrations")
    course = relationship("Course", back_populates="summer_registrations")
    summer_semester = relationship("SummerSemester", back_populates="registrations")



class ComplaintSuggestion(Base):
    __tablename__ = "complaint_suggestion"
    __table_args__ = (OPTS,)

    complt_sugst_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100))
    description = Column(Text)
    image_name = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    is_status = Column(Enum("Pending", "Solved", "Rejected"), nullable=False,
                       default="Pending", server_default="Pending")
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    user = relationship("User", back_populates="complaints")


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (OPTS,)

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    sender_role = Column(Enum("student", "teacher", "admin"), nullable=False)
    receiver_id = Column(Integer)
    receiver_role = Column(Enum("student", "teacher", "admin"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    related_course_id = Column(Integer, ForeignKey("courses.course_id", ondelete="SET NULL"), index=True)
    status = Column(Enum("Pending", "Resolved", "Rejected"), default="Pending", server_default="Pending")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))

    sender = relationship("User", back_populates="notifications_sent")
    related_course = relationship("Course", back_populates="notifications")


class PdfConfiguration(Base):
    __tablename__ = "pdf_configurations"
    __table_args__ = (OPTS_0900,)

    pdf_id = Column(Integer, primary_key=True, autoincrement=True)
    pdf_name = Column(String(100), nullable=False)
    pdf_type = Column(Enum("exam", "fee"))
    pdf_status = Column(Enum("active", "not_active"), default="active", server_default="active")
    total_no = Column(Integer)
    program_id = Column(Integer, ForeignKey("programs.program_id"), index=True)
    created_at = Column(TIMESTAMP, nullable=True, server_default=func.current_timestamp())
    expire_at = Column(TIMESTAMP, nullable=True)
    is_deleted = Column(Integer, default=0, server_default=text("0")) 

    program = relationship("Program", back_populates="pdf_configurations")


class SystemSetting(Base):
    __tablename__ = "system_settings"
    __table_args__ = (OPTS,)

    setting_key = Column(String(50), primary_key=True)  
    setting_value = Column(String(255))
    description = Column(Text)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("0"))