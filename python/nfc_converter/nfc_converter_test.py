import unittest


class NfcTester(unittest.TestCase):
    def test_runs(self):
        self.assertEqual('foo'.upper(),'FOO')


if __name__ == "__main__":
    unittest.main()
