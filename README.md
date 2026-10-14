# Event Ingestor Baseline

A small Python 3 command-line tool that reads JSON Lines event records and stores them in SQLite. It uses only the Python standard library.

## Run

From this directory, ingest the included fixture with:

```sh
python -m event_ingestor.cli --input fixtures/sample_valid.jsonl --db events.db
```

The command prints a JSON summary. Pass `--summary-json path/to/summary.json` to write that summary to a file instead.

Each input line must be a JSON object containing a non-empty `event_id`, a UTC ISO-8601 `timestamp` ending in `Z` or `+00:00`, a non-empty `source`, and an object-valued `payload`. Records are inserted in input order. This baseline intentionally inserts duplicate event IDs and stops immediately when it encounters malformed or invalid input; it does not support checkpoints, quarantine, or resumable batch transactions.

## Tests

Run the baseline regression suite from this directory:

```sh
python -m unittest discover -s tests
```
