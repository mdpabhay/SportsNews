# database.py
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List

DB_FILE = "cricket_data.db"

def _conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        match_id TEXT PRIMARY KEY,
        series_name TEXT,
        match_description TEXT,
        start_time TEXT,
        status TEXT,
        match_url TEXT,
        match_info TEXT,
        squads TEXT,
        scorecard TEXT,
        live_data TEXT,
        raw_html TEXT,
        updated_at TEXT
    );""")
    conn.commit()
    conn.close()

def _to_json_field(obj):
    if obj is None:
        return None
    try:
        return json.dumps(obj)
    except Exception:
        return json.dumps({"raw": str(obj)})

def upsert_match(match: Dict):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO matches(match_id, series_name, match_description, start_time, status, match_url,
                        match_info, squads, scorecard, live_data, raw_html, updated_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    ON CONFLICT(match_id) DO UPDATE SET
        series_name=excluded.series_name,
        match_description=excluded.match_description,
        start_time=excluded.start_time,
        status=excluded.status,
        match_url=excluded.match_url,
        match_info=excluded.match_info,
        squads=excluded.squads,
        scorecard=excluded.scorecard,
        live_data=excluded.live_data,
        raw_html=excluded.raw_html,
        updated_at=excluded.updated_at
    """, (
        match.get("match_id"),
        match.get("series_name"),
        match.get("match_description"),
        match.get("start_time"),
        match.get("status"),
        match.get("match_url"),
        _to_json_field(match.get("match_info")),
        _to_json_field(match.get("squads")),
        _to_json_field(match.get("scorecard")),
        _to_json_field(match.get("live_data")),
        _to_json_field(match.get("raw_html")),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

def get_all_matches() -> List[Dict]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT match_id, series_name, match_description, start_time, status, match_url, updated_at FROM matches ORDER BY start_time")
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append({
            "match_id": r["match_id"],
            "series_name": r["series_name"],
            "match_description": r["match_description"],
            "start_time": r["start_time"],
            "status": r["status"],
            "match_url": r["match_url"],
            "updated_at": r["updated_at"]
        })
    return out

def get_match_details(match_id: str) -> Optional[Dict]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    def _maybe_json(s):
        if s is None:
            return None
        try:
            return json.loads(s)
        except Exception:
            return s
    return {
        "match_id": r["match_id"],
        "series_name": r["series_name"],
        "match_description": r["match_description"],
        "start_time": r["start_time"],
        "status": r["status"],
        "match_url": r["match_url"],
        "match_info": _maybe_json(r["match_info"]),
        "squads": _maybe_json(r["squads"]),
        "scorecard": _maybe_json(r["scorecard"]),
        "live_data": _maybe_json(r["live_data"]),
        "raw_html": _maybe_json(r["raw_html"]),
        "updated_at": r["updated_at"]
    }
