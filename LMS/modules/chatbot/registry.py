
from modules.chatbot import rag


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


SEARCH=_tool(
    "search_policies",
    "University rules, policies, procedures and help-desk information (how something works, what the rules are). Not for personal data.",
    rag.search_policies,
    {"question":{"type":"string","description":"The question rewritten in English, short and specific."}}
)

TOOLS={
    "student":[SEARCH],
    "teacher":[SEARCH],
    "admin":[SEARCH]
}


def tools_for(role:str):
    return TOOLS.get(role,[])


