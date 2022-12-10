import os
from glob import glob
import json
from datetime import datetime
from typing import List

PATCH_DELIMETER: str = "keeper_db"
LOG_DIR: str = "/home/ghimmk/db_log"

DIGIT: str = "[0-9]"
LOG_EXT: str = ".json"
LOG_GLOB_PATTERN: str = DIGIT * 4 + '-' + DIGIT * 2 + '-' + DIGIT * 2 + LOG_EXT
# LOG_REGEX_PATTERN = \d{4}-\d{2}-\d{2}.json

logs: List[str] = sorted(glob(LOG_DIR + '/' + LOG_GLOB_PATTERN))


for log_file in logs:
    with open(log_file, 'r') as opened_log_file:
        day_log: List = json.load(opened_log_file)

        for msg in day_log:
            content: str = msg["text"]

            if not content.startswith(PATCH_DELIMETER):
                continue

            send_time: datetime = datetime.fromtimestamp(float(msg["ts"]))
