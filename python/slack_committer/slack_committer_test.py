import unittest
from slack_committer import *
import fnmatch
from typing import List


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

    def test_convert_to_plaintext(self):
        s: str = "keeper_db 1.11.0\n• 20220824 DB 업데이트\n• 테이블을 추가했습니다.\n    ◦ `merit_log`\n        ▪︎ 상\/벌점 관련 로그 테이블입니다.\n        ▪︎ 부여자(관리자만 가능), 수여자, 시간, 상\/벌점 유형을 기록합니다.\n    ◦ `merit_type`\n        ▪︎ 상\/벌점 유형을 기록하는 테이블입니다.\n        ▪︎ 점수, 상벌점 여부, 세부내용을 기록합니다.\n        ▪︎ `content` : LONGTEXT -&gt; TINYTEXT"
        md: str = "keeper_db 1.11.0\n- 20220824 DB 업데이트\n- 테이블을 추가했습니다.\n    - `merit_log`\n        - 상\/벌점 관련 로그 테이블입니다.\n        - 부여자(관리자만 가능), 수여자, 시간, 상\/벌점 유형을 기록합니다.\n    - `merit_type`\n        - 상\/벌점 유형을 기록하는 테이블입니다.\n        - 점수, 상벌점 여부, 세부내용을 기록합니다.\n        - `content` : LONGTEXT -> TINYTEXT"

        self.assertEqual(convert_to_plaintext(s), md)


def print_patch_notes():
    log_files: List[str] = get_log_files(LOG_DIR, LOG_GLOB_PATTERN)
    print(log_files)
    analyzed_log: AnalyzedLog = analyze_log_files(log_files)

    convert_patch_notes_format(analyzed_log.patch_notes)
    for p in analyzed_log.patch_notes:
        print(p.content)
        print(p.uploaded_files)
        print("\n===========================\n")


if __name__ == "__main__":
    unittest.main()
    # print_patch_notes()
