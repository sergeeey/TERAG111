from __future__ import annotations
import os, json, time
from datetime import datetime, timezone
from typing import Dict, Any

DB_PATH = os.getenv('JOURNAL_PATH', 'data/journal/journal.jsonl')
MAX_RECORDS = int(os.getenv('JOURNAL_MAX', '500'))

def _ensure_dir():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def append_cycle(record: Dict[str, Any]) -> None:
    _ensure_dir()
    record['timestamp'] = record.get('timestamp') or datetime.now(timezone.utc).isoformat()
    with open(DB_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    _trim()

def _trim():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if len(lines) > MAX_RECORDS:
            with open(DB_PATH, 'w', encoding='utf-8') as f:
                f.writelines(lines[-MAX_RECORDS:])
    except FileNotFoundError:
        pass

def latest(n:int=50):
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-n:]
        return [json.loads(x) for x in lines]
    except FileNotFoundError:
        return []




































