"""
MultiMind AI - Design DNA & Theme Registry Bootstrap (S6.2)
Idempotent bootstrap module to register S6.2 real Design DNA proofs and map them to ThemeRegistry.
"""
import logging
import dataclasses
from ui.dna import get_registry as get_dna_registry
from ui.dna.mapper import dna_to_theme
from ui.dna.proofs import PROOFS
from ui.themes import get_registry as get_theme_registry

logger = logging.getLogger(__name__)


def ensure_proof_dna_and_themes_registered() -> None:
    """Safely and idempotently registers S6.2 Design DNA proofs and their mapped Themes.

    Idempotence rules:
    - If a proof DNA/Theme ID is absent, registers it.
    - If present with full structural equality, safely skips re-registration.
    - If present with any conflicting parameters or semantic overrides, raises ValueError.
    """
    dna_reg = get_dna_registry()
    theme_reg = get_theme_registry()

    for proof_dna in PROOFS:
        # Check DNARegistry idempotence using full dataclass structural equality
        existing_dna = dna_reg.get_dna(proof_dna.id)
        if existing_dna is None:
            dna_reg.register_dna(proof_dna)
        else:
            if existing_dna != proof_dna:
                raise ValueError(
                    f"Conflicting DesignDNA definition found in registry for ID '{proof_dna.id}'. "
                    f"Registered DNA does not match incoming proof DNA."
                )

        # Map DNA to Theme
        mapped_theme = dna_to_theme(proof_dna)

        # Check ThemeRegistry idempotence using full dataclass structural equality
        if mapped_theme.id in theme_reg._themes:
            existing_theme = theme_reg._themes[mapped_theme.id]
            if existing_theme != mapped_theme:
                raise ValueError(
                    f"Conflicting Theme definition found in registry for ID '{mapped_theme.id}'. "
                    f"Registered Theme does not match incoming mapped Theme."
                )
        else:
            theme_reg.register_theme(mapped_theme)
