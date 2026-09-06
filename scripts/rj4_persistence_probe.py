"""Two-phase RJ-4 persistence probe for process/container recreation."""

from __future__ import annotations

import argparse
from pathlib import Path

from database.manager import DatabaseManager, validate_restore_candidate


SESSION_ID = "rj4-persistence-proof"


def seed(db_path: Path) -> None:
    db = DatabaseManager(str(db_path))
    existing = {row["id"] for row in db.get_sessions()}
    if SESSION_ID not in existing:
        db.create_session(SESSION_ID, "RJ4 durable session", "research")
    snapshot = db.export_bytes()
    assert snapshot.startswith(b"SQLite format 3\x00")
    validate_restore_candidate(db_path)
    print("RJ4_SEED_PASS")


def verify(db_path: Path) -> None:
    assert db_path.exists(), "durable database is missing after recreation"
    db = DatabaseManager(str(db_path))
    rows = {row["id"]: row for row in db.get_sessions()}
    assert SESSION_ID in rows, "persisted session did not survive recreation"
    assert rows[SESSION_ID]["name"] == "RJ4 durable session"
    validate_restore_candidate(db_path)
    snapshot = db.export_bytes()
    assert snapshot.startswith(b"SQLite format 3\x00")
    print("RJ4_VERIFY_PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("seed", "verify"))
    parser.add_argument("db_path")
    args = parser.parse_args()
    db_path = Path(args.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if args.phase == "seed":
        seed(db_path)
    else:
        verify(db_path)


if __name__ == "__main__":
    main()
