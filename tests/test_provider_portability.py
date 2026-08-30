"""Provider-adjacent imports must not require a Streamlit host."""
import builtins
import importlib.util
from pathlib import Path

import utils.config


def test_config_import_does_not_require_streamlit(monkeypatch):
    original_import = builtins.__import__

    def reject_streamlit(name, *args, **kwargs):
        if name == "streamlit":
            raise AssertionError("Config import must not require Streamlit")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", reject_streamlit)
    spec = importlib.util.spec_from_file_location(
        "config_without_streamlit", Path(utils.config.__file__)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.Config.API_TIMEOUT == 30
