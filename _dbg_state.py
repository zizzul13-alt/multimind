import reflex as rx
from multimind_reflex.state import HostState

s = HostState()
print("=== REAL HostState instance values ===")
for f in ['dna_runtime_available', 'private_theme_studio_available',
          'draft_identity_choice', 'draft_identity_dna', 'current_surface', 'logged_in']:
    try:
        print(f"  {f}: {getattr(s, f)!r}")
    except Exception as e:
        print(f"  {f}: ERR {e}")
try:
    mc = getattr(s, 'music_dna_choices')
    print(f"  music_dna_choices: len={len(mc)} first={mc[0] if mc else None}")
except Exception as e:
    print(f"  music_dna_choices: ERR {e}")
