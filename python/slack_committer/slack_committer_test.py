import unittest
from slack_committer import *
import fnmatch
from pprint import pprint


class StringPatternTester(unittest.TestCase):
    def test_glob_pattern(self):
        g: str = LOG_GLOB_PATTERN
        self.assertTrue(fnmatch.fnmatch('2020-12-03.json', g))
        self.assertFalse(fnmatch.fnmatch('2020-12-3.json', g))

    def test_is_patch_note(self):
        j1: JsonObject = {
            "text": "keeper_db 0.7.0\n• content 컬럼들의 자료형이 수정되었습니다."
        }

        j2: JsonObject = {
            "text": "keeper_db 1.10.0 ~ 1.11.0\n• content 컬럼들의 자료형이 수정되었습니다."
        }

        self.assertTrue(is_patch_note(j1))
        self.assertTrue(is_patch_note(j2))


class ConvertTester(unittest.TestCase):
    def test_convert_to_plaintext(self):
        s: str = "keeper_db 1.11.0\n• 20220824 DB 업데이트\n• 테이블을 추가했습니다.\n    ◦ `merit_log`\n        ▪︎ 상\/벌점 관련 로그 테이블입니다.\n        ▪︎ 부여자(관리자만 가능), 수여자, 시간, 상\/벌점 유형을 기록합니다.\n    ◦ `merit_type`\n        ▪︎ 상\/벌점 유형을 기록하는 테이블입니다.\n        ▪︎ 점수, 상벌점 여부, 세부내용을 기록합니다.\n        ▪︎ `content` : LONGTEXT -&gt; TINYTEXT"
        md: str = "keeper_db 1.11.0\n- 20220824 DB 업데이트\n- 테이블을 추가했습니다.\n    - `merit_log`\n        - 상\/벌점 관련 로그 테이블입니다.\n        - 부여자(관리자만 가능), 수여자, 시간, 상\/벌점 유형을 기록합니다.\n    - `merit_type`\n        - 상\/벌점 유형을 기록하는 테이블입니다.\n        - 점수, 상벌점 여부, 세부내용을 기록합니다.\n        - `content` : LONGTEXT -> TINYTEXT"

        self.assertEqual(convert_to_plaintext(s), md)

    def test_convert_userid_to_username(self):
        user_map: Dict[str, str] = {"U02RSJATULA": "gusah009",
                                    "U02RL5VEJ0N": "lkukh17"}
        userid_text: str = "keeper_db 0.18.0\n• 20220214 DB패치노트\n• 기본 데이터가 추가되었습니다. `category` <@U02RSJATULA> <@U02RL5VEJ0N> \n    ◦ 대조표의 기본데이터 시트에 기록해두었습니다."
        username_text: str = "keeper_db 0.18.0\n• 20220214 DB패치노트\n• 기본 데이터가 추가되었습니다. `category` @gusah009 @lkukh17 \n    ◦ 대조표의 기본데이터 시트에 기록해두었습니다."

        self.assertEqual(convert_userid_to_username(
            userid_text, user_map), username_text)


def print_patch_notes():
    log_files: List[str] = get_log_files(LOG_DIR, LOG_GLOB_PATTERN)
    # print(log_files)
    analyzed_log: AnalyzedLog = analyze_log_files(log_files)
    add_user_manually(analyzed_log.user_map)
    convert_patch_notes_format(analyzed_log)
    for p in analyzed_log.patch_notes:
        print(p.content)
        print(p.uploaded_files)
        print("\n===========================\n")

    pprint(analyzed_log.user_map)


if __name__ == "__main__":
    unittest.main()
    # print_patch_notes()
