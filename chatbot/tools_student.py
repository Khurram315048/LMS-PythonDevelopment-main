from datetime import datetime
from zoneinfo import ZoneInfo
from chatbot.db import query

TZ=ZoneInfo("Asia/Karachi")
MAX_ROWS=15


def today_schedule(user:dict):
    day=datetime.now(TZ).strftime("%A")
    if day not in ("Monday","Tuesday","Wednesday","Thursday","Friday"):
        return {
            "day":day,
            "classes":[],
            "note":"Weekend, no classes scheduled"
            }
    rows=query("""
        SELECT c.course_name,cs.start_time,cs.end_time,cs.location,se.section_name
        FROM student_section ss
        JOIN sections se ON se.section_id=ss.section_id AND se.is_deleted=0
        JOIN course_schedule cs ON cs.section_id=se.section_id AND cs.is_deleted=0
        JOIN courses c ON c.course_id=cs.course_id AND c.is_deleted=0
        JOIN student_course sc ON sc.student_id=ss.student_id AND sc.course_id=cs.course_id AND sc.is_deleted=0
        WHERE ss.student_id=%s AND ss.is_deleted=0 AND cs.day_of_week=%s
        ORDER BY cs.start_time""",(user["student_id"],day))
    return {
        "day":day,
        "classes":rows
        }


def my_attendance(user:dict):
    rows=query("""
        SELECT c.course_name,
               COUNT(a.attendance_id) AS total_lectures,
               COALESCE(SUM(a.attendance_status='Present'),0) AS attended
        FROM student_course sc
        JOIN courses c ON c.course_id=sc.course_id AND c.is_deleted=0
        LEFT JOIN attendance a ON a.student_course_id=sc.student_course_id AND a.is_deleted=0
        WHERE sc.student_id=%s AND sc.is_deleted=0
        GROUP BY sc.student_course_id,c.course_name
        ORDER BY c.course_name""",(user["student_id"],))
    for r in rows:
        total=int(r["total_lectures"])
        present=int(r["attended"])
        r["total_lectures"]=total
        r["attended"]=present
        r["percentage"]=round(present*100/total,1) if total else 0
    return {
        "courses":rows
        }


def my_submissions(user:dict):
    sid=user["student_id"]
    uploaded=query("""
        SELECT c.course_name,s.submission_type,s.submission_status,s.marks,s.total_marks,s.upload_date
        FROM student_submissions s
        JOIN courses c ON c.course_id=s.course_id AND c.is_deleted=0
        WHERE s.student_id=%s AND s.is_deleted=0
        ORDER BY s.upload_date DESC LIMIT %s""",(sid,MAX_ROWS))
    not_uploaded=query("""
        SELECT c.course_name,'assignment' AS submission_type
        FROM student_section ss
        JOIN sections se ON se.section_id=ss.section_id AND se.is_deleted=0 AND se.assignments_enabled=1
        JOIN courses c ON c.course_id=se.course_id AND c.is_deleted=0
        WHERE ss.student_id=%s AND ss.is_deleted=0
          AND NOT EXISTS (SELECT 1 FROM student_submissions x
                          WHERE x.student_id=ss.student_id AND x.section_id=se.section_id
                            AND x.submission_type='assignment' AND x.is_deleted=0)
        UNION ALL
        SELECT c.course_name,'quiz'
        FROM student_section ss
        JOIN sections se ON se.section_id=ss.section_id AND se.is_deleted=0 AND se.quizzes_enabled=1
        JOIN courses c ON c.course_id=se.course_id AND c.is_deleted=0
        WHERE ss.student_id=%s AND ss.is_deleted=0
          AND NOT EXISTS (SELECT 1 FROM student_submissions x
                          WHERE x.student_id=ss.student_id AND x.section_id=se.section_id
                            AND x.submission_type='quiz' AND x.is_deleted=0)""",(sid,sid))
    return {"uploaded":uploaded,"open_but_not_uploaded_yet":not_uploaded}


def my_complaints(user:dict):
    rows=query("""
        SELECT title,is_status AS status FROM complaint_suggestion
        WHERE user_id=%s AND is_deleted=0
        ORDER BY complt_sugst_id DESC LIMIT %s""",(user["user_id"],MAX_ROWS))
    return {
        "complaints":rows
        }



def my_fyp(user:dict):
    rows=query("""
        SELECT f.project_title,f.status,f.progress,
               CONCAT(t.first_name,' ',t.last_name) AS supervisor
        FROM fyp_groups f
        LEFT JOIN teachers t ON t.teacher_id=f.teacher_id
        WHERE f.student_id=%s AND f.is_deleted=0
        ORDER BY f.fyp_id DESC LIMIT 1""",(user["student_id"],))
    return {"fyp":rows[0] if rows else None}



def my_fee(user:dict):
    rows=query("""
        SELECT fee_month,fee_amount,fee_status,
               (voucher_front_pic IS NOT NULL AND voucher_front_pic<>'') AS voucher_uploaded,
               update_date AS last_update
        FROM student_fees
        WHERE student_id=%s AND is_deleted=0
        ORDER BY student_fees_id DESC LIMIT 6""",(user["student_id"],))
    for r in rows:
        r["voucher_uploaded"]=bool(r["voucher_uploaded"])
    return {"fee_records":rows,
            "note":"fee_status 'due' with voucher_uploaded true usually means the voucher is uploaded and waiting for the office to mark it paid."}



def my_results(user:dict):
    sid=user["student_id"]
    semesters=query("""
        SELECT student_semester AS semester,overall_gpa,result_status
        FROM student_results
        WHERE student_id=%s AND is_deleted=0
        ORDER BY student_semester""",(sid,))
    courses=query("""
        SELECT sr.student_semester AS semester,c.course_name,srm.total_marks,
               srm.student_grade AS grade,srm.subject_gpa,srm.status
        FROM student_results sr
        JOIN student_result_marks srm ON srm.student_result_id=sr.student_result_id AND srm.is_deleted=0
        JOIN student_course sc ON sc.student_course_id=srm.student_course_id
        JOIN courses c ON c.course_id=sc.course_id
        WHERE sr.student_id=%s AND sr.is_deleted=0
        ORDER BY sr.student_semester DESC,c.course_name
        LIMIT %s""",(sid,MAX_ROWS*3))
    return {"semesters":semesters,"courses":courses}