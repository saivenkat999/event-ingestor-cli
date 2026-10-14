import json
import sqlite3


class EventStorage:
    def __init__(self, db_path: str):
        self._connection = sqlite3.connect(db_path)
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS events ("
            "seq_id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "event_id TEXT NOT NULL, "
            "timestamp TEXT NOT NULL, "
            "source TEXT NOT NULL, "
            "payload_json TEXT NOT NULL)"
        )
        self._connection.commit()

    def insert_event(self, event_id, timestamp, source, payload_dict):
        payload_json = json.dumps(payload_dict, ensure_ascii=False)
        self._connection.execute(
            "INSERT INTO events (event_id, timestamp, source, payload_json) "
            "VALUES (?, ?, ?, ?)",
            (event_id, timestamp, source, payload_json),
        )
        self._connection.commit()

    def count_events(self) -> int:
        row = self._connection.execute("SELECT COUNT(*) FROM events").fetchone()
        return row[0]

    def get_all_events(self) -> list[dict]:
        self._connection.row_factory = sqlite3.Row
        rows = self._connection.execute(
            "SELECT seq_id, event_id, timestamp, source, payload_json "
            "FROM events ORDER BY seq_id"
        ).fetchall()
        return [dict(row) for row in rows]

    def close(self):
        self._connection.close()
