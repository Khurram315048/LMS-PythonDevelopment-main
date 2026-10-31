from chatbot import tools_student as ts
from chatbot import rag
from chatbot import tools_sql as sq


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

TOOLS={
    "student":STUDENT_TOOLS,
    "teacher":[],
    "admin":[]
    }


def tools_for(role:str):
    return TOOLS.get(role,[])