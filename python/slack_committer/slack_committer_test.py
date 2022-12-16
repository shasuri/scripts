import unittest
import slack_committer
import fnmatch


class StringPatternTester(unittest.TestCase):
    def test_glob_pattern(self):
        g: str = slack_committer.LOG_GLOB_PATTERN
        self.assertTrue(fnmatch.fnmatch('2020-12-03.json', g))
        self.assertFalse(fnmatch.fnmatch('2020-12-3.json', g))

    def test_is_patch_note(self):
        j1: slack_committer.JsonObject = {
            "text": "keeper_db 0.7.0\n• content 컬럼들의 자료형이 수정되었습니다."
        }

        j2: slack_committer.JsonObject = {
            "text": "keeper_db 1.10.0 ~ 1.11.0\n• content 컬럼들의 자료형이 수정되었습니다."
        }

        self.assertTrue(slack_committer.is_patch_note(j1))
        self.assertTrue(slack_committer.is_patch_note(j2))


if __name__ == "__main__":
    unittest.main()
