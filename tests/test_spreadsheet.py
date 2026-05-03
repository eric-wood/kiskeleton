import unittest
from pathlib import Path

from src.spreadsheet import Spreadsheet


# this is not my preferred method of doing this, as it has the following downsides:
# - it relies on the output being an unformatted raw version of the s-expressions
# - in the event of a failure there's no diff presented
# the goal for now is to provide a sanity check and prevent regressions,
# so this is more than sufficient but I'd like to revisit it if the project grows.
class SnapshotAssertions:
    def assertMatchesSnapshot(self, fixture_path: str, result: str):
        expected = Path(fixture_path).read_text().rstrip()
        if expected != result:
            raise AssertionError(f"Input does not match fixture {fixture_path}")


class TestSpreadsheet(unittest.TestCase, SnapshotAssertions):
    def test_single(self):
        input_path = "tests/fixtures/single.csv"
        spreadsheet = Spreadsheet()
        spreadsheet.read(input_path)
        result = spreadsheet.to_library().to_str()
        self.assertMatchesSnapshot("tests/fixtures/single_result.kicad_sym", result)

    def test_multiple(self):
        input_path = "tests/fixtures/multiple.csv"
        spreadsheet = Spreadsheet()
        spreadsheet.read(input_path)
        result = spreadsheet.to_library().to_str()
        self.assertMatchesSnapshot("tests/fixtures/multiple_result.kicad_sym", result)
