# I3-P01 production EVENT verification

## Scope and result

The production `RootStore` accepts ordered external LEARN events, executes the
existing I2 two-pass kernel over frozen W/H/R, commits the approved sensory
cohort and latent topology, and atomically checkpoints W/R/H and its typed
observation journal in SQLite. BEGIN and ABORT preserve a non-reusable root
high watermark; ABORT restores the exact H_BEGIN bytes and retains lawful
sensory births. Production END remains blocked and no synapse, evidence,
completed root, contextual owner, Assembly or generation is created here.

This is a P01 implementation result, **not evidence of learning or real-world
truth**. `EXTERNAL_DIRECT` records a validated API input, not independent
semantic certification. Python-private guards and the stored SHA-256
checkpoints are integrity and process-boundary checks, not authentication
against a malicious process able to rewrite the whole database. The supplied
code-revision string is recorded identity metadata, not proof of Git identity.

## Changes and scientific sources

Branch `feature/i3-local-learning`; approved P01 contract parent
`0250181d1893c7827a08eb599b88b52f062eda87`; implementation commit
`991d206382352ba0a907c5ca06c9d515b586fcdf`. The report and final END-rejection
regression are committed separately; their commit is read from Git history,
avoiding a self-referential SHA.

Changed paths relative to the P01 parent:

- `README.md`;
- `src/dgca_next/graph/audit.py`, `cell.py`, `latent.py`, `network.py`,
  `production.py`;
- `src/dgca_next/learning/production_event.py`;
- `src/dgca_next/persistence/graph_codec.py`, `production_store.py`, `store.py`;
- `tests/test_graph_cells.py`, `tests/test_i3_r01_root_store.py`,
  `tests/test_i3_p01_production_event.py`;
- `docs/implementation/I3-P01-PRODUCTION-EVENT-VERIFICATION-REPORT.md`.

The two prior assertions changed only where the authorized API changes the
behavior: physical `Cell` now includes admission provenance, and a fresh
production store now initializes the approved H profile rather than requiring
caller-supplied H. Explicit caller H still selects the old **fixture-only,
fail-closed** skeleton; its files are not silently promoted into production.
Existing fixture graph writers reject production graphs.

The scientific source files are unchanged from the P01 parent. Integrity check
SHA-256: Core RC4.4
`3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c`;
LLA RC4.4
`ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0`.

## Actual production event trace

The following observations were obtained using `RootStore` against a new
temporary SQLite database, with caller-declared test code revision `a` repeated
40 times. The input is an external API submission of `(("a", "1"),)`; the
literal feature is not a semantic answer or label.

- `BEGIN_EXPOSURE(1)`, then `EVENT(1, 0, (("a", "1"),))` succeeds. Its
  global event ID is `0`, event order is `0`, and the first hard-boundary flag
  is normalized true. Origin and mode are typed `EXTERNAL_DIRECT` and `LEARN`.
- Observation digest:
  `87265149bf7ca770278f06eab98b2f3ee85ced8d1bbea0d2b954648bb6d86b3e`.
  Direct `X_fixed` is `1000000` at IDs `8606`, `9345`, `11795`, `12181`.
- Pre-event committed set, pass-1 and final **cell activity**, emitters, and
  F_step are empty. The four uncommitted input positions have raw drive `1.0`
  and normalized drive `0.9090909090909091`; they are not activated as
  committed cells during the event.
- The event commits those four non-fixture physical cells. Each owns 24 typed
  slots; 60 slots are occupied in total and the inverse index has 52 distinct
  target IDs. Graph audit passes, with **0 synapses** and 0 completed roots.
  The canonical W checkpoint SHA-256 is
  `a55c5013ac04fe3043b679f206c84923ada8835aab7ac744d1bb3ee7dca5d552`.
  The OPEN root's next order is 1. A subprocess post-commit exit and independent
  reopen recover the complete checkpoint and original observation.
- H_BEGIN raw bytes have SHA-256
  `b2bb874f7c8df9c7fc5e7398e6f2d4dcc6518eb1387239ba9118a9aa0a0d8da3`.
  The newborn EVENT creates no per-cell overrides and does not change H.

A subsequent event 1 with the same feature sees the four cells as committed
before the event. Each has pass-1 and final activity `0.7272727272727273`,
and all four are emitters and members of F_step. Provisional H has each cell
EMA `0.0975`, gain `0.999905`, LANGUAGE regional EMA `0.0785`, and threshold
`0.20500000000000002`; its raw SHA-256 is
`8665ea2e183c1ec33d2d896a746d56952f9c6586146368ca37a2d455dd8b83f9`.
After closing and reopening the database, next order is 2, W and the earlier
witness are unchanged. ABORT restores the exact original H bytes and SHA-256
`b2bb874f7c8df9c7fc5e7398e6f2d4dcc6518eb1387239ba9118a9aa0a0d8da3`;
all four cells and W hash remain. The root high watermark is 1 and completed
root count remains 0. Duplicate ABORT is idempotent.

With cold inputs `(a,1),(ab,1),(c,1),(d,1)`, the 16-way production event
admits IDs `8286, 8465, 8606, 8649, 8694, 9227, 9345, 9902, 9912, 10128,
10273, 10513` and reports deferred IDs `11524, 11641, 11795, 12181`. After
ABORT, a new root's observation admits the four deferred IDs and does not
rebirth the earlier 12. Their distinct global event identities and physical
indices remain in the journal. These are structural EVENT results, not links.

## Failure and recovery coverage

The production tests submit actual inputs through `RootStore`; no fixture graph
or fabricated observation is used to obtain the mandatory birth. They cover
invalid features and order, duplicate order, empty valid event, two connections
and exclusive OPEN state, canonical graph round-trip, damaged profile/schema
and reverse index, corrupt event checksum, immutable witness construction,
read-only processing after ABORT without W/H mutation, hard-boundary reset,
and the difference between learning and temporal frontiers during later birth.

Subprocess `os._exit(71)` tests stop immediately before and after SQLite commit
for BEGIN, first EVENT, adapting EVENT, and ABORT. Reopening yields the exact
pre-commit state or the entire post-commit checkpoint: no orphan witness,
partial W/H/R state, duplicated event order or doubled adaptation. A post-birth
reopen audits the graph and inverse index; after ABORT it keeps W and recovers
the exact H_BEGIN bytes. No neural event or H adaptation is rerun on reload.
Checksums detect accidental corruption but are not a cryptographic trust
boundary against an actor who can replace all data and checksums.

## Validation results

Local Windows / Python 3.14:

| Exact command | Result |
| --- | --- |
| `.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp -rs` | **PASS:** `664 passed in 30.35s`; no skips, including the previous 640 tests. |
| `.venv\Scripts\python.exe -m pytest -q tests/test_i3_p01_production_event.py --basetemp=.pytest-tmp -rs` | **PASS:** `24 passed in 7.26s`, including the final production END-rejection assertion. |
| `.venv\Scripts\python.exe -m ruff check .` | **PASS:** `All checks passed!` |
| `.venv\Scripts\python.exe -m ruff format --check .` | **PASS:** `76 files already formatted`. |
| `.venv\Scripts\python.exe -m mypy` | **PASS:** `Success: no issues found in 43 source files`. |
| `.venv\Scripts\python.exe -m dgca_next verify-specs` | **PASS:** both RC4.4 hashes above. |
| `.venv\Scripts\python.exe -m pip check` | **PASS:** `No broken requirements found.` |
| `git diff --check` | **PASS:** no output. |
| `git diff --exit-code 0250181 -- docs/specs` | **PASS:** exit 0; the scientific sources are unchanged. |
| `git status --porcelain` at implementation commit | **PASS:** no tracked or untracked changes. |

**FAIL:** none in final local validation. **NOT_RUN:** P02 END and evidence,
production synaptic learning, and full I3 empirical gates; these are outside
P01. **SPEC_BLOCKED:** none identified for this slice. The implementation-head
CI run [40746217794](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/40746217794)
completed **PASS on Ubuntu and Windows** for commit
`991d206382352ba0a907c5ca06c9d515b586fcdf`.
The report commit triggers a distinct final-head run; its status and SHA must
be checked in the [branch workflow history](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/workflows/validate.yml?query=branch%3Afeature%2Fi3-local-learning).

## P01 acceptance gates

| Gate | Verdict at report creation | Evidence |
| --- | --- | --- |
| P01-G01 | **PASS** | Production EVENT accepts `a`, records typed external witness and advances order atomically. |
| P01-G02 | **PASS** | Four-cell and 16→12→4 production cohorts, 24 slots per cell, independent graph/reverse audit, no synapses. |
| P01-G03 | **PASS** | Frozen pre-event W/H/R and actual I2 passes, direct input, temporal/synchronous lanes, emitters and frontiers are journaled. |
| P01-G04 | **PASS** | Virtual defaults, no newborn adaptation; adapted H restores byte-for-byte on ABORT with W retained. |
| P01-G05 | **PASS** | W/R/H and observation round-trip, independent reopen of OPEN root and next order, read-only after ABORT. |
| P01-G06 | **PASS** | Before/after process crashes for BEGIN/EVENT/ABORT, rejected duplicate order, malformed and corrupted records; END remains blocked. |
| P01-G07 | **NOT_RUN** at report creation | Local regression/static/integrity checks pass; exact final-head Ubuntu/Windows CI is pending the report commit. |
| P01-G08 | **PASS** | This report records actual production traces and limits; no learning is claimed. |

P01 may be called **I3-P01 REVIEW READY** only after both final-head CI jobs
pass. Full I3 remains partial; P02 requires separate authorization and review.
