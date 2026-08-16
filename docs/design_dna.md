# MultiMind AI - Design DNA Contract & Architecture (S6.1)

## Overview

Design DNA represents structured visual and design intent derived from a reference or design direction. It provides a formal data contract that describes visual character, color direction, typography direction, surface/material language, shape language, and interaction character without becoming an arbitrary CSS dump or layout engine.

## Conceptual Architecture Flow

```
Reference / Inspiration
        ↓
    Design DNA (ui.dna.models.DesignDNA)
        ↓
  pure adapter (ui.dna.mapper.dna_to_theme)
        ↓
    Theme contract (ui.themes.models.Theme)
        ↓
   Theme Engine (ui.themes.registry.ThemeRegistry)
        ↓
  semantic `--mm-*` CSS custom properties
        ↓
   MultiMind UI Foundation (ui.foundation)
```

## Contracts & Modules (`ui/dna/`)

### 1. `DesignDNA` (`ui/dna/models.py`)
Dataclass capturing structured design character and semantic token overrides:
- **Identity / Reference**: `id`, `display_name`, `category`, `description`, `reference_identity`
- **Design Character**: `visual_character`, `color_direction`, `typography_direction`, `surface_language`, `shape_language`, `interaction_character`
- **Material / Provenance**: `materials` (list of `MaterialReference`), `provenance` (dictionary for metadata like author, license, source, attribution)
- **Theme Overrides**: `colors`, `typography`, `spacing`, `radius` (maps directly to S5 Theme contract)

### 2. `MaterialReference` (`ui/dna/models.py`)
Dataclass representing individual design materials, textures, fonts, or assets with provenance:
- `id`, `material_type`, `source`, `author`, `license`, `attribution`, `reference_ip`
- `scope_lock` (bool): `True` for reference-specific materials, `False` for shared resources.
- `shared_resource_policy` (str): `"disallowed"` for reference-specific materials, `"allowed"` for explicitly shared resources.

#### Canonical Material Sharing Policy:
- **Reference-Specific / Non-Shared**: `scope_lock=True` AND `shared_resource_policy="disallowed"`
- **Explicitly Shared**: `scope_lock=False` AND `shared_resource_policy="allowed"`
- Contradictory combinations raise `ValueError` on validation.

### 3. `dna_to_theme()` Pure Adapter (`ui/dna/mapper.py`)
Function translating a `DesignDNA` instance into a valid S5 `Theme` object:
- Deep copies supported semantic override dictionaries (`colors`, `typography`, `spacing`, `radius`).
- Constructs a `ThemeMetadata` object populated from DNA description, reference identity, and DNA-level provenance metadata.
- Does **not** mutate the source `DesignDNA` instance or base tokens.
- Does **not** automatically register the theme with `ThemeRegistry`.

### 4. `DNARegistry` (`ui/dna/registry.py`)
Central registry managing registration, material scope ownership enforcement, and lookup for `DesignDNA` instances:
- `register_dna(dna)`: Validates DNA, rejects duplicate DNA IDs with `ValueError`, and enforces material ownership rules (reusing non-shared materials across distinct DNA entries raises `ValueError`).
- `list_dna()`: Returns all registered DNA entries.
- `get_dna(dna_id)`: Retrieves DNA by ID or returns `None` if unknown (no silent fallback or default DNA concept).

## Architectural Rules & Locks

1. **Theme Separation**: Design DNA describes visual intent; Theme represents resolved semantic token values applied by the Theme Engine.
2. **Layout Lock**: Design DNA **never** controls application layout, sidebar positioning, login/chat structure, or page composition.
3. **No Arbitrary CSS**: Design DNA contains no `custom_css` escape hatches or unparsed CSS blobs. All visual overrides pass through semantic `--mm-*` CSS variables via the S5 Theme Engine.
4. **No Asset Scraper / AI Extractor**: S6.1 provides architecture only. Asset downloading, scraping, license crawling, and AI DNA extraction are strictly deferred.
