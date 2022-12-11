import os
from glob import glob
import json
from datetime import datetime
from typing import List, Dict

PATCH_DELIMETER: str = "keeper_db"
LOG_DIR: str = "/home/ghimmk/db_log"

DIGIT: str = "[0-9]"
LOG_EXT: str = ".json"
LOG_GLOB_PATTERN: str = DIGIT * 4 + '-' + DIGIT * 2 + '-' + DIGIT * 2 + LOG_EXT
# LOG_REGEX_PATTERN = \d{4}-\d{2}-\d{2}.json


class PatchNote:
    content: str
    send_time: datetime
    uploaded_files: List[str]

    def __init__(self, content: str, send_time: datetime, uploaded_files: List[str]) -> None:
        self.content = content
        self.send_time = send_time
        self.uploaded_files = uploaded_files


def slack_commit():
    log_files: List[str] = get_logs(LOG_DIR, LOG_GLOB_PATTERN)
    analyze_log_files(log_files)


def get_logs(log_path: str, log_pattern: str) -> List[str]:
    return sorted(glob(log_path + '/' + log_pattern))


def analyze_log_files(log_files: List[str]) -> List[PatchNote]:
    patch_notes: List[PatchNote] = list()

    for day_log_file in log_files:
        with open(day_log_file, 'r') as day_log:
            messages: List[Dict] = json.load(day_log)
            for msg in messages:
                if(is_patch_note(msg)):
                    patch_notes.append(extract_patch_note(msg))

    return patch_notes


def is_patch_note(msg: Dict[str]) -> bool:
    return msg["text"].startswith(PATCH_DELIMETER)


def extract_patch_note(msg: str) -> PatchNote:

    content: str = msg["text"]
    send_time: datetime = datetime.fromtimestamp(float(msg["ts"]))
    uploaded_files: List[str] = [f["name"] for f in msg["files"]]

    return PatchNote(content, send_time, uploaded_files)


if __name__ == "__main__":
    slack_commit()
