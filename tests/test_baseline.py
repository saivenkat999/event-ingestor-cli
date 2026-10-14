import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "fixtures" / "sample_valid.jsonl"
sys.path.insert(0, str(REPO_ROOT))


class EventIngestionBaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, input_path, db_path, summary_path=None):
        command = [
            sys.executable,
            "-m",
            "event_ingestor.cli",
            "--input",
            str(input_path),
            "--db",
            str(db_path),
        ]
        if summary_path is not None:
            command.extend(["--summary-json", str(summary_path)])
        return subprocess.run(
            command,
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

    def test_valid_file_ingestion(self):
        db_path = self.temp_path / "events.db"
        result = self.run_cli(FIXTURE_PATH, db_path)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {"processed": 5, "inserted": 5},
        )
        connection = sqlite3.connect(str(db_path))
        try:
            count = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        finally:
            connection.close()
        self.assertEqual(count, 5)

    def test_cli_writes_summary_json_file(self):
        db_path = self.temp_path / "events.db"
        summary_path = self.temp_path / "summary.json"
        result = self.run_cli(FIXTURE_PATH, db_path, summary_path)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        with summary_path.open("r", encoding="utf-8") as summary_file:
            summary = json.load(summary_file)
        self.assertEqual(summary, {"processed": 5, "inserted": 5})

    def test_validate_record_accepts_valid_record(self):
        try:
            from event_ingestor.ingestor import validate_record
        except ImportError as error:
            self.fail("event_ingestor.ingestor is not available: {}".format(error))

        record = {
            "event_id": "event-valid",
            "timestamp": "2025-01-01T12:00:00Z",
            "source": "baseline-test",
            "payload": {"value": 7},
        }
        self.assertEqual(validate_record(record), record)

    def test_validate_record_rejects_invalid_records(self):
        try:
            from event_ingestor.ingestor import validate_record
        except ImportError as error:
            self.fail("event_ingestor.ingestor is not available: {}".format(error))

        invalid_records = [
            {
                "timestamp": "2025-01-01T12:00:00Z",
                "source": "baseline-test",
                "payload": {},
            },
            {
                "event_id": "event-invalid",
                "timestamp": "2025-01-01T12:00:00Z",
                "source": "baseline-test",
                "payload": [],
            },
        ]
        for record in invalid_records:
            with self.subTest(record=record):
                with self.assertRaises(ValueError):
                    validate_record(record)


if __name__ == "__main__":
    unittest.main()
