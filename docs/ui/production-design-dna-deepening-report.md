# MultiMind AI - Production Design DNA Deepening Report (S8.2)

## 1. Production Semantic Contract

S8.2 upgrades MultiMind AI's Design DNA architecture from proof-level definitions to production-depth contracts. 

The 9 new semantic fields added to `DesignDNA` (`ui/dna/models.py`) represent structured visual, spatial, and design intent without containing pixel coordinates, arbitrary CSS strings, Streamlit UI code, or hardcoded layout breakpoints:

- `visual_energy`: `Optional[str]`
- `spatial_density`: `Optional[str]`
- `composition_balance`: `Optional[str]`
- `hierarchy_strength`: `Optional[str]`
- `surface_character`: `Optional[str]`
- `shape_character`: `Optional[str]`
- `ornament_emphasis`: `Optional[str]`
- `interaction_intensity`: `Optional[str]`
- `responsive_identity_priority`: `Optional[str]`

All 9 fields are default-safe (`Optional[str] = None`) to preserve 100% backward compatibility with legacy and minimal `DesignDNA` definitions (T27). When populated, values are validated strictly against bounded taxonomy sets.

---

## 2. Exact Controlled Vocabulary

| Semantic Dimension | Allowed Bounded Vocabulary Values |
| :--- | :--- |
| **`visual_energy`** | `quiet`, `restrained`, `balanced`, `expressive`, `aggressive` |
| **`spatial_density`** | `spacious`, `balanced`, `compact`, `dense` |
| **`composition_balance`** | `regular`, `asymmetric`, `organic` |
| **`hierarchy_strength`** | `soft`, `moderate`, `strong`, `dramatic` |
| **`surface_character`** | `flat`, `layered`, `paper`, `atmospheric`, `poster` |
| **`shape_character`** | `soft`, `restrained`, `sharp`, `organic` |
| **`ornament_emphasis`** | `none`, `subtle`, `selective`, `prominent` |
| **`interaction_intensity`** | `gentle`, `restrained`, `deliberate`, `assertive` |
| **`responsive_identity_priority`** | `minimal`, `preserve_core`, `preserve_strong` |

---

## 3. Canonical Profile Table for All 5 DNAs

| Field | Rinpa Decorative Spatial (`rinpa-decorative-spatial`) | Japan Print / Ink (`japan-print-ink`) | Chainsaw Man Inspired (`chainsaw-man-inspired`) | Mushishi Inspired (`mushishi-inspired`) | Japan High-Density Information (`japan-high-density-info`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Role** | `identity` | `identity` | `identity` | `identity` | `web_information` |
| **`visual_energy`** | `expressive` | `balanced` | `aggressive` | `quiet` | `None` |
| **`spatial_density`** | `spacious` | `balanced` | `dense` | `spacious` | `None` |
| **`composition_balance`** | `asymmetric` | `regular` | `asymmetric` | `organic` | `None` |
| **`hierarchy_strength`** | `strong` | `strong` | `dramatic` | `soft` | `None` |
| **`surface_character`** | `layered` | `paper` | `poster` | `atmospheric` | `None` |
| **`shape_character`** | `organic` | `restrained` | `sharp` | `organic` | `None` |
| **`ornament_emphasis`** | `selective` | `subtle` | `prominent` | `subtle` | `None` |
| **`interaction_intensity`** | `deliberate` | `deliberate` | `assertive` | `gentle` | `None` |
| **`responsive_identity_priority`** | `preserve_strong` | `preserve_core` | `preserve_strong` | `preserve_core` | `None` |
| **`presentation_policy`** | `None` | `None` | `None` | `None` | `metadata_prominence="high"`, `status_richness="rich"`, `navigation_density="compact"`, `secondary_compactness=True`, `utility_grouping="structured"` |

---

## 4. MAPPED_NOW / PRESENTATION_POLICY / DEFERRED Classification

For each production semantic dimension, its system classification is:

1. **`visual_energy`** ➔ **DEFERRED**
2. **`spatial_density`** ➔ **DEFERRED**
3. **`composition_balance`** ➔ **DEFERRED**
4. **`hierarchy_strength`** ➔ **DEFERRED**
5. **`surface_character`** ➔ **DEFERRED**
6. **`shape_character`** ➔ **DEFERRED**
7. **`ornament_emphasis`** ➔ **DEFERRED**
8. **`interaction_intensity`** ➔ **DEFERRED**
9. **`responsive_identity_priority`** ➔ **DEFERRED**

*(Note: Secondary information density and metadata prominence are classified as **`PRESENTATION_POLICY`** owned by `PresentationPolicy` on Web/Information DNA. Visual token mapping for palette, font stacks, spacing grids, and border radii pass directly via **`MAPPED_NOW`** in `dna_to_theme()`).*

---

## 5. Material Ownership

The existing Material Pipeline (`ui/dna/resolver.py`, `ui/dna/registry.py`) remains 100% authoritative:
- Identity DNA owns primary graphic mark and visual material references (`rinpa-gold-mark`, `japan-ink-mark`, `chainsaw-hazard-mark`, `mushishi-moss-mark`).
- All material asset path containment checks and fallback mechanisms are strictly preserved without duplicate resolvers or scraped assets.

---

## 6. Composition Ownership

Subsystem responsibilities remain strictly decoupled:
- **IDENTITY DNA**: Owns primary visual identity, Theme token palette/font/radius, spatial character intent, and primary graphic mark.
- **WEB / INFORMATION DNA**: Owns bounded `PresentationPolicy` (metadata prominence, status richness, navigation density, secondary compactness, utility grouping).
- **UI / UX ARCHETYPE**: Owns interaction morphology, workspace structure, and application shell flow.
- **THEME ENGINE**: Owns `--mm-*` CSS custom properties mapping.
- **MATERIAL PIPELINE**: Owns material references and fallback resolution.

---

## 7. Theme Studio Relationship

Theme Studio (`ui/theme_studio/`) state invariants remain intact:
- Draft state (`ThemeStudioDraft`) is isolated from active session application state until explicitly applied (`apply_draft_to_active_theme`).
- Reset/Discard (`reset_draft_to_base`) preserves currently selected composition role IDs while restoring default token values.
- All 4 canonical Identity DNAs and 1 Web/Information DNA are fully exposed in Theme Studio selectors.

---

## 8. Responsive Semantics

Responsive identity priorities (`minimal`, `preserve_core`, `preserve_strong`) express semantic intent for how strongly identity visual cues should survive layout compaction on small screens.

They strictly contain **zero**:
- CSS breakpoints
- Pixel values or media queries
- DOM positioning instructions

---

## 9. Synthetic Future DNA Extension Procedure

To add a synthetic or production Identity/Web DNA without editing generic resolution code:
1. Define a `DesignDNA` instance with `role="identity"` or `role="web_information"`.
2. Populate required contract fields and optional production semantic fields using bounded vocabulary.
3. Call `register_dna(new_dna)`.
4. Compose via `resolve_composition(DesignComposition(identity_dna_id="new-dna-id", ...))`.

Resolution occurs generically without any hardcoded `if dna.id == ...` branches.

---

## 10. VISUAL REALITY TABLE

| DIMENSION | CONTRACT EXISTS | CURRENT CONSUMER | STATUS |
| :--- | :--- | :--- | :--- |
| **`visual_energy`** | yes | NONE | `NOT_YET_CONSUMED` |
| **`spatial_density`** | yes | NONE | `NOT_YET_CONSUMED` |
| **`composition_balance`** | yes | NONE | `NOT_YET_CONSUMED` |
| **`hierarchy_strength`** | yes | NONE | `NOT_YET_CONSUMED` |
| **`surface_character`** | yes | NONE | `NOT_YET_CONSUMED` |
| **`shape_character`** | yes | NONE | `NOT_YET_CONSUMED` |
| **`ornament_emphasis`** | yes | NONE | `NOT_YET_CONSUMED` |
| **`interaction_intensity`** | yes | NONE | `NOT_YET_CONSUMED` |
| **`responsive_identity_priority`** | yes | NONE | `NOT_YET_CONSUMED` |
| **`metadata_prominence`** | yes | `ui/theme_studio/surface.py` | `PARTIALLY_VISIBLE` |
| **`status_richness`** | yes | `ui/theme_studio/surface.py` | `PARTIALLY_VISIBLE` |
| **`secondary_compactness`** | yes | `ui/theme_studio/surface.py` | `PARTIALLY_VISIBLE` |

---

## 11. Known Presentation Limitations

- Production semantic dimensions (`visual_energy`, `spatial_density`, `composition_balance`, `hierarchy_strength`, `surface_character`, `shape_character`, `ornament_emphasis`, `interaction_intensity`, `responsive_identity_priority`) are formally tracked as validated design intent in the semantic contract layer (`DesignDNA`), but are not yet visually rendered or transformed into CSS custom properties by the asset-free S5 Theme Engine.
- They are intentionally classified as `DEFERRED` / `NOT_YET_CONSUMED` to avoid fake visual mappings or brittle CSS hacks.
- Current `PresentationPolicy` values are exposed in Theme Studio preview/summary surfaces, but the main archetype projections do not yet consume them as a data-driven presentation contract. Therefore these policy dimensions are classified as `PARTIALLY_VISIBLE`, not `VISIBLE_NOW`.
