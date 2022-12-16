from glob import glob
import json
from datetime import datetime
from typing import List, Dict, Union
from git import Repo
import re

JsonObject = Dict[str, Union[str, int, float]]
JsonArray = List[JsonObject]


LOG_DIR: str = "/home/ghimmk/scripts/python/slack_committer/db_log"
USERS_LIST: str = "//home/ghimmk/scripts/python/slack_committer/db_log/users.json"
REPO_DIR: str = "/home/ghimmk/keeper_homepage/Homepage-Database"

DIGIT: str = "[0-9]"
YEAR: str = DIGIT * 4
MONTH: str = DIGIT * 2
DAY: str = DIGIT * 2
LOG_EXT: str = ".json"
LOG_GLOB_PATTERN: str = YEAR + '-' + MONTH + '-' + DAY + LOG_EXT

PATCH_DELIMETER: str = "keeper_db"

WHOLE_USER_MAP: Dict[str, str]
USER_ID_PATTERN: str = r"(<@)(U[A-Z0-9]{10})(>)"


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
    uid: str
    name: str

    def __init__(self, uid: str, name: str) -> None:
        self.uid = uid
        self.name = name


def slack_commit():
    log_files: List[str] = get_log_files(LOG_DIR, LOG_GLOB_PATTERN)
    set_whole_user_map(USERS_LIST)
    analyzed_log: AnalyzedLog = analyze_log_files(log_files)

    convert_patch_notes_format(analyzed_log)

    # commit_patch_notes(REPO_DIR, analyzed_log.patch_notes)


def get_log_files(log_path: str, log_pattern: str) -> List[str]:
    return sorted(glob(log_path + '/' + log_pattern))


def set_whole_user_map(users_list_file: str) -> Dict[str, str]:
    whole_user_map: Dict[str, str] = dict()

    with open(users_list_file, 'r') as users_list:
        users_array: JsonArray = json.load(users_list)

        for u in users_array:
            whole_user_map[u["id"]] = u["name"]

    global WHOLE_USER_MAP
    WHOLE_USER_MAP = whole_user_map


def analyze_log_files(log_files: List[str]) -> AnalyzedLog:
    patch_notes: List[PatchNote] = list()
    user_map: Dict[str, str] = dict()

    user_id: str
    user: User

    for day_log_file in log_files:
        with open(day_log_file, 'r') as day_log:
            messages: JsonArray = json.load(day_log)

            for msg in messages:
                user_id = msg["user"]

                if user_id not in user_map:
                    if is_user_profile_included(msg):
                        user = get_user_from_profile(msg)

                    elif is_user_exist(user_id):
                        user = get_user_from_map(user_id)
                    user_map[user.uid] = user.name

                if is_patch_note(msg):
                    patch_notes.append(get_patch_note(msg))

    return AnalyzedLog(patch_notes, user_map)


def is_user_profile_included(msg: JsonObject) -> bool:
    return ("user_profile" in msg)


def get_user_from_profile(msg: JsonObject) -> User:
    user_id = msg["user"]
    user_name = msg["user_profile"]["name"]

    return User(user_id, user_name)


def is_user_exist(user_id: str) -> bool:
    return (user_id in WHOLE_USER_MAP)


def get_user_from_map(user_id: str) -> User:
    return User(user_id, WHOLE_USER_MAP[user_id])


def is_patch_note(msg: JsonObject) -> bool:
    return msg["text"].startswith(PATCH_DELIMETER)


def get_patch_note(msg: JsonObject) -> PatchNote:
    content: str = msg["text"]
    send_time: datetime = datetime.fromtimestamp(float(msg["ts"]))

    uploaded_files: List[str] = [f["name"]
                                 for f in msg["files"]
                                 if "name" in f]

    return PatchNote(content, send_time, uploaded_files)


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
        content = replace_by_regex_pattern(content)

    return content


def replace_by_regex_pattern(content: str) -> str:
    return re.sub(
        USER_ID_PATTERN,
        lambda m: f"@{WHOLE_USER_MAP[m.group(1)]}",
        content)


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
