import logging
from chatbot.db import teacher_query
from chatbot.tools_sql import check_sql,MAX_ROWS

VIEWS_T={"v_t_profile","v_t_courses","v_t_schedule","v_t_students","v_t_student_attendance",
         "v_t_attendance_log","v_t_fyp","v_t_salary","v_t_complaints","v_t_notifications"}

SCHEMA_T="""Run ONE read-only MySQL SELECT on the logged-in teacher's own data. Use it for any question the other tools do not answer exactly (filters, counts, sums, comparisons, sorting).
The views already contain only this teacher's rows, so NEVER filter by teacher id. Use only these views and columns:
v_t_profile(first_name,last_name,email,contact,qualification,joining_date)
v_t_courses(course_name,program_name,credit_hours,no_of_lectures)
v_t_schedule(day_of_week,course_name,section_name,start_time,end_time,location)
v_t_students(course_name,section_name,first_name,last_name,current_semester)
v_t_student_attendance(course_name,first_name,last_name,total_lectures,attended,absent,percentage)  percentage NULL means no lectures yet
v_t_attendance_log(course_name,attendance_date,day_of_week,total_students,total_present,total_absent)
v_t_fyp(student_name,project_title,status,progress,created_at)
v_t_salary(month,year,basic_salary,bonus,deductions,net_salary,status)
v_t_complaints(title,status)
v_t_notifications(title,description,status,created_at)
Rules: one SELECT only, no semicolon, no comments, no backticks, only these views. Use LIKE '%text%' for names."""


def query_my_data_teacher(user:dict,sql=None):
    try:
        s=check_sql(sql,VIEWS_T)
    except ValueError as e:
        return {"error":str(e),"hint":"Write one SELECT using only the v_t_* views."}
    try:
        rows=teacher_query(user,s)
    except Exception as e:
        logging.warning(f"teacher query failed: {e}")
        return {"error":"query failed","detail":str(e)[:200]}
    return {"rows":rows[:MAX_ROWS],"row_count":len(rows),"truncated":len(rows)>MAX_ROWS}




def _like(v):
    v=str(v or "").strip()[:60]
    return f"%{v}%" if v else None


def _f(value,column):
    like=_like(value)
    return (f" AND {column} LIKE %s",[like]) if like else ("",[])


def t_schedule(user:dict,day=None,course=None):
    d=str(day or "").strip().capitalize()
    e,p="",[]
    if d in ("Monday","Tuesday","Wednesday","Thursday","Friday"):
        e=" AND day_of_week=%s"
        p.append(d)
    f,fp=_f(course,"course_name")
    rows=teacher_query(user,f"""SELECT * FROM v_t_schedule WHERE 1=1{e}{f}
        ORDER BY FIELD(day_of_week,'Monday','Tuesday','Wednesday','Thursday','Friday'),start_time""",tuple(p+fp))
    return {"classes":rows}


def t_student_attendance(user:dict,course=None,name=None,below=None):
    f1,p1=_f(course,"course_name")
    f2,p2=_f(name,"CONCAT(first_name,' ',last_name)")
    e,p3="",[]
    try:
        if below not in (None,""):
            e=" AND percentage < %s"
            p3.append(float(below))
    except (TypeError,ValueError):
        e,p3="",[]
    rows=teacher_query(user,f"""SELECT * FROM v_t_student_attendance WHERE 1=1{f1}{f2}{e}
        ORDER BY percentage ASC LIMIT %s""",tuple(p1+p2+p3+[MAX_ROWS]))
    return {"students":rows}


def t_salary(user:dict,month=None,year=None):
    f,p=_f(month,"`month`")
    e=""
    try:
        if year not in (None,""):
            e=" AND `year`=%s"
            p.append(int(year))
    except (TypeError,ValueError):
        e=""
    rows=teacher_query(user,f"SELECT * FROM v_t_salary WHERE 1=1{f}{e} ORDER BY `year` DESC LIMIT 6",tuple(p))
    return {"salary_records":rows}


def t_fyp(user:dict,status=None):
    f,p=_f(status,"status")
    rows=teacher_query(user,f"SELECT * FROM v_t_fyp WHERE 1=1{f} ORDER BY created_at DESC LIMIT %s",tuple(p+[MAX_ROWS]))
    return {"fyp_students":rows}


def t_profile(user:dict):
    rows=teacher_query(user,"SELECT * FROM v_t_profile")
    return {"profile":rows[0] if rows else None}