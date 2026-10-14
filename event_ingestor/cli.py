import argparse
import json
import sys

from event_ingestor.ingestor import Ingestor
from event_ingestor.storage import EventStorage


def _write_summary(summary, summary_path):
    if summary_path:
        with open(summary_path, "w", encoding="utf-8") as summary_file:
            json.dump(summary, summary_file)
            summary_file.write("\n")
        return

    json.dump(summary, sys.stdout)
    sys.stdout.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ingest JSONL events into SQLite.")
    parser.add_argument("--input", required=True, help="Path to the input JSONL file.")
    parser.add_argument("--db", required=True, help="Path to the SQLite database.")
    parser.add_argument(
        "--summary-json",
        help="Write the ingestion summary to this JSON file instead of stdout.",
    )
    args = parser.parse_args(argv)

    storage = None
    try:
        storage = EventStorage(args.db)
        summary = Ingestor(storage).ingest_file(args.input)
        _write_summary(summary, args.summary_json)
        return 0
    except Exception as error:
        sys.stderr.write("{}\n".format(error))
        return 1
    finally:
        if storage is not None:
            storage.close()


if __name__ == "__main__":
    sys.exit(main())
