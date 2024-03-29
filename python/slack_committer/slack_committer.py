import os
import shutil
import argparse
import json
import re
from glob import glob
from fnmatch import fnmatch
from git import Repo
from datetime import datetime
from typing import List, Dict, Union
from colorama import Fore

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

RECENT_FILE_NAME: str = "recent_init.sql"
RECENT_FILE_GLOB_PATTERN: str = "*init*.sql"

README_FILE_NAME: str = "README.md"
README_HEADER: str = """

# Homepage-Database

키퍼 홈페이지 데이터베이스

## Recent Patch note
### """

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--export", action="store",
                    dest="file_export", help="export json array of PatchNote class")

parser.add_argument("-i", "--import", action="store",
                    dest="file_import", help="import json array of PatchNote class")

parser.add_argument("-d", "--directory", action="store",
                    dest="origin_file_dir", help="set directory of original files, default is below the repository path")

parser.add_argument("-p", "--print", action="store_true",
                    dest="print_mode", help="print all patch notes")

parser.add_argument("-c", "--collect_all", action="store_true",
                    dest="collect_all_mode", help="do not use delimeter and collect all logs")

parser.add_argument("-r", "--recent", action="store_true",
                    dest="stage_recent", help="stage on recent file")

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
        patch_note_dict = vars(self)
        patch_note_dict["send_time"] = self.send_time.strftime(DATETIME_FORMAT)

        return patch_note_dict


def from_dict_to_PatchNote(dict_in: JsonObject) -> PatchNote:
    return PatchNote(dict_in["content"],
                     datetime.strptime(dict_in["send_time"], DATETIME_FORMAT),
                     dict_in["uploaded_files"])


PatchNotes = List[PatchNote]


class AnalyzedLog:
    patch_notes: PatchNotes
    user_map: Dict[str, str]

    def __init__(self, patch_notes: PatchNotes, user_map: Dict[str, str]) -> None:
        self.patch_notes = patch_notes
        self.user_map = user_map


class User:
    uid: str
    name: str

    def __init__(self, uid: str, name: str) -> None:
        self.uid = uid
        self.name = name


def slack_commit(patch_notes: PatchNotes):
    commit_patch_notes(patch_notes)


def get_patch_notes() -> PatchNotes:
    log_files: List[str] = get_log_files(LOG_DIR, LOG_GLOB_PATTERN)
    user_map: Dict[str, str] = get_user_map(USERS_LIST)
    analyzed_log: AnalyzedLog = analyze_log_files(log_files, user_map)
    convert_patch_notes_format(analyzed_log)

    return analyzed_log.patch_notes


def export_patch_notes(export_path: str, patch_notes: PatchNotes) -> None:
    patch_notes_json: JsonArray = get_patch_notes_json_format(patch_notes)

    with open(export_path, 'w') as file_exported:
        file_exported.write(patch_notes_json)


def get_patch_notes_json_format(patch_notes: PatchNotes) -> JsonArray:
    return json.dumps(
        [p.to_dict() for p in patch_notes],
        indent=2, ensure_ascii=False)


def get_imported_patch_notes(import_path: str) -> PatchNotes:
    with open(import_path, 'r') as file_imported:
        patch_notes_imported_json: JsonArray = json.load(file_imported)

    patch_notes: PatchNotes = [
        from_dict_to_PatchNote(p)
        for p in patch_notes_imported_json]

    return patch_notes


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
    patch_notes: PatchNotes = list()

    for day_log_file in log_files:
        with open(day_log_file, 'r') as day_log:
            messages = json.load(day_log)

            for msg in messages:
                if is_user_profile_included(msg) and msg["user"] not in user_map:
                    user = get_user_from_profile(msg)
                    user_map[user.uid] = user.name

                if args.collect_all_mode or is_patch_note(msg):
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

    uploaded_files: List[str] = get_uploaded_files(msg)

    return PatchNote(content, send_time, uploaded_files)


def get_uploaded_files(msg: JsonObject) -> List[str]:
    uploaded_file_objects: JsonObject = msg.get("files")

    if uploaded_file_objects:
        return [f["name"]
                for f in uploaded_file_objects
                if "name" in f]
    else:
        return list()


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


def commit_patch_notes(patch_notes: PatchNotes) -> None:
    repo: Repo = Repo(REPO_DIR)
    send_time_str: str

    for p in patch_notes:
        send_time_str = p.send_time.strftime(DATETIME_FORMAT)

        stage_recent_patchnote(repo, p.content)
        stage_uploaded_files(repo, p)

        repo.index.commit(p.content,
                          commit_date=send_time_str,
                          author_date=send_time_str)


def stage_recent_patchnote(repo: Repo, patch_note_content: str):
    readme_path: str = f"{REPO_DIR}/{README_FILE_NAME}"

    update_readme(readme_path, patch_note_content)

    repo.git.add(readme_path)


def update_readme(readme_path: str, patch_note_content: str):
    readme_content: str = README_HEADER + patch_note_content

    with open(readme_path, 'w') as readme:
        readme.write(readme_content)


def stage_uploaded_files(repo: Repo, patch_note: PatchNote) -> None:
    staged_date: str = patch_note.send_time.strftime("%Y-%m-%d")
    staged_dir: str = f"{REPO_DIR}/{staged_date}"
    origin_dir: str = get_origin_dir()

    try:
        make_staged_dir(staged_dir)
    except FileNotFoundError:
        return

    move_uploaded_files(patch_note.uploaded_files, origin_dir, staged_dir)
    repo.git.add(staged_dir)

    if args.stage_recent:
        stage_recent_file(repo, patch_note.uploaded_files, staged_dir)


def get_origin_dir() -> str:
    return args.origin_file_dir if args.origin_file_dir else REPO_DIR


def make_staged_dir(staged_dir: str) -> None:
    try:
        os.mkdir(staged_dir)
    except FileExistsError as ee:
        print(f"{ee}\n{staged_dir} already exists. Make dir process will be passed.")
    except FileNotFoundError as nfe:
        print(f"{nfe}\n{staged_dir} path is not found. Staging is stopped.")
        raise FileNotFoundError


def move_uploaded_files(uploaded_files: List[str], origin_dir: str, staged_dir: str) -> None:
    for f in uploaded_files:
        try:
            shutil.move(f"{origin_dir}/{f}", f"{staged_dir}/{f}")
        except FileNotFoundError as nfe:
            print(f"{nfe}\n{origin_dir}/{f} not exist... skip this file.")


def stage_recent_file(repo: Repo, uploaded_files: List[str], staged_dir: str) -> None:
    recent_file: str = get_recent_file(uploaded_files)

    if recent_file:
        copy_recent_file(recent_file, staged_dir)
        repo.git.add(f"{REPO_DIR}/{RECENT_FILE_NAME}")


def get_recent_file(uploaded_files: List[str]) -> str:
    for f in uploaded_files:
        if fnmatch(f, RECENT_FILE_GLOB_PATTERN):
            return f

    return ""


def copy_recent_file(recent_file: str, staged_dir: str) -> None:
    shutil.copy(f"{staged_dir}/{recent_file}",
                f"{REPO_DIR}/{RECENT_FILE_NAME}")


def print_patch_notes(patch_notes: PatchNotes) -> None:
    for p in patch_notes:
        print(Fore.MAGENTA + p.send_time.strftime(DATETIME_FORMAT))
        print(Fore.WHITE + p.content, end="\n")

        if not p.uploaded_files:
            print(Fore.RED + "No file uploaded.", end="\n\n")
        else:
            print(Fore.YELLOW + str(p.uploaded_files), end="\n\n")


if __name__ == "__main__":

    patch_notes: PatchNotes

    if args.file_import and args.file_export:
        print("Choose either import and export mode or nothing.")
        exit(1)

    if args.file_import:
        print(f"import : {args.file_import}")
        patch_notes = get_imported_patch_notes(args.file_import)
        commit_patch_notes(patch_notes)

    elif args.file_export:
        print(f"export : {args.file_export}")
        patch_notes = get_patch_notes()
        export_patch_notes(args.file_export, patch_notes)

    elif args.print_mode:
        patch_notes = get_patch_notes()
        print_patch_notes(patch_notes)

    else:
        print("parse log and commit")
        patch_notes = get_patch_notes()
        commit_patch_notes(patch_notes)
