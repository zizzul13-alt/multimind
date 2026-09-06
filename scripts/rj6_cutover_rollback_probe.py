"""RJ-6 cutover/rollback drill helpers over the real MultiMind application boundary.

This module never changes deployment state by itself. The RJ-6 workflow owns host
startup/stop/recreate; this probe only performs deterministic application operations
against the authoritative SQLite files shared by both presentation hosts.
"""

from __future__ import annotations

import argparse

from core.application import ChatRequest
from core.composition import build_application_for_user
from multimind_reflex.bridge import environment_secrets_source
from utils.config import Config


USER_A = "rj6-user-a"
USER_B = "rj6-user-b"
RESTORE_USER = "rj6-restore"
SESSION_A = "RJ6 rollback user A"
SESSION_B = "RJ6 rollback user B"
STREAMLIT_PROMPT = "RJ6 streamlit phase"
REFLEX_PROMPT = "RJ6 reflex phase"
USER_B_PROMPT = "RJ6 user B private phase"


class DeterministicAgent:
    def generate(self, prompt, system_prompt=None, mode="coding"):
        return {
            "status": "success",
            "text": f"rj6-ok:{prompt[-120:]}",
            "tokens": 7,
            "cost": 0.0,
        }


def _app(user_id: str):
    return build_application_for_user(
        user_id,
        runtime_memories={},
        agents={"unified": DeterministicAgent()},
    )


def _session(application, name: str):
    matches = [item for item in application.list_sessions() if item["name"] == name]
    assert len(matches) == 1, f"expected exactly one session named {name!r}, got {len(matches)}"
    return matches[0]


def _execute(application, session, prompt: str):
    application.select_session(session)
    result = application.execute_chat(
        ChatRequest(
            original_prompt=prompt,
            context_mode="continue",
            session_id=session["id"],
            session_mode=session.get("mode", "coding"),
            active_agents=["unified"],
        )
    )
    assert result.status == "success"
    assert result.persisted is True
    return result


def streamlit_write() -> None:
    app_a = _app(USER_A)
    app_b = _app(USER_B)
    assert not app_a.list_sessions(), "RJ6 user A database must start clean"
    assert not app_b.list_sessions(), "RJ6 user B database must start clean"

    app_a.create_session(SESSION_A, "research")
    app_b.create_session(SESSION_B, "coding")
    session_a = _session(app_a, SESSION_A)
    session_b = _session(app_b, SESSION_B)
    _execute(app_a, session_a, STREAMLIT_PROMPT)
    _execute(app_b, session_b, USER_B_PROMPT)

    assert Config.get_db_path(USER_A) != Config.get_db_path(USER_B)
    assert all(item["name"] != SESSION_B for item in app_a.list_sessions())
    assert all(item["name"] != SESSION_A for item in app_b.list_sessions())
    print("RJ6_STREAMLIT_WRITE_PASS")


def reflex_write() -> None:
    app_a = _app(USER_A)
    session_a = _session(app_a, SESSION_A)
    before = app_a.get_session_chats(session_a["id"])
    assert {item["prompt"] for item in before} == {STREAMLIT_PROMPT}
    _execute(app_a, session_a, REFLEX_PROMPT)
    after = app_a.get_session_chats(session_a["id"])
    assert {item["prompt"] for item in after} == {STREAMLIT_PROMPT, REFLEX_PROMPT}
    print("RJ6_REFLEX_WRITE_PASS")


def verify_shared_truth(marker: str = "RJ6_SHARED_TRUTH_PASS") -> None:
    app_a = _app(USER_A)
    app_b = _app(USER_B)
    session_a = _session(app_a, SESSION_A)
    session_b = _session(app_b, SESSION_B)

    chats_a = app_a.get_session_chats(session_a["id"])
    chats_b = app_b.get_session_chats(session_b["id"])
    assert {item["prompt"] for item in chats_a} == {STREAMLIT_PROMPT, REFLEX_PROMPT}
    assert {item["prompt"] for item in chats_b} == {USER_B_PROMPT}
    assert len(chats_a) == 2
    assert len(chats_b) == 1
    assert all(item["name"] != SESSION_B for item in app_a.list_sessions())
    assert all(item["name"] != SESSION_A for item in app_b.list_sessions())
    print(marker)


def backup_restore() -> None:
    app_a = _app(USER_A)
    backup = app_a.export_database()
    assert backup.startswith(b"SQLite format 3\x00")

    restore_app = _app(RESTORE_USER)
    restored = restore_app.restore_database(backup)
    assert restored.status == "success"
    restored_session = _session(restore_app, SESSION_A)
    restored_chats = restore_app.get_session_chats(restored_session["id"])
    assert {item["prompt"] for item in restored_chats} == {STREAMLIT_PROMPT, REFLEX_PROMPT}

    invalid = restore_app.restore_database(b"not-a-sqlite-backup")
    assert invalid.status == "invalid_backup"
    restored_session = _session(restore_app, SESSION_A)
    assert len(restore_app.get_session_chats(restored_session["id"])) == 2

    verify_shared_truth("RJ6_BACKUP_RESTORE_SOURCE_ISOLATION_PASS")
    print("RJ6_BACKUP_RESTORE_PASS")


def secret_contract() -> None:
    source = environment_secrets_source(
        {
            "MULTIMIND_GEMINI_KEY": "rj6-gemini-sentinel",
            "GEMINI_API_KEY": "must-not-win",
            "MULTIMIND_GROQ_KEY": "rj6-groq-sentinel",
            "MULTIMIND_CLOUDFLARE_ACCOUNT_ID": "rj6-account-sentinel",
        }
    )
    default = source["default"]
    assert default["gemini_key"] == "rj6-gemini-sentinel"
    assert default["groq_key"] == "rj6-groq-sentinel"
    assert default["cloudflare_account_id"] == "rj6-account-sentinel"
    assert "must-not-win" not in default.values()
    print("RJ6_SECRET_INJECTION_CONTRACT_PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "phase",
        choices=(
            "streamlit-write",
            "reflex-write",
            "verify",
            "backup-restore",
            "rollback-verify",
            "secret-contract",
        ),
    )
    args = parser.parse_args()
    if args.phase == "streamlit-write":
        streamlit_write()
    elif args.phase == "reflex-write":
        reflex_write()
    elif args.phase == "verify":
        verify_shared_truth()
    elif args.phase == "backup-restore":
        backup_restore()
    elif args.phase == "rollback-verify":
        verify_shared_truth("RJ6_ROLLBACK_STREAMLIT_SAME_DB_PASS")
    else:
        secret_contract()


if __name__ == "__main__":
    main()
