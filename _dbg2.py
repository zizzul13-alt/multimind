"""Debug: verify the exact state class the app uses, via its real import path."""
import multimind_reflex.multimind_reflex as app_mod

# The app aliases WorkspaceDnaState as HostState
HostState = app_mod.HostState
print("HostState is:", HostState.__module__, "->", HostState.__name__)

# Reflex state fields are descriptors; read the raw default from __fields__
fields = HostState.__fields__
for name in ["dna_runtime_available", "draft_identity_choice", "draft_identity_dna"]:
    f = fields.get(name)
    if f is not None:
        print(f"  {name} = {f.default!r}")
    else:
        print(f"  {name} = <NOT A FIELD>")

# music_dna_choices
mc = fields.get("music_dna_choices")
if mc is not None:
    d = mc.default
    try:
        print(f"  music_dna_choices = len {len(d)} first={d[0] if d else None}")
    except Exception:
        print(f"  music_dna_choices = {d!r}")
