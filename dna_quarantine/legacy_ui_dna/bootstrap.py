"""
MultiMind AI - Design DNA & Theme Registry Bootstrap (S6.2 / S8.1)
Idempotent bootstrap module to register Design DNA proofs and map Identity DNAs to ThemeRegistry.
"""
import copy
import logging
from .registry import get_registry as get_dna_registry
from .mapper import dna_to_theme
from .proofs import PROOFS
from ui.themes import get_registry as get_theme_registry

logger = logging.getLogger(__name__)


def ensure_proof_dna_and_themes_registered() -> None:
    """Safely and idempotently registers Design DNA proofs and maps Identity DNAs to ThemeRegistry.

    Idempotence rules:
    - If a proof DNA/Theme ID is absent, registers a deep copy.
    - If present, compares against fresh canonical proof instance to prevent shared object mutation drift.
    - If present with any conflicting parameters or semantic overrides, raises ValueError.
    """
    dna_reg = get_dna_registry()
    theme_reg = get_theme_registry()

    for canonical_proof_dna in PROOFS:
        existing_dna = dna_reg.get_dna(canonical_proof_dna.id)
        if existing_dna is None:
            # Register a deep copy so registered instance object identity is decoupled from canonical PROOFS
            dna_reg.register_dna(copy.deepcopy(canonical_proof_dna))
        else:
            # Compare registered instance against fresh canonical proof definition
            if existing_dna != canonical_proof_dna:
                raise ValueError(
                    f"Conflicting DesignDNA definition found in registry for ID '{canonical_proof_dna.id}'. "
                    f"Registered DNA does not match canonical expected proof DNA."
                )

        # Only map Identity DNAs into ThemeRegistry automatically
        if canonical_proof_dna.role == "identity":
            mapped_theme = dna_to_theme(canonical_proof_dna)

            # Use public list_themes API for exact ID presence lookup without inspecting private _themes dictionary
            registered_themes = {t.id: t for t in theme_reg.list_themes()}
            if mapped_theme.id in registered_themes:
                existing_theme = registered_themes[mapped_theme.id]
                if existing_theme != mapped_theme:
                    raise ValueError(
                        f"Conflicting Theme definition found in registry for ID '{mapped_theme.id}'. "
                        f"Registered Theme does not match incoming mapped Theme."
                    )
            else:
                theme_reg.register_theme(mapped_theme)
