"""Flat-file SQLite quote store (stdlib only). DB lives at backend/quotes.db."""
import json
import os
import sqlite3
import unicodedata
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("QUOTES_DB", os.path.join(HERE, "quotes.db"))
WEB_SOURCE = os.environ.get("QUOTES_URL", "https://dummyjson.com/quotes?limit=0")
MAX_QUOTE_LEN = 160  # keeps every card readable on one 1920x1080 screen
MAX_LETTERS = 16
VOID = "No quote starts with {l}, but keep seeking wisdom!"

SCHEMA = """
CREATE TABLE IF NOT EXISTS quotes (
  id INTEGER PRIMARY KEY,
  text TEXT NOT NULL UNIQUE,
  author TEXT,
  first_letter TEXT NOT NULL,
  source TEXT DEFAULT 'seed'
);
CREATE INDEX IF NOT EXISTS idx_quotes_letter ON quotes(first_letter);
"""


def connect(path=None):
    conn = sqlite3.connect(path or DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def first_letter(text):
    """First A-Z letter of text with accents folded (É -> E); '' if it doesn't start with one."""
    for ch in text.strip().lstrip("\"'“”‘’([ "):
        base = unicodedata.normalize("NFD", ch)[:1].upper()
        return base if "A" <= base <= "Z" else ""
    return ""


def add_many(conn, rows, source):
    added = 0
    for text, author in rows:
        text = (text or "").strip()
        letter = first_letter(text)
        if not text or not letter:
            continue
        cur = conn.execute(
            "INSERT OR IGNORE INTO quotes(text, author, first_letter, source) VALUES (?,?,?,?)",
            (text, author or "Unknown", letter, source),
        )
        added += cur.rowcount
    conn.commit()
    return added


def seed_bundled(conn):
    with open(os.path.join(HERE, "seed_quotes.json"), encoding="utf-8") as f:
        return add_many(conn, json.load(f), "seed")


def seed_from_web(conn=None, timeout=10):
    """Pull quotes from the web. Never raises: offline just means fewer quotes."""
    import requests

    own = conn is None
    conn = conn or connect()
    try:
        resp = requests.get(WEB_SOURCE, timeout=timeout)
        resp.raise_for_status()
        rows = [(q.get("quote"), q.get("author")) for q in resp.json().get("quotes", [])]
        return add_many(conn, rows, "web")
    except Exception as exc:  # noqa: BLE001 - best effort by design
        print(f"Web quote fetch skipped: {exc}")
        return 0
    finally:
        if own:
            conn.close()


def quotes_for_name(conn, name):
    """One quote per letter of `name`, distinct where a letter repeats. None if no letters."""
    letters = [first_letter(c) for c in name if c.strip()]
    letters = [l for l in letters if l][:MAX_LETTERS]
    if not letters:
        return None
    pool = {}
    for letter, n in Counter(letters).items():
        rows = conn.execute(
            "SELECT text, author FROM quotes WHERE first_letter=? AND length(text)<=? "
            "ORDER BY random() LIMIT ?",
            (letter, MAX_QUOTE_LEN, n),
        ).fetchall()
        pool[letter] = [{"letter": letter, "text": r["text"], "author": r["author"]} for r in rows]
    out, used = [], Counter()
    for l in letters:
        options = pool[l]
        if not options:  # nothing starts with this letter at all
            out.append({"letter": l, "text": VOID.format(l=l), "author": "The Void"})
            continue
        out.append(options[used[l] % len(options)])  # distinct while stock lasts, then reuse
        used[l] += 1
    return out


if __name__ == "__main__":
    c = connect()
    print(f"Bundled quotes added: {seed_bundled(c)}")
    print(f"Web quotes added: {seed_from_web(c)}")
