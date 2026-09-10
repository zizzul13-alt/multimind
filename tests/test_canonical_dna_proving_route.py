from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT = (ROOT / "multimind_reflex" / "__init__.py").read_text(encoding="utf-8")
PAGE = (ROOT / "multimind_reflex" / "canonical_page.py").read_text(encoding="utf-8")


def test_package_loads_isolated_canonical_proving_route_before_app_construction():
    assert "canonical_page" in INIT
    assert '@rx.page(route="/canonical-dna"' in PAGE
    assert "canonical_theme_studio_panel()" in PAGE


def test_proving_route_is_explicitly_non_cutover_and_application_neutral():
    assert "PROVING · NOT CUTOVER" in PAGE
    assert "application truth untouched" in PAGE
    for forbidden in (
        "core.application",
        "providers.",
        "database.",
        "sqlite3",
        "dna_quarantine",
        "design_dna.",
    ):
        assert forbidden not in PAGE
