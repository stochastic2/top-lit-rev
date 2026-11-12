# Superseded development experiment

This twenty-attempt run tested a preliminary circuit that rejected every
nonzero terminal flag. It accepted 1/20 and was superseded by the certified
flag-repair and protected-recovery controller. Its artifacts predate the
final flag-policy/version fields and complete flag logging; do not use it
as a run of the current `compact_flagged` profile or with the current verifier.

The final implementation and validated fifty-attempt run are documented in
[the compact-terminal note](../../notes/compact_terminal_extraction.md) and
[the final comparison](../c4-helix-compact-terminal-comparison.json).
