from pathlib import Path

from core.application import MultiMindApplication
from core.composition import build_application_for_user
from utils.config import Config


def test_generic_secrets_source_prefers_user():
    source = {
        "alice": {"gemini_key": "alice-key"},
        "default": {"gemini_key": "default-key"},
    }
    assert Config.get_api_keys("Alice", source)["gemini_key"] == "alice-key"


def test_generic_secrets_source_falls_back_to_default():
    source = {"default": {"groq_key": "default-groq"}}
    assert Config.get_api_keys("alice", source)["groq_key"] == "default-groq"


def test_generic_secrets_source_empty_shape_without_source():
    assert Config.get_api_keys("alice") == Config.EMPTY_API_KEYS
    assert Config.get_api_keys("alice", {}) == Config.EMPTY_API_KEYS


def test_generic_secrets_source_can_be_callable():
    assert Config.get_api_keys(
        "alice", lambda: {"alice": {"openrouter_key": "callable-key"}}
    )["openrouter_key"] == "callable-key"


def test_config_module_has_no_streamlit_dependency():
    config_source = Path("utils/config.py").read_text(encoding="utf-8")
    assert "import streamlit" not in config_source
    assert "st.secrets" not in config_source


def test_shared_composition_uses_generic_source_and_validated_db_namespace(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "DB_DIR", str(tmp_path / "data"))
    captured = {}

    def agents_factory(api_keys):
        captured["keys"] = api_keys
        return {"unified": object()}

    class FakeDatabase:
        def __init__(self, db_path):
            captured["db_path"] = db_path

    app = build_application_for_user(
        "Alice",
        {"alice": {"gemini_key": "secret"}},
        agents_factory=agents_factory,
        database_factory=FakeDatabase,
        runtime_memories={},
    )

    assert isinstance(app, MultiMindApplication)
    assert captured["keys"] == {"gemini_key": "secret"}
    assert Path(captured["db_path"]).name == "alice.db"
    assert Path(captured["db_path"]).parent == (tmp_path / "data" / "users").resolve()


def test_application_read_and_export_seams_do_not_mutate_memory():
    class FakeDatabase:
        def get_sessions(self):
            return [{"id": "s1", "name": "Session"}]

        def get_session_chats(self, session_id, limit=50):
            assert session_id == "s1"
            assert limit == 7
            return [{"id": "c1", "session_id": "s1"}]

        def export_bytes(self):
            return b"sqlite-bytes"

    memories = {"sentinel": object()}
    original = dict(memories)
    app = MultiMindApplication(db=FakeDatabase(), runtime_memories=memories)

    assert app.list_sessions() == [{"id": "s1", "name": "Session"}]
    assert app.get_session_chats("s1", limit=7) == [{"id": "c1", "session_id": "s1"}]
    assert app.export_database() == b"sqlite-bytes"
    assert memories == original


def test_streamlit_host_uses_shared_seams_instead_of_direct_persistence():
    app_source = Path("app.py").read_text(encoding="utf-8")
    assert "build_application_for_user(" in app_source
    assert ".list_sessions()" in app_source
    assert ".get_session_chats(" in app_source
    assert ".export_database()" in app_source
    assert "db.get_sessions(" not in app_source
    assert "db.get_session_chats(" not in app_source
    assert "Config.get_db_path(" not in app_source
    assert "from database.manager import DatabaseManager" not in app_source
