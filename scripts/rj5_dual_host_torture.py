"""RJ-5 dual-host application-truth torture.

This does not fake presentation business logic. It instantiates the same
MultiMindApplication composition boundary multiple times, representing host A
(Streamlit), host B (Reflex), and host A again against one authoritative SQLite
file and verifies that persisted truth survives each handoff.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.application import ApplicationRuntime, ChatRequest
from core.composition import build_application_for_user
from database.manager import DatabaseManager


class DeterministicUnifiedAgent:
    def generate(self, prompt, system_prompt=None, mode=None):
        return {
            "status": "success",
            "text": f"echo:{mode}:{prompt[-80:]}",
            "tokens": 11,
            "cost": 0.0,
        }


def _app(db: DatabaseManager, memories: dict):
    return build_application_for_user(
        "rj5_dual_host",
        db=db,
        agents={"unified": DeterministicUnifiedAgent()},
        runtime_memories=memories,
    )


def run(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = DatabaseManager(str(db_path))

    # Host A / Streamlit semantic pass.
    memories_a: dict = {}
    host_a = _app(db, memories_a)
    session_id = host_a.create_session("RJ5 shared truth", "research")
    session = next(row for row in host_a.list_sessions() if row["id"] == session_id)
    host_a.select_session(session)
    result_a = host_a.execute_chat(
        ChatRequest(
            original_prompt="host-a-first",
            context_mode="continue",
            session_id=session_id,
            session_mode="research",
            active_agents=["unified"],
        )
    )
    assert result_a.status == "success" and result_a.persisted

    # Host B / Reflex semantic pass: fresh runtime, same authoritative DB.
    memories_b: dict = {}
    host_b = _app(db, memories_b)
    session_b = next(row for row in host_b.list_sessions() if row["id"] == session_id)
    host_b.select_session(session_b)
    history_b = host_b.get_session_chats(session_id)
    assert len(history_b) == 1
    assert history_b[0]["prompt"] == "host-a-first"
    result_b = host_b.execute_chat(
        ChatRequest(
            original_prompt="host-b-second",
            context_mode="continue",
            session_id=session_id,
            session_mode="research",
            active_agents=["unified"],
        )
    )
    assert result_b.status == "success" and result_b.persisted

    # Host A again: no hidden presentation state can be required for truth.
    host_a2 = _app(db, {})
    session_a2 = next(row for row in host_a2.list_sessions() if row["id"] == session_id)
    host_a2.select_session(session_a2)
    history_a2 = host_a2.get_session_chats(session_id)
    assert [row["prompt"] for row in history_a2] == ["host-a-first", "host-b-second"]

    # Snapshot and restore into another authoritative DB without conversion.
    snapshot = host_a2.export_database()
    restore_path = db_path.with_name("restored.db")
    restored_db = DatabaseManager(str(restore_path))
    runtime = ApplicationRuntime(current_session=session_a2, memories={"stale": object()})
    restored_app = build_application_for_user(
        "rj5_dual_host",
        db=restored_db,
        agents={"unified": DeterministicUnifiedAgent()},
        runtime=runtime,
    )
    restore_result = restored_app.restore_database(snapshot)
    assert restore_result.status == "success"
    assert restore_result.runtime_invalidated
    assert runtime.current_session is None
    assert runtime.memories == {}
    restored_rows = restored_app.get_session_chats(session_id)
    assert [row["prompt"] for row in restored_rows] == ["host-a-first", "host-b-second"]

    print("RJ5_DUAL_HOST_A_B_A_PASS")
    print("RJ5_EXPORT_RESTORE_SAME_SCHEMA_PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("db_path")
    args = parser.parse_args()
    run(Path(args.db_path))


if __name__ == "__main__":
    main()
