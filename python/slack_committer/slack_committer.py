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


def slack_commit():
    log_files: List[str] = get_logs(LOG_DIR, LOG_GLOB_PATTERN)
    analyze_log_files(log_files)


def get_logs(log_path: str, log_pattern: str) -> List[str]:
    return sorted(glob(log_path + '/' + log_pattern))


def analyze_log_files(log_files: List[str]):
    for day_log_file in log_files:
        with open(day_log_file, 'r') as day_log:
            day_log_loaded: List[str] = json.load(day_log)
            extract_patch_info(day_log_loaded)


def extract_patch_info(messages: str):
    for msg in messages:
        content: str = msg["text"]

        if not content.startswith(PATCH_DELIMETER):
            continue

        send_time: datetime = datetime.fromtimestamp(float(msg["ts"]))


if __name__ == "__main__":
    slack_commit()
