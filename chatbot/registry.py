from chatbot import tools_student as ts
from chatbot import rag
from chatbot import tools_sql as sq
from chatbot import tools_teacher as tt
 


def _tool(name:str,description:str,fn,params=None):
    return {
        "schema":{
            "type":"function",
            "function":{
            "name":name,
            "description":description,
            "parameters":{
                "type":"object",
                "properties":params or {}
                }}},
        "fn":fn
    }


COURSE={"course":{"type":"string","description":"Part of the course name. Omit for all."}}
TEACHER_TOOLS=[
    _tool("get_my_profile","Teacher's own profile: name, email, contact, qualification, joining date.",tt.t_profile),
    _tool("get_my_schedule","Teaching timetable. Omit day for the whole week.",tt.t_schedule,
          {"day":{"type":"string","description":"Weekday name. Omit for all days."},**COURSE}),
    _tool("get_student_attendance","Per student attendance in the teacher's courses. Use below to list students under a percentage.",tt.t_student_attendance,
          {**COURSE,"name":{"type":"string","description":"Part of the student name."},
           "below":{"type":"number","description":"Only students with percentage below this."}}),
    _tool("get_my_salary","The teacher's own salary records: basic, bonus, deductions, net, paid or pending.",tt.t_salary,
          {"month":{"type":"string","description":"Month name."},"year":{"type":"integer","description":"Year."}}),
    _tool("get_my_fyp","FYP students supervised by the teacher: title, status, progress.",tt.t_fyp,
          {"status":{"type":"string","description":"In Progress, Approved, Completed or Rejected."}}),
    _tool("search_policies","University rules, policies and procedures (salary rules, hiring, leave, how something works). Not for the teacher's own data.",
          rag.search_policies,
          {"question":{"type":"string","description":"The question rewritten in English, short and specific."}}),
    _tool("query_my_data",tt.SCHEMA_T,tt.query_my_data_teacher,
          {"sql":{"type":"string","description":"One MySQL SELECT over the v_t_* views."}}),
]


STUDENT_TOOLS=[
    _tool("get_today_schedule","Today's classes (course, time, location) of the logged-in student.",ts.today_schedule),
    _tool("get_my_attendance","Course-wise attendance (total lectures, attended, percentage) of the logged-in student.",ts.my_attendance),
    _tool("get_my_submissions","Assignments/quizzes the student uploaded (status Pending means the teacher has not reviewed it yet, with marks if graded) and which open ones are not uploaded yet.",ts.my_submissions),
    _tool("get_my_complaints","Status (Pending/Solved/Rejected) of complaints and suggestions the student submitted.",ts.my_complaints),
    _tool("get_my_fee","Recent fee records (month, amount, paid or due).",ts.my_fee),
    _tool("get_my_fyp","Final year project status, progress and supervisor of the student.",ts.my_fyp),
    _tool("get_my_results","Semester GPA and pass/fail, and per-course marks, grade and subject GPA of the logged-in student.",ts.my_results),
    _tool("search_policies","University rules, policies, procedures and help-desk information (how something works, what the rules are, which page to use). Not for the student's own data.",
    rag.search_policies,
        {"question":{"type":"string","description":"The question rewritten in English, short and specific."}}),
    _tool("query_my_data",sq.SCHEMA,sq.query_my_data,
          {"sql":{"type":"string","description":"One MySQL SELECT over the v_my_* views."}}),
]


ADMIN_TOOLS=[
    _tool("search_policies","University rules, policies and procedures (account management, admissions, fee collection, attendance, exams, how something works).",
          rag.search_policies,
          {"question":{"type":"string","description":"The question rewritten in English, short and specific."}}),
]

TOOLS={
    "student":STUDENT_TOOLS,
    "teacher":TEACHER_TOOLS,
    "admin":ADMIN_TOOLS
    }


def tools_for(role:str):
    return TOOLS.get(role,[])








