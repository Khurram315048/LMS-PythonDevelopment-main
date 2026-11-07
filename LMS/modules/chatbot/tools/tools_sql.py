import re
import logging
from tools.tools_student import scoped_query

MAX_ROWS=50
VIEWS={"v_my_profile","v_my_courses","v_my_schedule","v_my_attendance","v_my_submissions",
       "v_my_results","v_my_result_marks","v_my_fees","v_my_complaints","v_my_fyp",
       "v_my_exams","v_my_requests","v_my_notifications"}
_BAD_CHARS=re.compile(r"[;@`\\#]|--|/\*|\*/")
_BAD_WORDS=re.compile(r"\b(into|outfile|dumpfile|load_file|sleep|benchmark|information_schema|"
                     r"performance_schema|mysql|sys|lock|handler|call|set|my_student_id|my_user_id|my_teacher_id)\b|for\s+update",re.I)




_FROM_COMMA=re.compile(r"\b(?:from|join)\s+[a-z_][a-z0-9_]*(?:\s+(?:as\s+)?[a-z_][a-z0-9_]*)?\s*,",re.I)
_SOURCES=re.compile(r"\b(?:from|join)\s+([a-z_][a-z0-9_]*)",re.I)



SCHEMA="""Run ONE read-only MySQL SELECT on the logged-in student's own data. Use it for any question about the student's own data that the other tools do not answer exactly, or when you need a filter, count, sum, average, comparison or sort.
The views already contain only this student's rows, so NEVER filter by student id. Use only these views and columns:
v_my_profile(first_name,last_name,email,contact,current_semester,admission_session,admission_date,last_qualification,program_name,program_coordinator)
v_my_courses(course_name,teacher_name)
v_my_schedule(day_of_week,course_name,section_name,start_time,end_time,location)
v_my_attendance(course_name,total_lectures,attended,absent,percentage)  one row per course, percentage NULL means no lectures yet
v_my_submissions(course_name,submission_type,submission_status,marks,total_marks,upload_date)  submission_type is assignment or quiz
v_my_results(semester,overall_gpa,result_status)
v_my_result_marks(semester,course_name,total_marks,grade,subject_gpa,status)
v_my_fees(fee_month,fee_amount,fee_status,voucher_uploaded,last_update)
v_my_complaints(title,status)
v_my_fyp(project_title,status,progress,supervisor)
v_my_exams(exam_category,exam_date,exam_semester,start_time,end_time,location,mode,status)
v_my_requests(request_type,detail,status,request_date)  request_type is semester_freeze, improvement, retake or summer_registration
v_my_notifications(title,description,status,created_at)
Rules: one SELECT only, no semicolon, no comments, only these views. Use LIKE '%text%' for course names. Select only the columns needed.
Examples: overall attendance = SELECT ROUND(100*SUM(attended)/SUM(total_lectures),1) AS overall FROM v_my_attendance
courses below 75 percent = SELECT course_name,percentage FROM v_my_attendance WHERE percentage<75"""






def check_sql(sql,views=VIEWS):
    s=str(sql or "").strip().rstrip(";").strip()
    if not s or len(s)>600:
        raise ValueError("empty or too long")
    if not re.match(r"^select\b",s,re.I):
        raise ValueError("only a SELECT is allowed")
    if _BAD_CHARS.search(s) or _BAD_WORDS.search(s):
        raise ValueError("query contains something that is not allowed")
    if _FROM_COMMA.search(s):
        raise ValueError("use JOIN, not comma between tables")
    sources=_SOURCES.findall(s)
    if not sources:
        raise ValueError("select from one of the allowed views")
    for t in sources:
        if t.lower() not in views:
            raise ValueError(f"unknown view {t}")
    return s


def query_my_data(user:dict,sql=None):
    try:
        s=check_sql(sql)
    except ValueError as e:
        return {
            "error":str(e),
            "hint":"Write one SELECT using only the v_my_* views."}
    try:
        rows=scoped_query(s,user["student_id"],user["user_id"])
    except Exception as e:
        logging.warning(f"query_my_data failed: {e}")
        return {
            "error":"query failed",
            "detail":str(e)[:200]}
    return {
        "rows":rows[:MAX_ROWS],
        "row_count":len(rows),
        "truncated":len(rows)>MAX_ROWS
        }


