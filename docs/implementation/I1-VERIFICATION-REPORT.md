# I1 verification report

Date: 2026-10-27 (America/New_York).
Status: **I1 PARTIAL / POLICY_BLOCKED — verified structural subset delivered**.
Repository: `naoufelbvb2-arch/DGCA-NEXT-V1`.
Only implementation branch: `feature/i1-graph-anatomy`.

The three structural increments were implemented, tested and committed in order.
Production latent initialization and confirmation-window recycling remain
`UNRESOLVED_LATENT_POLICY`. No heuristic was substituted. The mandatory overall
I1 completion condition in contract §6 is therefore unsatisfied. This is not an
I1 COMPLETE or I2 authorization.

## Base, commits and source integrity

| Reference | SHA |
|---|---|
| Accepted I0 main base | `fdcd3ea3c85b9c7484e89d043188a59d49907b71` |
| Starting I1 branch, including approved contract | `695034e2f7a73f555cfaf537ffa7a6f42885df29` |
| I1-R01 anatomy | `e439030cad74cb79f26063d3757138eef04eb40a` |
| I1-R02 connectivity | `219ddef2eda30a17728bfc878fbf8c239872a2d4` |
| I1-R03 tested implementation | `f62d5eb1739d1e8a18a8427c65ffe354c47ac591` |

The delivery adds this report to the tested implementation. Its final SHA is
given in the completion message; resolve this report's own commit with
`git log -1 --format=%H -- docs/implementation/I1-VERIFICATION-REPORT.md`.
No self-referential commit hash is embedded here.

Both RC4.1 specs, the source manifest, both I0 reports/contracts, the approved I1
contract, all existing I0 source files, `pyproject.toml`, and all four I0 test
modules are unchanged. No merge, force push, main change or other-repository edit
was performed. Branch ancestry to the accepted main base was checked before code.

Exact integrity output, also obtained before implementation:

```text
PASS docs/specs/DGCA_CORE_RC4_1.md SHA-256=f9d57129b773a93cf8603cdf2df0f6530364200ddea7ce7a070101491800a92d
PASS docs/specs/DGCA_LLA_RC4_1.md SHA-256=67d98d3e34aa0edeac2c77b955c0a0e489d3b6aac89f86959a8b626c4b4d2b69
```

## Exact changed paths

| Path | Responsibility |
|---|---|
| `src/dgca_next/graph/__init__.py` | Public structural exports |
| `src/dgca_next/graph/cell.py` | Immutable physical commitment/membership metadata |
| `src/dgca_next/graph/geometry.py` | Pure bounded microcolumn geometry |
| `src/dgca_next/graph/latent.py` | 24 typed positions and explicit unresolved-policy diagnostic |
| `src/dgca_next/graph/synapse.py` | Directed fixture records, numerical validation, pure quality |
| `src/dgca_next/graph/budget.py` | Unique outgoing/cross/episodic capacity validation |
| `src/dgca_next/graph/network.py` | Sparse graph, fixture builder, forward/reverse views and shadows |
| `src/dgca_next/graph/transaction.py` | Single-use batch transaction and failure injection |
| `src/dgca_next/graph/audit.py` | Independent state/transition audits |
| `tests/conftest.py` | Explicit synthetic physical fixture factories |
| `tests/test_graph_addresses.py` | Full ID bijection and bounded geometry |
| `tests/test_graph_cells.py` | Lazy reads, immutable metadata, fixture-only commitment |
| `tests/test_graph_latent.py` | Category/region quotas, D, inverse index, pins, policy diagnostics/skips |
| `tests/test_graph_synapses.py` | Scope/time legality, duplicate/timing rules, bounds and fixture Q |
| `tests/test_graph_budgets.py` | Real eligible cap fixtures, shared claims, transfer and independent cap audits |
| `tests/test_graph_transactions.py` | Atomic failures, stale shadows, protection audits, corruption and ordering |
| `tests/test_graph_stress.py` | Full physical network with sparse records, measurements and canonical digest |
| `.github/workflows/validate.yml` | Preserve I0 checks and add I1 feature pushes on Ubuntu/Windows |
| `README.md` | Actual APIs, administrative conventions, commands and policy limitations |
| `docs/implementation/I1-VERIFICATION-REPORT.md` | This report |

## Commands and executed checkpoint evidence

Local environment: Windows, CPython 3.14.4, existing I0 `.venv`, pytest 9.0.2,
Ruff 0.14.14, mypy 1.19.1. No new runtime or development dependency was added.
All shell commands below ran from the repository root. The exact interpreter
prefix was `.\.venv\Scripts\python.exe`.

| Checkpoint | Exact test command | Result |
|---|---|---|
| Baseline, before code | `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp` | `163 passed in 1.39s` |
| I1-R01 | `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp` | `194 passed in 2.16s` |
| I1-R02 | `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp` | `269 passed in 2.32s` |
| Committed I1-R03, final run | `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp` | `314 passed, 2 skipped in 6.10s` |
| Committed I1-R03, repeat with reasons | `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp -rs` | `314 passed, 2 skipped in 6.38s` |

Each increment ran all existing I0 regressions, not only its new tests. Final
distinct test totals: **314 PASS = 163 I0 + 151 I1**, **0 FAIL**, **2 POLICY_BLOCKED
skips**. The two repeat final runs produced 628 passing test executions; they do
not represent 628 distinct tests. Skipped policy executions are never PASS.

Exact final test output:

```text
........................................................................ [ 22%]
........................................................................ [ 45%]
....................................................ss.................. [ 68%]
........................................................................ [ 91%]
............................                                             [100%]
314 passed, 2 skipped in 6.10s
```

Exact repeat output including policy reasons:

```text
........................................................................ [ 22%]
........................................................................ [ 45%]
....................................................ss.................. [ 68%]
........................................................................ [ 91%]
............................                                             [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\test_graph_latent.py:103: POLICY_BLOCKED: UNRESOLVED_LATENT_POLICY, missing original confirmation window
SKIPPED [1] tests\test_graph_latent.py:107: POLICY_BLOCKED: UNRESOLVED_LATENT_POLICY, missing exact inherited target selection
314 passed, 2 skipped in 6.38s
```

| Exact final validation command | Verdict / exact output |
|---|---|
| `.\.venv\Scripts\python.exe -m ruff check .` | PASS — `All checks passed!` |
| `.\.venv\Scripts\python.exe -m ruff format --check .` | PASS — `26 files already formatted` |
| `.\.venv\Scripts\python.exe -m mypy` | PASS — `Success: no issues found in 14 source files` |
| `.\.venv\Scripts\python.exe -m dgca_next verify-specs` | PASS — exact two hashes above |
| `.\.venv\Scripts\python.exe -m pip check` | PASS — `No broken requirements found.` |
| `git diff --check` | PASS — exit 0 |
| `git status --porcelain` after committed implementation validation | PASS — empty stdout |
| `Get-Content .pytest_cache/i1-stress-metrics.json` | PASS — measured artifact below; ignored, not a source file |

The unchanged-baseline check also returned exit 0 with empty stdout:

```powershell
git diff 695034e2f7a73f555cfaf537ffa7a6f42885df29 HEAD --exit-code -- docs/specs docs/implementation/I0-IMPLEMENTATION-CONTRACT.md docs/implementation/I0-VERIFICATION-REPORT.md docs/implementation/I1-IMPLEMENTATION-CONTRACT.md src/dgca_next/contracts.py src/dgca_next/config.py src/dgca_next/__init__.py src/dgca_next/__main__.py src/dgca_next/integrity.py pyproject.toml tests/test_package_import.py tests/test_spec_integrity.py tests/test_contract_schemas.py tests/test_config_determinism.py
```

**CI PASS:** [I0 and I1 validation, run 40546175740](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/40546175740)
on tested commit `f62d5eb1739d1e8a18a8427c65ffe354c47ac591`. Both
`contracts (ubuntu-latest)` and `contracts (windows-latest)` completed successfully.
For each job, installation, version, integrity, both pytest runs, Ruff, formatting,
mypy and final clean-status steps all concluded `success`, including the
cross-platform canonical structural digest assertion. CI PASS includes the two
declared policy skips and does not resolve the missing scientific rule.
The subsequent report-only delivery commit's run is linked separately in the
completion message when available.

## Measured sparse-network fixture

The final repeat run constructed all 12,288 committed cell records with 768
explicitly injected one-slot neighborhoods, 576 live links and 192 reserved
future keys across all three regions. It allocated 768 stored 24-position slot
tuples (18,432 positions), not a dense N×N connectivity matrix. Separate lazy-read
tests enumerate all logical cells and slots without storing or committing any.

Exact measurements from the final repeat run:

```json
{
  "build_seconds": 0.9871929999790154,
  "fixture_only": true,
  "independent_audit_seconds": 0.599567900004331,
  "live_synapses": 576,
  "logical_cells": 12288,
  "materialized_cells": 12288,
  "occupied_slots": 768,
  "peak_traced_bytes": 13680805,
  "platform": "win32",
  "python": "3.14.4",
  "reserved_keys": 192,
  "retained_traced_bytes": 6241441,
  "slot_owner_records": 768,
  "structural_sha256": "160a96789166570bd8337c04f55044687c2dae8df62f690832d0164afb0f58b9"
}
```

Build time includes the pre-publication state/transition audit. The second audit
is separately timed. Memory uses Python `tracemalloc` through construction,
audit, full logical traversal and canonical diagnostic hashing; it is not process
RSS. Runtime measurements naturally vary. No time/memory pass threshold or neural
performance claim was invented. The same structural digest is checked by CI.

## I1 test mapping

| Contract IDs | Disposition | Executed evidence |
|---|---|---|
| T01–T04 | PASS | All physical IDs; lazy reads; corner/edge/center geometry; all region/category quotas |
| T05–T08 | PASS | Forward/reverse primitive consistency; exact D OR; fixed/live/protected/pinned rejection; injected index rollback |
| T09 | POLICY_BLOCKED | No production confirmation-window execution; separate fail-closed and synthetic teardown tests PASS |
| T10–T12 | PASS | Region/scope/time matrix; independent reverse keys; self/duplicate handling; commitment and D rejection |
| T13–T16 | PASS | 64/65 and 12/13 genuinely eligible distinct pairs; shared claims; reserve→live; rollback and no hidden frees |
| T17–T18 | PASS | Full source latent positions with z-side eligibility; overlap fixture uses four slots and six distinct role-position keys |
| T19–T20 | PASS | Pure fixture Q including internal-support discount/absent link; finite binary64 and state bounds |
| T21–T23 | PASS | Independent audits and deliberate corruption; every injection stage; canonical reordered and fresh-process hash tests |
| T24–T25 | PASS | Full physical-network sparse fixture and measurements; all 163 I0 tests and immutable source hashes |
| T26 | POLICY_BLOCKED | No exact inherited initializer target-selection policy; separate diagnostic/no-mutation test PASS |

No scientific LLA or LG test ID is claimed PASS from these physical subsets.
Failure injection covers shadow cell, slot, inverse index, link, reservation and
budget writes plus immediately-before-publication. Observers see the prior graph
at every hook. Independent before-image checks additionally catch attempted pin
removal and consolidated-link deletion even when the prospective state is
otherwise internally consistent. Nothing fallible follows atomic publication.

## Acceptance gates

| Gate | Verdict | Scope |
|---|---|---|
| I1-G01 | PASS | Physical ID space, immutable nonsemantic Cell, lazy sparse storage |
| I1-G02 | POLICY_BLOCKED for production policy; structural portion PASS | Typed latent schema, forward/reverse index and D verified; L01 initialization/recycling policy remains open |
| I1-G03 | PASS | Directed records, legality, commitment metadata, fixture provenance, no learning updates |
| I1-G04 | PASS | Total/cross/episodic/global episodic/membership bounds; unique key claims and transfers |
| I1-G05 | PASS | Single-use shadow batches, stale rejection, independent audits and injected-failure rollback |
| I1-G06 | PASS structural verification | Full-network sparse containers measured; no performance threshold inferred |
| I1-G07 | PASS | I0 unchanged and green, source integrity, reproducible ordering, Ubuntu/Windows CI verified above |
| I1-G08 | PASS | PASS/FAIL/NOT_RUN/POLICY_BLOCKED reported; fixture and empirical claims separated |

Overall: **I1 PARTIAL / POLICY_BLOCKED** regardless of structural test/CI success.

## FAIL, NOT_RUN and unresolved policy

**FAIL:** zero final test failures, audit errors or configured validation failures.
No pytest assertion failed during development. Interim Ruff import/line-wrapping
findings were corrected; no warning filter or check was weakened. Initial local
tracking setup needed an explicit I1 ref because the I0 checkout was a
single-branch clone. This was corrected before any implementation edits.
Sandboxed Git sometimes warned that the user's global ignore file was
unreadable; repository cleanliness was confirmed by empty status stdout and
approved execution. These are not scientific-policy blockers.

**POLICY_BLOCKED:** L01, I1-T09 and I1-T26 production-policy execution.
Core §1.3 states “historical highest coactive/intra” and “original confirmation
window” but does not define the complete ordinary selection/comparator or
recycling confirmation procedure. Core §12 repeats the slot counts. LLA §5
requires event/close structural eligibility; LLA §6.2 defines contextual role
capacity selection. Neither supplies the missing general initializer/recycling
rule. The approved I1 contract §2.3 explicitly anticipates this gap.

The missing policy must specify target selection/order/ties for ordinary intra,
local, inter and topographic positions, overlap handling, and the original
confirmation-window guards/duration before production wiring is enabled.
`W_conf=100`, `H_context=5`, geometry radius, or a new random seed cannot be
silently substituted for that missing rule. No new scientific parameter was set.

Minimal reproducer:

```python
from dgca_next.graph import SparseNetwork

graph = SparseNetwork()
before = graph.structural_hash
try:
    graph.initialize_latent_neighborhoods()
except RuntimeError as error:
    assert "UNRESOLVED_LATENT_POLICY" in str(error)
assert graph.structural_hash == before
```

An explicit unprotected occupied coactive fixture slot also rejects
`FixtureBuilder.recycle_slot(...)` with the same diagnostic. Fixed, live,
protected and candidate-pinned slots reject first with their specific protection
reason. These rejection tests do not count as execution of the missing policy.

**NOT_RUN:** all 57 named scientific tests LLA-T01–T41 and LG-T01–T16; neural
activation/normalization, observed SIC commitment, positive witness certification,
q/y aggregation, learning, demotion/expiration, recruitment, actual Assembly
birth, contextual prediction, hierarchy, retrieval and generation. Durable
journals, SQLite/persistence, save/load, crash recovery, exposure BEGIN/END/ABORT
and H_slow rollback remain I3+. No true neural learning evidence was produced.
Other Python minor versions, GPUs and performance/scaling experiments were not run.

Administrative conventions are explicit: fixed slot numbering chooses no
targets; redundant owner targets are rejected by the conservative fixture API;
debug hashes and wiring deltas are diagnostics, not persistence; exact duplicate
mutations are no-ops, conflicting payloads fail; batches are all-or-nothing and
single-threaded; pins and reservation claims are separate physical resources.
Existing links cannot be updated by an evidence law or state-transition engine.

No I2 work was begun. Further production-policy design and I1 completion require
independent review.
