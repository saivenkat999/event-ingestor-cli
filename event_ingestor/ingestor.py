import json

from event_ingestor.storage import EventStorage


def _is_ascii_digits(value):
    return bool(value) and value.isascii() and value.isdigit()


def _is_utc_iso_timestamp(value):
    if value.endswith("Z"):
        timestamp_body = value[:-1]
    elif value.endswith("+00:00"):
        timestamp_body = value[:-6]
    else:
        return False

    if timestamp_body.count("T") != 1:
        return False
    date_text, time_text = timestamp_body.split("T", 1)
    date_parts = date_text.split("-")
    time_parts = time_text.split(":")
    if len(date_parts) != 3 or len(time_parts) != 3:
        return False
    if not all(_is_ascii_digits(part) for part in date_parts):
        return False

    year, month, day = (int(part) for part in date_parts)
    if len(date_parts[0]) != 4 or not 1 <= month <= 12:
        return False

    days_per_month = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if not 1 <= day <= days_per_month[month - 1]:
        return False

    second_text = time_parts[2]
    if "." in second_text:
        second_parts = second_text.split(".", 1)
        if not _is_ascii_digits(second_parts[1]):
            return False
        second_text = second_parts[0]

    if not all(_is_ascii_digits(part) for part in time_parts[:2]):
        return False
    if not _is_ascii_digits(second_text):
        return False

    hour, minute, second = int(time_parts[0]), int(time_parts[1]), int(second_text)
    return 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59


def validate_record(raw_dict: dict) -> dict:
    if not isinstance(raw_dict, dict):
        raise ValueError("record must be a JSON object")

    event_id = raw_dict.get("event_id")
    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError("event_id must be a non-empty string")

    timestamp = raw_dict.get("timestamp")
    if not isinstance(timestamp, str) or not _is_utc_iso_timestamp(timestamp):
        raise ValueError("timestamp must be an ISO-8601 UTC timestamp")

    source = raw_dict.get("source")
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")

    payload = raw_dict.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")

    return {
        "event_id": event_id,
        "timestamp": timestamp,
        "source": source,
        "payload": payload,
    }


class Ingestor:
    def __init__(self, storage: EventStorage):
        self._storage = storage

    def ingest_file(self, input_path: str) -> dict:
        processed = 0
        inserted = 0
        with open(input_path, "r", encoding="utf-8") as input_file:
            for raw_line in input_file:
                record = validate_record(json.loads(raw_line))
                self._storage.insert_event(
                    record["event_id"],
                    record["timestamp"],
                    record["source"],
                    record["payload"],
                )
                processed += 1
                inserted += 1
        return {"processed": processed, "inserted": inserted}
