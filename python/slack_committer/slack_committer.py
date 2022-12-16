import fnmatch
import os
from glob import glob
import json
from datetime import datetime
from typing import List, Dict, Union

JsonObject = Dict[str, Union[str, int, float]]
JsonArray = List[JsonObject]
# JsonMsg = Dict[str, str]


LOG_DIR: str = "/home/ghimmk/db_log"

DIGIT: str = "[0-9]"
YEAR: str = DIGIT * 4
MONTH: str = DIGIT * 2
DAY: str = DIGIT * 2
LOG_EXT: str = ".json"
LOG_GLOB_PATTERN: str = YEAR + '-' + MONTH + '-' + DAY + LOG_EXT
# LOG_REGEX_PATTERN = \d{4}-\d{2}-\d{2}.json

# ANY_DIGIT: str = "*([0-9])"
PATCH_DELIMETER: str = "keeper_db"


class PatchNote:
    content: str
    send_time: datetime
    uploaded_files: List[str]

    def __init__(self, content: str, send_time: datetime, uploaded_files: List[str]) -> None:
        self.content = content
        self.send_time = send_time
        self.uploaded_files = uploaded_files


class AnalyzedLog:
    patch_notes: List[PatchNote]
    user_map: Dict[str, str]

    def __init__(self, patch_notes: List[PatchNote], user_map: Dict[str, str]) -> None:
        self.patch_notes = patch_notes
        self.user_map = user_map


class User:
    code: str
    name: str

    def __init__(self, code: str, name: str) -> None:
        self.code = code
        self.name = name


def slack_commit():
    log_files: List[str] = get_log_files(LOG_DIR, LOG_GLOB_PATTERN)

    analyzed_log: AnalyzedLog = analyze_log_files(log_files)


def get_log_files(log_path: str, log_pattern: str) -> List[str]:
    return sorted(glob(log_path + '/' + log_pattern))


def analyze_log_files(log_files: List[str]) -> AnalyzedLog:
    patch_notes: List[PatchNote] = list()
    user_map: Dict[str, str] = dict()

    user: User

    for day_log_file in log_files:
        with open(day_log_file, 'r') as day_log:
            messages: JsonArray = json.load(day_log)

            for msg in messages:

                if is_user_profile_included(msg) and msg["user"] not in user_map:
                    user = get_user_map(msg)
                    user_map[user.code] = user.name

                if is_patch_note(msg):
                    patch_notes.append(get_patch_note(msg))

    return AnalyzedLog(patch_notes, user_map)


def is_user_profile_included(msg: JsonObject) -> bool:
    return ("user_profile" in msg)


def get_user_map(msg: JsonObject) -> User:
    code = msg["user"]
    name = msg["user_profile"]["real_name"]

    return User(code, name)


def is_patch_note(msg: JsonObject) -> bool:
    return msg["text"].startswith(PATCH_DELIMETER)


def get_patch_note(msg: JsonObject) -> PatchNote:
    content: str = msg["text"]
    send_time: datetime = datetime.fromtimestamp(float(msg["ts"]))
    uploaded_files: List[str] = [f["name"] for f in msg["files"]]

    return PatchNote(content, send_time, uploaded_files)


if __name__ == "__main__":
    slack_commit()
