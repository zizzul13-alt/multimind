# MULTIMIND — PRIVATE DESIGN-DNA EXTRACTION IMPLEMENTATION

Status: IMPLEMENTED ON REVIEW BRANCH / NOT GOVERNOR ACCEPTED

Public extraction branch removes the M12 private-owned runtime and research roots from the current public tree while retaining `ui/dna_bridge.py` as the supported host-facing seam.

Private target: `zizzul13-alt/multimind-design-dna`

Exact private extraction source: `57bced06a417e026cd97fdf6170cb04abcf67d82` (M12 durable closure).

Public history is NOT sanitized by this change. Historical public commits remain historical public commits.

The first public absent-package regression exposed two residual S8 semantic tests that still directly imported the historical DNA shims. They are Design-DNA/presentation-contract tests, not public absent-package host tests, and have been moved to the private extraction test inventory rather than restoring a reverse dependency from the public repository.

Required before acceptance:
- public app/regression PASS with private package absent;
- private package structural/runtime PASS;
- cross-repository proof with private package present;
- broken/incompatible private package safe fallback proof;
- diff audit confirming no DB/provider/core semantic changes.
