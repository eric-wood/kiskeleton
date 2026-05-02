import unittest
from pathlib import Path

from src.spreadsheet import Spreadsheet


class FixtureAssertions:
    def assertMatchesFixture(self, fixture_path: str, result: str):
        expected = Path(fixture_path).read_text().rstrip()
        if expected != result:
            raise AssertionError(f"Input does not match fixture {fixture_path}")


class TestSpreadsheet(unittest.TestCase, FixtureAssertions):
    def test_single(self):
        input_path = "tests/fixtures/single.csv"
        spreadsheet = Spreadsheet()
        spreadsheet.read(input_path)
        result = spreadsheet.to_library().to_str()
        self.assertMatchesFixture("tests/fixtures/single_result.kicad_sym", result)
