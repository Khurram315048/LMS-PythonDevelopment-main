from fastapi.templating import Jinja2Templates
from core.config import BASE_DIR

TEMPLATES_DIR=BASE_DIR / "web" / "templates"


def get_templates(folder:str | None=None)->Jinja2Templates:
    dirs=[str(TEMPLATES_DIR)]
    if folder:
        dirs.insert(0,str(TEMPLATES_DIR / folder))
    return Jinja2Templates(directory=dirs)