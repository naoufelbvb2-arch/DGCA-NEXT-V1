# Final lifecycle evidence — provenance boundaries

Only the explicitly authorized final experimental branch is used. All accepted
production source, scientific parameters, encodings and capabilities remain
unchanged. These drivers submit external physical feature bundles through
`RootStore`; they never use FixtureBuilder or supply a caller-created synapse,
Assembly identity, membership, weight or positive-evidence witness.

The append-only [declarations](../../I4-FINAL-LIFECYCLE-CLOSEOUT-CHANGELOG.md)
precede each executed curriculum. The final report distinguishes actual
publication, read-only component measurements, negative controls and unexecuted
cases. Long local experiments are not silently described as rerun by CI.

## Original authenticated source

Original accepted R04 F05-r3 publication, unchanged database file SHA256:
`c4febc61a86b233bd4d0115a9da660e31c3bd4f3c1b5b8a00ab204ac04e23323`.
Receipt: `../i4-r04-autonomous/F05-r3-publish.json`. The database is retained
locally at `.pytest-tmp/r04-operators/F05-r3-publish.sqlite`; its large SQLite
file is not committed. Its full original event/END history is cold rederived
by the accepted RootStore before new external events are accepted. Its initial
revision is retained as database identity, independently of each new driver's
executing Git revision.

Reproduction of that original history starts with the accepted R04 F05-r3
curriculum and conditional operator-publication drivers documented in the
[accepted R04 report](../../I4-R04-AUTONOMOUS-CONSOLIDATED-VERIFICATION-REPORT.md).
SQLite file layout/hash need not match a new independent backend execution;
physical W/H/R, event provenance and operator measurements are separate checks.
No new file hash is silently substituted for the retained original source.

## A01-r1 continuation

```powershell
.venv/Scripts/python.exe tests/experiments/i4_final_lifecycle_closeout.py --source .pytest-tmp/r04-operators/F05-r3-publish.sqlite --source-receipt docs/implementation/evidence/i4-r04-autonomous/F05-r3-publish.json --database .pytest-tmp/i4-final-closeout/A01-r1.sqlite --output docs/implementation/evidence/i4-final-closeout/A01-r1.json
```

All target paths must be new. The actual trace stops at the first terminal
MAINTAIN archive. It retains every event and accepted/refused root proposal,
actual structural scores and mutations, W/H/R hashes, old physical credits
and cold-recovery result. Raw binary EVENT bytes are represented by their
canonical digest and complete numerical/provenance fields in the JSON.

The six transaction/falsification controls each copy the same genuine OPEN
pre-archive checkpoint, not a numeric graph. They are **not** additional
independent learning roots or extra confirmations of the same link.

```powershell
.venv/Scripts/python.exe tests/experiments/i4_final_archive_controls.py --source .pytest-tmp/i4-final-closeout/A01-r1.before-archive.sqlite --receipt docs/implementation/evidence/i4-final-closeout/A01-r1.json --database .pytest-tmp/i4-final-closeout/A01-publish.sqlite --output docs/implementation/evidence/i4-final-closeout/A01-publish.json --case publish
```

Repeat with distinct new database/output paths for `abort`, `BEFORE_COMMIT`,
`AFTER_COMMIT`, `forged_score`, `forged_lineage`. Original files are not altered
by corruption controls. Hash repair alone is never historical authority.
The saved-state pytest cases are component checks of these actual artifacts;
they are not a second execution of the long production curricula.
