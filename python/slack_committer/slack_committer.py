import json
import re
from datetime import datetime
from glob import glob
from git import Repo
import argparse
from typing import List, Dict, Union

JsonObject = Dict[str, Union[str, int, float, List, Dict]]
JsonArray = List[JsonObject]


LOG_DIR: str = "/home/ghimmk/scripts/python/slack_committer/db_log"
USERS_LIST: str = "/home/ghimmk/scripts/python/slack_committer/db_log/users.json"
REPO_DIR: str = "/home/ghimmk/keeper_homepage/Homepage-Database"

DIGIT: str = "[0-9]"
YEAR: str = DIGIT * 4
MONTH: str = DIGIT * 2
DAY: str = DIGIT * 2
LOG_EXT: str = ".json"
LOG_GLOB_PATTERN: str = YEAR + '-' + MONTH + '-' + DAY + LOG_EXT

PATCH_DELIMETER: str = "keeper_db"

USER_ID_REG_PATTERN: str = r"(<@)(U[A-Z0-9]{10})(>)"
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

parser = argparse.ArgumentParser()
parser.add_argument("--export", action="store",
                    dest="file_export", help="export json array of PatchNote class")

parser.add_argument("--import", action="store",
                    dest="file_import", help="import json array of PatchNote class")

parser.add_argument("--log", action="store_true",
                    dest="log_mode", help="print all log")

args = parser.parse_args()


class PatchNote:
    content: str
    send_time: datetime
    uploaded_files: List[str]

    def __init__(self, content: str, send_time: datetime, uploaded_files: List[str]) -> None:
        self.content = content
        self.send_time = send_time
        self.uploaded_files = uploaded_files

    def to_dict(self) -> JsonObject:
        patch_note_dict = self.__dict__
        patch_note_dict["send_time"] = self.send_time.strftime(DATETIME_FORMAT)

        return patch_note_dict

    @classmethod
    def from_dict(cls, dict_in: JsonObject) -> 'PatchNote':
        for key in dict_in:
            if key == "send_time":
                setattr(cls, key, datetime(dict_in[key]))
            else:
                setattr(cls, key, dict_in[key])

        return cls


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
    patch_notes: List[PatchNote] = get_patch_notes()

    # commit_patch_notes(REPO_DIR, analyzed_log.patch_notes)


def get_patch_notes() -> List[PatchNote]:
    log_files: List[str] = get_log_files(LOG_DIR, LOG_GLOB_PATTERN)
    user_map: Dict[str, str] = get_user_map(USERS_LIST)
    analyzed_log: AnalyzedLog = analyze_log_files(log_files, user_map)
    convert_patch_notes_format(analyzed_log)

    return analyzed_log.patch_notes


def export_patch_notes(export_path: str) -> None:
    patch_notes: List[PatchNote] = get_patch_notes()
    patch_notes_json: JsonArray = get_patch_notes_json_format(patch_notes)

    with open(export_path, 'w') as file_exported:
        file_exported.write(patch_notes_json)


def get_patch_notes_json_format(patch_notes: List[PatchNote]) -> JsonArray:
    return json.dumps(
        [p.to_dict() for p in patch_notes],
        indent=2, ensure_ascii=False)


def commit_imported_patch_notes(import_path: str) -> None:
    with open(import_path, 'r') as file_imported:
        patch_notes_imported: JsonArray = json.load(file_imported)

    # commit_patch_notes(REPO_DIR, PatchNote(patch_notes_imported))


def get_log_files(log_path: str, log_pattern: str) -> List[str]:
    return sorted(glob(log_path + '/' + log_pattern))


def get_user_map(users_list_file: str) -> Dict[str, str]:
    user_map: Dict[str, str] = dict()

    try:
        with open(users_list_file, 'r') as users_list:
            users_array: JsonArray = json.load(users_list)

            for u in users_array:
                user_map[u["id"]] = u["name"]

    except FileNotFoundError as f:
        print(f"{f} : File not found")

    return user_map


def analyze_log_files(log_files: List[str], user_map: Dict[str, str]) -> AnalyzedLog:
    messages: JsonArray
    user: User
    patch_notes: List[PatchNote] = list()

    for day_log_file in log_files:
        with open(day_log_file, 'r') as day_log:
            messages = json.load(day_log)

            for msg in messages:
                if is_user_profile_included(msg) and msg["user"] not in user_map:
                    user = get_user_from_profile(msg)
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
    return content\
        .replace('•', '-')\
        .replace('◦', '-')\
        .replace('▪︎', '-')


def replace_lgt_to_symbol(content: str) -> str:
    return content\
        .replace("&gt;", '>')\
        .replace("&lt;", '<')


def convert_userid_to_username(content: str, user_map: Dict[str, str]) -> str:
    content = replace_by_regex_pattern(content, user_map)
    return content


def replace_by_regex_pattern(content: str, user_map: Dict[str, str]) -> str:
    return re.sub(
        USER_ID_REG_PATTERN,
        lambda m: f"@{user_map.get(m.group(2))}",
        content)


def commit_patch_notes(repo_path: str, patch_notes: List[PatchNote]) -> None:
    repo: Repo = Repo(repo_path)
    send_time_str: str

    for p in patch_notes:
        repo.git.add(p.uploaded_files)

        send_time_str = p.send_time.strftime(DATETIME_FORMAT)

        repo.index.commit(p.content,
                          commit_date=send_time_str,
                          author_date=send_time_str)


if __name__ == "__main__":

    if args.file_export:
        print(f"export : {args.file_export}")
        export_patch_notes(args.file_export)

    elif args.file_import:
        print(f"import : {args.file_import}")
        commit_imported_patch_notes(args.file_import)

    else:
        # full process
        slack_commit()

    if args.log_mode:
        pass
