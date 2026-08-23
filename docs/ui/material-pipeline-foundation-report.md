# MultiMind AI — Material Pipeline Foundation & Real Proof Integrations Report

## Executive Summary

This report documents the architectural foundation and proof integrations for MultiMind AI's Material / Asset Pipeline within the Design DNA subsystem.

The Material Pipeline establishes a bounded, deterministic asset resolution mechanism connecting references and Design DNA to validated repository visual materials, without mutating core theme engines, introducing speculative infrastructure, or executing unparsed CSS / HTML.

---

## 1. Baseline Gap Analysis (CURRENT MAIN)

Prior to this phase:
1. `MaterialReference` contained metadata fields (`id`, `material_type`, `source`, `author`, `license`, `attribution`, `reference_ip`, `scope_lock`, `shared_resource_policy`), but lacked a repository asset binding field (`asset_path`).
2. S6.2 proof Design DNAs (`japan-print-ink`, `chainsaw-man-inspired`, `mushishi-inspired`) were asset-free (`materials = []`).
3. Application presentation surfaces (sidebar branding, Theme Studio preview) used generic emoji/text markers (`🤖 MultiMind`) with no generic seam to resolve and display theme-bound materials.

---

## 2. Architectural Model & Layer Separation

The pipeline strictly preserves the architectural separation of concerns:

```
Reference / Inspiration
        ↓
DesignDNA (ui.dna.models.DesignDNA)
        ↓
MaterialReference (ui.dna.models.MaterialReference)
        ↓
Generic Material Resolver (ui.dna.resolver)
        ↓
Presentation Consumption Seam (ui.presentation.brand.render_brand_identity)
        ↓
Bounded Streamlit Component Surface
```

### Core Separation Locks:
- **Reference ≠ DesignDNA ≠ Material ≠ Theme ≠ CSS ≠ Layout**
- **Material** is NOT arbitrary CSS or unparsed CSS blobs.
- **Material** is NOT a second Theme Engine.
- **Material** does NOT own application state.
- **Theme** continues to represent pure semantic CSS token overrides (`--mm-*`).

---

## 3. Storage Convention & Deterministic Root Anchoring

Approved UI material assets reside in a predictable, repository-local path:

```
ui/assets/materials/
    <material_id>/
        <asset_filename>
```

### Approved Proof Assets:
1. `ui/assets/materials/japan-ink-mark/mark.svg`
2. `ui/assets/materials/chainsaw-hazard-mark/mark.svg`
3. `ui/assets/materials/mushishi-moss-mark/mark.svg`

### Deterministic Root Anchoring:
The material root is anchored deterministically relative to `ui/dna/resolver.py` module path rather than process current working directory (`CWD`), ensuring asset resolution succeeds regardless of execution entry point or `os.chdir()`.

Runtime material assets are strictly local repository files. No external CDN fetching, hotlinking, or remote downloads are permitted.

---

## 4. Contract Extension & Supported Material Types

### MaterialReference Contract (`ui/dna/models.py`)
Minimally extended with `asset_path: str = ""`:

- `id`: Non-empty material ID string (independent of theme ID).
- `material_type`: Enforced against `SUPPORTED_MATERIAL_TYPES = {"graphic_mark"}`.
- `asset_path`: Repository-relative path string.
- `scope_lock` & `shared_resource_policy`: Enforces non-shared vs shared resource rules in `DNARegistry`.
- `source`, `author`, `license`, `attribution`, `reference_ip`: Truthful provenance tracking.

### Supported Material Type Set:
To prevent speculative infrastructure, `SUPPORTED_MATERIAL_TYPES` is strictly bounded to types with a real presentation consumer (`"graphic_mark"`). Unsupported material types fail closed to fallback.

### DNARegistry Ownership (`ui/dna/registry.py`)
`DNARegistry` retains single-source-of-truth ownership over registered `DesignDNA` objects and enforces material scope lock policies:
- Reusing a scope-locked material (`scope_lock=True`, `shared_resource_policy="disallowed"`) across distinct `DesignDNA` registrations is rejected with a `ValueError`.

---

## 5. Security & Containment Verification

The Material Resolver (`ui/dna/resolver.py`) validates every `asset_path` against strict security checks before declaring a material resolved:

1. **Relative Path Enforcement**: Absolute paths (e.g., `/etc/passwd`) are rejected.
2. **Path Traversal Guard**: Path traversal sequences (`../`, `..\\`) are rejected using `os.path.commonpath` verification against the canonical material root (`ui/assets/materials`).
3. **Prefix Verification**: Resolved absolute targets must strictly start with the canonical material root directory separator.
4. **Existence & Type Check**: The target must exist on disk as a regular file (`os.path.isfile`).
5. **Fail-Closed Fallback**: If any security check fails or file is missing, resolution fails closed to `status="fallback"`.

---

## 6. Truthful Provenance & Licensing Policy

All repository material assets carry explicit, truthful provenance metadata.

### Proof Asset Provenance:
- **`japan-ink-mark`**: Author: `"Programmatically generated SVG for MultiMind AI"`, License: `"MultiMind AI Project Terms"`, Reference IP: `"Traditional Japanese print/ink arts"`.
- **`chainsaw-hazard-mark`**: Author: `"Programmatically generated SVG for MultiMind AI"`, License: `"MultiMind AI Project Terms"`, Reference IP: `"Generic industrial hazard visual language"`.
- **`mushishi-moss-mark`**: Author: `"Programmatically generated SVG for MultiMind AI"`, License: `"MultiMind AI Project Terms"`, Reference IP: `"Natural atmospheric graphic language"`.

### Licensing Hard Rules:
- Proof assets record truthful project terms rather than claiming unsupported external open-source licenses.
- No copyrighted third-party artwork, manga panels, or character silhouettes.
- Generic industrial hazard geometry is used for Chainsaw-inspired proof without reproducing protected trademarks or character artwork.
- Technical proof assets are truthfully attributed as programmatically generated project assets.

---

## 7. Generic Resolution & Presentation Seam

### Generic Material Resolver (`ui/dna/resolver.py`)
Provides deterministic resolution without theme-specific branching (`if theme == "mushishi"`):

1. **Direct DNA Lookup**: Checks `DNARegistry.get_dna(theme_or_dna_id)`.
2. **Custom Theme Provenance Lookup**: For custom themes (e.g. from Theme Studio), parses `theme.metadata.reference` (e.g. `"dna:japan-print-ink"`) to resolve the underlying source DNA.
3. **Unbound / Ordinary Themes**: Return `status="fallback"` safely.

### Presentation Seam (`ui/presentation/brand.py`)
The `render_brand_identity()` helper consumes the resolver and renders using safe Streamlit image primitives (`st.image(resolved_path, width=32)`) with bounded sizing:

- **Sidebar Header**: `app.py` sidebar renders material branding via `render_brand_identity()`.
- **Theme Studio Live Preview**: `ui/theme_studio/surface.py` preview surface consumes the exact same `render_brand_identity()` seam.
- **Zero Unsafe HTML SVG Injection**: Asset rendering uses Streamlit image primitives rather than injecting raw SVG strings into `unsafe_allow_html`.

---

## 8. Exact Procedure for Adding a Future Material / Theme

Future theme expansion requires zero architecture or presentation code changes:

1. **Add Approved Asset**: Place local SVG/PNG file in `ui/assets/materials/<material_id>/<asset_filename>`.
2. **Define Provenance & MaterialReference**: Create a `MaterialReference` with truthful provenance metadata, `material_type="graphic_mark"`, and valid `asset_path`.
3. **Bind to DesignDNA**: Attach the `MaterialReference` to a `DesignDNA.materials` list.
4. **Register DNA**: Register the `DesignDNA` with `DNARegistry` (which maps automatically to `ThemeRegistry` via `bootstrap.py`).
5. **Add Tests**: Verify asset resolution, path containment, and fallback behavior in test suite.

---

## 9. Verification & Test Obligations

All test obligations have been implemented and verified in `tests/test_material_pipeline.py`:

- MaterialReference `asset_path` compatibility and existing validation rules
- Valid repository material resolution for all 3 proof DNAs
- Absolute path rejection (`/etc/passwd`)
- Path traversal rejection (`../../etc/passwd`)
- Normalized path containment verification
- Deterministic resolution when process working directory (`os.chdir()`) differs from repo root
- Unsupported material type safety rejection (`SUPPORTED_MATERIAL_TYPES = {"graphic_mark"}`)
- Missing asset fallback
- Invalid/unbound theme fallback
- Scope lock / non-shared material ownership enforcement
- Custom Theme Studio theme derived from DNA resolves correct source material
- Sidebar and Theme Studio share the identical resolver contract
- Containment lock preventing asset escape from `ui/assets/materials`
