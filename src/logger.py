# src/logger.py

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import hashlib

DB_PATH = "logs/tickets.db"
JSON_PATH = "logs/tickets.jsonl"

Path("logs").mkdir(exist_ok=True)

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ticket_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT,
            email TEXT,
            confidence REAL,
            action TEXT,
            answer_hash TEXT,
            timestamp TEXT
        )
    """)
    return conn


def log_ticket(ticket_id, email, confidence, action, answer):
    ts = datetime.utcnow().isoformat()
    answer_hash = hashlib.sha256(answer.encode("utf-8")).hexdigest()[:16]

    conn = _get_conn()
    conn.execute(
        "INSERT INTO ticket_logs VALUES (NULL,?,?,?,?,?,?)",
        (ticket_id, email, confidence, action, answer_hash, ts)
    )
    conn.commit()
    conn.close()

    with open(JSON_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ticket_id": ticket_id,
            "email": email,
            "confidence": confidence,
            "action": action,
            "answer_hash": answer_hash,
            "timestamp": ts
        }) + "\n")
