"""
merge_progress.py
Copies Aashi's study history from another copy of the database (for example
the one downloaded from her laptop) into this one, without duplicates:
quiz attempts, lesson completions and reading attempts.

Content (lessons, questions, passages) is never copied; only her progress.
A backup of this database is made first.

Run from the backend folder:
    python merge_progress.py study_buddy_aashi.db
"""
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from database import ensure_schema
import models  # noqa: F401

DB_PATH = Path(__file__).parent / "study_buddy.db"

# table -> columns that identify the same event in both copies
TABLES = {
    "quiz_attempts": ("topic_id", "attempted_at"),
    "lesson_progress": ("lesson_id",),
    "passage_attempts": ("passage_id", "attempted_at"),
}


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    other = Path(sys.argv[1]).resolve()
    if not other.exists():
        raise SystemExit(f"Not found: {other}")

    ensure_schema()
    backup = DB_PATH.with_name(f"study_buddy.backup-{datetime.now():%Y%m%d-%H%M%S}-pre-merge.db")
    shutil.copy2(DB_PATH, backup)
    print(f"Backed up database to {backup.name}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("attach database ? as other", (str(other),))
    with conn:
        for table, key in TABLES.items():
            if not conn.execute("select 1 from other.sqlite_master where name = ?", (table,)).fetchone():
                continue
            ours = [r[1] for r in conn.execute(f"pragma main.table_info({table})")]
            theirs = {r[1] for r in conn.execute(f"pragma other.table_info({table})")}
            cols = [c for c in ours if c in theirs and c != "id"]
            match = " and ".join(f"m.{k} = o.{k}" for k in key)
            n = conn.execute(
                f"insert into main.{table} ({', '.join(cols)}) "
                f"select {', '.join('o.' + c for c in cols)} from other.{table} o "
                f"where not exists (select 1 from main.{table} m where {match})"
            ).rowcount
            print(f"{table}: added {n}")
    conn.close()


if __name__ == "__main__":
    main()
