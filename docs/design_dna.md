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

## Controlled Design Vocabulary v1

### Overview & Architectural Principle

Controlled Design Vocabulary v1 establishes standard definitions for visual and design intent terms used within MultiMind AI Design DNA.

Vocabulary terms describe **DESIGN INTENT**, not direct CSS properties or physical artifacts.
The conceptual flow is strictly:

```
Vocabulary Term (Design Intent)
        ↓
DesignDNA Descriptive Fields
        ↓
Supported Semantic Token Mapping (colors, typography, spacing, radius)
        ↓
Theme Contract
        ↓
Theme Engine (`--mm-*` CSS custom properties)
```

If a vocabulary characteristic cannot be represented by the asset-free Theme Engine, it is classified explicitly as deferred rather than bypassed with arbitrary CSS or layout hacks.

---

### Term Definitions & Capabilities

#### 1. INK
- **Design Intent**: A printed or hand-drawn mark language characterized by strong dark marks, pen/brush impression, variable visual density, and print-like contrast.
- **What it is NOT**: It does NOT mean simply applying `#000000` black color, nor does it authorize physical ink splatter textures, canvas image backgrounds, or SVG brush filters.
- **Supported Mapping**: High contrast dark foreground text against warm/paper surfaces (`#111111` or `#1A1A1A`), deliberate typography weights, and firm borders.
- **Classification**: **Representable Now** (via semantic color contrast and typography hierarchy). Physical brush strokes/textures are **Asset-Dependent (Deferred)**.

#### 2. PAPER
- **Design Intent**: A surface language suggesting printed physical media through warm/off-white or restrained surface relationships and controlled contrast.
- **What it is NOT**: It does NOT require or permit a paper texture noise image, background image pattern, or physical page curl shadows.
- **Supported Mapping**: Warm light surface and background tones (`#F7F4EB`, `#EFECE2`, `#E5E0D8`), subtle warm borders (`#D6D0C4`), and soft non-pure-black text (`#222222`).
- **Classification**: **Representable Now** (via semantic surface and background token palette). Texture images are **Asset-Dependent (Deferred)**.

#### 3. PRINT
- **Design Intent**: A graphic language influenced by physical/editorial printing: deliberate contrast, restrained palette, clear typography hierarchy, and tactile visual direction.
- **What it is NOT**: Faking print artifacts, halftone dots, offset registration errors, or noise overlays via arbitrary CSS.
- **Supported Mapping**: High contrast body/heading text, structured line-heights, restrained accent usage, and clean solid surface borders.
- **Classification**: **Representable Now** (via typography roles and surface/border tokens). Halftone or grain effects are **Asset-Dependent (Deferred)**.

#### 4. EDITORIAL
- **Design Intent**: Strong, structured typography and information hierarchy that leads the reader's eye naturally.
- **What it is NOT**: Reorganizing application layout, altering sidebar placement, or redesigning Streamlit components.
- **Supported Mapping**: Distinct font weight and size contrasts across display, heading, subheading, body, and label typography roles.
- **Classification**: **Representable Now** (via typography scale and weight roles). Multi-column grid changes are **Layout-Dependent (Unsupported)**.

#### 5. POSTER
- **Design Intent**: Assertive graphic emphasis created through strong contrast, impactful accent relationships, and visual hierarchy.
- **What it is NOT**: Converting application pages into marketing poster compositions or injecting large background banners.
- **Supported Mapping**: High-saturation or bold accent tokens (`#E63946`, `#FF3300`), stark surface-to-background contrast, and bold font weights.
- **Classification**: **Representable Now** (via accent color and typography weight roles). Full-bleed poster layouts are **Layout-Dependent / Unintended**.

#### 6. ROUGH
- **Design Intent**: Controlled visual harshness, energy, or firmness in visual character.
- **What it is NOT**: Random CSS noise, jagged border hacks, broken alignment, or reduced usability.
- **Supported Mapping**: Sharper radii (`0px`), stark contrast borders, and high-energy accent pairings.
- **Classification**: **Representable Now** (via radius and border tokens). Jagged/distressed vector masks are **Asset-Dependent (Deferred)**.

#### 7. ORGANIC
- **Design Intent**: Natural and less mechanical visual relationships, expressed through restrained colors, softer contrast, and compatible rounded geometry.
- **What it is NOT**: Skewed layouts, fluid canvas animations, or leaf/plant illustration backgrounds.
- **Supported Mapping**: Natural muted hues (moss greens, earth beige, slate gray), soft radii (`0.5rem` - `0.75rem`), and gentle surface elevation steps.
- **Classification**: **Representable Now** (via palette and radius tokens). Organic background shapes are **Asset-Dependent (Deferred)**.

#### 8. ATMOSPHERIC
- **Design Intent**: Immersive mood produced primarily through deliberate color palette, subtle surface layering, and controlled contrast.
- **What it is NOT**: Background photography, video loops, ambient audio, or blurred photo backdrops.
- **Supported Mapping**: Deep surface tones, subtle surface hover elevations, and harmonious text-to-background contrast ratios.
- **Classification**: **Representable Now** (via surface token hierarchy). Photo backdrops are **Asset-Dependent (Deferred)**.

#### 9. SHARP
- **Design Intent**: A firm, crisp visual character expressed through geometry, stark border contrast, and exact hierarchy.
- **What it is NOT**: Modifying component structure or injecting structural CSS grid overrides.
- **Supported Mapping**: Zero or minimal border radii (`0px` or `2px`), defined border colors, and clean font pairings.
- **Classification**: **Representable Now** (via radius and border tokens).

#### 10. CALM
- **Design Intent**: Restrained accents, comfortable visual rhythm, softer contrast hierarchy, and reduced visual aggression.
- **What it is NOT**: Excessive whitespace that breaks application layout or alters S4 page composition.
- **Supported Mapping**: Low-saturation accents, comfortable typography line-heights, and soft border/surface transitions.
- **Classification**: **Representable Now** (via color saturation and spacing tokens).

#### 11. HIGH CONTRAST
- **Design Intent**: Strong semantic separation between text, surfaces, borders, accents, and interactive states while maintaining readability/accessibility.
- **What it is NOT**: Unusable or eye-searing neon combinations that violate accessibility guidelines.
- **Supported Mapping**: Explicit color tokens guaranteeing high WCAG contrast ratios across background, surface, text, and focus states.
- **Classification**: **Representable Now** (via semantic color tokens).

#### 12. MUTED
- **Design Intent**: Reduced color saturation and intensity while preserving legibility, interaction clarity, and state distinction.
- **What it is NOT**: Low-contrast unreadable text or invisible input borders.
- **Supported Mapping**: Softened palette values with preserved minimum WCAG text contrast and distinct hover/focus state feedback.
- **Classification**: **Representable Now** (via semantic color tokens).

---

### S6.2 Proof DNA Vocabulary Mapping Summary

| Real Proof DNA | Primary Vocabulary Emphasis | Key Semantic Implementation |
| :--- | :--- | :--- |
| **Japan Print / Ink** (`japan-print-ink`) | `ink`, `paper`, `print`, `editorial`, `restrained`, `high-contrast` | Dark ink text (`#121212`) on warm paper surface (`#F5F2EB`), stark borders (`#222222`), firm small radii (`2px`), print-like serif-compatible font stacks. |
| **Chainsaw Man Inspired** (`chainsaw-man-inspired`) | `poster`, `editorial`, `rough`, `sharp`, `high-contrast` | Stark dark asphalt background (`#111114`), assertive warning yellow (`#FFCC00`) & visceral red (`#E63946`) accents, zero radius (`0px`), crisp bold typography hierarchy. |
| **Mushishi Inspired** (`mushishi-inspired`) | `organic`, `atmospheric`, `calm`, `muted`, `restrained` | Deep forest moss background (`#111814`), soft sage surface (`#1D2822`), pale green-tinted text (`#E2EBE5`), calm muted tea accent (`#7A9A8B`), softer radii (`8px` - `12px`). |
