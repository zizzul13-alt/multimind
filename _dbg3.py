"""Why is music_dna_choices MISSING while draft_identity_choice is set?"""
from multimind_reflex.workspace_dna_state import (
    WorkspaceDnaState,
    _music_dna_choice_snapshots,
)

snaps = _music_dna_choice_snapshots()
print("seed func returns len:", len(snaps))
print("seed first:", snaps[0] if snaps else None)

mc = WorkspaceDnaState.__fields__["music_dna_choices"]
print("music_dna_choices default:", mc.default, "| factory:", getattr(mc, "default_factory", None))

import multimind_reflex.state as base
print("--- base list-ish fields (how a GOOD list field is declared) ---")
for name, f in base.HostState.__fields__.items():
    ann = str(f.annotation).lower()
    if "list" in ann:
        print(f"  {name}: default={f.default!r} factory={getattr(f, 'default_factory', None)}")

print("--- workspace_dna list fields ---")
for name, f in WorkspaceDnaState.__fields__.items():
    ann = str(f.annotation).lower()
    if "list" in ann:
        print(f"  {name}: default={f.default!r} factory={getattr(f, 'default_factory', None)}")
