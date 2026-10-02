import logging
import os
from enum import StrEnum

log_dir=os.path.join(os.getcwd(), 'logs')
os.makedirs(log_dir,exist_ok=True)
log_file_path=os.path.join(log_dir, 'app.log')


log_format_debug="%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"
log_format_standard="%(asctime)s - %(levelname)s - %(message)s"

class LogLevels(StrEnum):
    info="INFO"
    error="ERROR"
    warn="WARN"
    debug="DEBUG"



def config_logging(log_level:str=LogLevels.error):
    log_level=str(log_level).upper()
    valid_levels=[level.value for level in LogLevels]
    
    if log_level not in valid_levels:
        log_level=LogLevels.error.value


    if log_level==LogLevels.debug.value:
        selected_format=log_format_debug
    else:
        selected_format=log_format_standard

    logging.basicConfig(
        level=log_level,
        format=selected_format,
        handlers=[
            logging.FileHandler(log_file_path), 
            logging.StreamHandler()           
        ],
        force=True 
    )

logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("multipart").setLevel(logging.WARNING)

config_logging(LogLevels.warn)