from glob import glob
import json
from datetime import datetime
from typing import List, Dict, Union
from git import Repo

JsonObject = Dict[str, Union[str, int, float]]
JsonArray = List[JsonObject]


LOG_DIR: str = "/home/ghimmk/scripts/python/slack_committer/db_log"
REPO_DIR: str = "/home/ghimmk/keeper_homepage/Homepage-Database"

DIGIT: str = "[0-9]"
YEAR: str = DIGIT * 4
MONTH: str = DIGIT * 2
DAY: str = DIGIT * 2
LOG_EXT: str = ".json"
LOG_GLOB_PATTERN: str = YEAR + '-' + MONTH + '-' + DAY + LOG_EXT

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

    add_user_manually(analyzed_log.user_map)
    convert_patch_notes_format(analyzed_log)

    commit_patch_notes(REPO_DIR, analyzed_log.patch_notes)


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
    name = msg["user_profile"]["name"]

    return User(code, name)


def is_patch_note(msg: JsonObject) -> bool:
    return msg["text"].startswith(PATCH_DELIMETER)


def get_patch_note(msg: JsonObject) -> PatchNote:
    content: str = msg["text"]
    send_time: datetime = datetime.fromtimestamp(float(msg["ts"]))

    uploaded_files: List[str] = [f["name"]
                                 for f in msg["files"]
                                 if "name" in f]

    return PatchNote(content, send_time, uploaded_files)


def add_user_manually(user_map: Dict[str, str]) -> None:
    manual_users = {
        "U02S5FDQ6TB": "koty08"
    }

    user_map.update(manual_users)


def convert_patch_notes_format(analyzed_log: AnalyzedLog) -> None:
    for p in analyzed_log.patch_notes:
        p.content = convert_to_plaintext(p.content)
        p.content = convert_userid_to_username(
            p.content, analyzed_log.user_map)


def convert_to_plaintext(content: str) -> str:
    content = replace_lgt_to_symbol(content)
    content = replace_dot_to_bar(content)

    return content


def replace_dot_to_bar(content: str) -> str:
    return content.replace('•', '-')\
        .replace('◦', '-')\
        .replace('▪︎', '-')


def replace_lgt_to_symbol(content: str) -> str:
    return content.replace("&gt;", '>')\
        .replace("&lt;", '<')


def convert_userid_to_username(content: str, user_map: Dict[str, str]) -> str:
    for user_id, user_name in user_map.items():
        content = content.replace("<@" + user_id + ">", '@' + user_name)

    return content


def commit_patch_notes(repo_path: str, patch_notes: List[PatchNote]) -> None:
    repo: Repo = Repo(repo_path)
    send_time_str: str

    for p in patch_notes:
        repo.git.add(p.uploaded_files)

        send_time_str = p.send_time.strftime('%Y-%m-%d %H:%M:%S')

        repo.index.commit(p.content,
                          commit_date=send_time_str,
                          author_date=send_time_str)


if __name__ == "__main__":
    slack_commit()
