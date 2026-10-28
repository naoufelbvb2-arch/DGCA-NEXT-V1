# I2 neural dynamics verification

Date: 2026-10-27 (America/New_York). Status: **I2 PARTIAL / SPEC_BLOCKED**.
Repository `naoufelbvb2-arch/DGCA-NEXT-V1`, branch
`feature/i2-neural-dynamics`. Both RC4.2 specifications remain **NOT FROZEN /
NOT EMPIRICALLY VERIFIED**. No test here demonstrates learned intelligence.

## Base and commits

| Reference | SHA |
|---|---|
| Accepted I1 base, merged before this mission | `0b05311fe82dc2e8961bcca226f8d795b3484524` |
| Starting I2 branch and approved execution contract | `00474b02aed7b0da33f375dd785540655ebb0497` |
| I2-R01 SIC and fingerprints | `c5d63dfbe4d7da081c4d05c91806dc16601a4f06` |
| I2-R02 numerical dynamics | `08c7d9c9881cc0f6bc0dcd22f18b8959b9d9ef38` |
| I2-R03 provenance and frontiers | `e82fa365495ec487006b6a6829504710afaab824` |
| I2-R04 contextual and scratch fixtures | `f7fd42197342f1bb0b49c6e2df67ec2f158af8dc` |
| I2-R05 verification hardening and blockers | `b50e0c2a9765432c27a4f4d7c453abdd0bd94a84` |

The report-only delivery commit can be resolved without embedding its own hash:
`git log -1 --format=%H -- docs/implementation/I2-VERIFICATION-REPORT.md`.
The completion message records the delivered branch SHA and final-head CI link.
No work in this mission merged to main.

## Changed files relative to the I2 starting commit

| Path | Responsibility |
|---|---|
| `.github/workflows/validate.yml` | Add I2 branch push to Ubuntu/Windows validation |
| `README.md` | Actual I2 status, API boundary and three blockers |
| `src/dgca_next/peripheral/__init__.py` | Peripheral exports |
| `src/dgca_next/peripheral/sic.py` | NFC, exact decimal SIC, separate original bundle digest, alias diagnostics |
| `src/dgca_next/peripheral/fingerprint.py` | FP-ROLE-V1 and fixed-order owner-profile bytes/hash |
| `src/dgca_next/dynamics/__init__.py` | Dynamics package boundary |
| `src/dgca_next/dynamics/numeric.py` | Binary64 bounds, stable fold, Q6 and SPEC_BLOCKED |
| `src/dgca_next/dynamics/state.py` | I1 immutable graph-state snapshot and explicit frozen H |
| `src/dgca_next/dynamics/drive.py` | Sorted directed neural propagation; fail-closed S01 |
| `src/dgca_next/dynamics/activation.py` | Gated raw column normalization and exactly two passes |
| `src/dgca_next/dynamics/frontier.py` | Final activity, cross and new-event frontiers |
| `src/dgca_next/dynamics/provenance.py` | Typed lanes and bounded, ordered read-only context proof paths |
| `src/dgca_next/dynamics/context_gate.py` | Physical fixture descriptors, calibration, keys and parent checks |
| `src/dgca_next/dynamics/routing.py` | Frozen unique/ambiguous source mask and legal target exception |
| `src/dgca_next/dynamics/attractor.py` | Legal Assembly fixture validation and pure transitions; S02 |
| `src/dgca_next/dynamics/homeostasis.py` | Pure slow-state formulas requiring supplied fixture rho; S03 |
| `src/dgca_next/dynamics/session.py` | Isolated read-only events, immutable scratch, trace and fault hooks |
| `src/dgca_next/dynamics/measurement.py` | Evaluator-only PredScore and FULL/CONTROL/gain |
| `tests/neural_fixtures.py` | Explicit synthetic physical links, bindings and Assemblies |
| `tests/test_sic_v1.py` | Published vectors, strict input, collisions, alias and replay identity |
| `tests/test_dynamics_numeric.py` | Independent binary64 and Q6 checks |
| `tests/test_dynamics_two_pass.py` | Frozen drives, two passes, normalization, S01 and threshold deferral |
| `tests/test_dynamics_frontier.py` | Causality, provenance, cold reset, replay and forgery resistance |
| `tests/test_dynamics_context.py` | Gate, calibration, collision, parent and stale binding checks |
| `tests/test_dynamics_routing.py` | Target-scoped, depth-2 and ambiguous-owner routing |
| `tests/test_dynamics_attractor.py` | Legal fixture Assemblies, transitions, homeostasis, S02 and S03 |
| `tests/test_dynamics_sessions.py` | FULL/CONTROL, evaluation isolation, malformed input and injected faults |
| `tests/test_dynamics_measurements.py` | Sparse fixture timing/memory and same-state reproducibility |
| `docs/implementation/I2-VERIFICATION-REPORT.md` | This report |

No I0/I1 regression test was removed or changed. Neither scientific file nor
the source manifest/configuration was changed by I2.

## PASS: executed local checks

Windows, CPython 3.14.4, pytest 9.0.2, Ruff 0.14.14 and mypy 1.19.1.
Commands below ran at the repository root on the I2 branch.

| Exact command | Result |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp -rs` before I2 code | `421 passed in 15.79s` |
| Same full-suite command after R01 | `470 passed in 10.23s` |
| Same full-suite command after R02 | `493 passed in 8.64s` |
| Same full-suite command after R03 | `502 passed in 9.40s` |
| Same full-suite command after R04 | `531 passed in 10.52s` |
| Same full-suite command after R05 | `547 passed in 9.72s` |
| `.\.venv\Scripts\python.exe -m ruff check .` | `All checks passed!` |
| `.\.venv\Scripts\python.exe -m ruff format --check .` | `56 files already formatted` |
| `.\.venv\Scripts\python.exe -m mypy` | `Success: no issues found in 32 source files` |
| `.\.venv\Scripts\python.exe -m dgca_next verify-specs` | Two raw SHA-256 PASS lines below |
| `.\.venv\Scripts\python.exe -m pip check` | `No broken requirements found.` |
| `git diff 00474b02aed7b0da33f375dd785540655ebb0497 --exit-code -- docs/specs` | Exit 0, no source differences |
| `git diff --check` | Exit 0 |
| `Get-Content -Encoding utf8 .pytest_cache/i2-dynamics-metrics.json -Raw` | Fixture measurements below |

Exact final local pytest output:

```text
........................................................................ [ 13%]
........................................................................ [ 26%]
........................................................................ [ 39%]
........................................................................ [ 52%]
........................................................................ [ 65%]
........................................................................ [ 78%]
........................................................................ [ 92%]
...........................................                              [100%]
547 passed in 9.72s
```

Exact source-integrity output:

```text
PASS docs/specs/DGCA_CORE_RC4_2.md SHA-256=570570a2a57c3b859ed3745c8812711cf36de89a47be50bdbf5f415a1b8dbc59
PASS docs/specs/DGCA_LLA_RC4_2.md SHA-256=47ad994cbda467ae1ce0ffd6c2868522f5502897f6c4d2d1f3ab68b69ac1df30
```

The full suite includes all 421 existing I0/I1 tests. The new tests asserting
that an unresolved case raises `SpecBlocked` pass as **guard tests**; they do
not turn the corresponding scientific mechanism or acceptance gate into PASS.
The current suite has no skips or xfails.

Cross-platform implementation run:
[I0, I1 and I2 validation, 40621164837](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/40621164837)
on `b50e0c2a9765432c27a4f4d7c453abdd0bd94a84`. The workflow checks raw source
integrity, the complete pytest suite twice, Ruff, formatting, mypy and clean
status on both `ubuntu-latest` and `windows-latest`. **PASS:** both jobs and all
their steps completed successfully on that implementation commit. This report's
own commit also triggers the same workflow; final delivery-head results are
observed and linked after publication in the completion message. The report does
not claim a final-head result before that run completes.

## I2 acceptance gates and test dispositions

| Gate | Result | Executed coverage and limitation |
|---|---|---|
| I2-G01 | PASS | SIC vectors, NFC, strict strings/length, half-even stages, receiver alias and role/profile bytes |
| I2-G02 | SPEC_BLOCKED S01 | Two passes, real I1 fixture Q, frozen previous drives, same-column gating and no third pass pass for consolidated synchronous paths; nonconsolidated synchronous path fails closed |
| I2-G03 | PASS | Typed lanes, observed/context F_step, residual exclusion, frozen previous source, hard-boundary/cold isolation and read-only origin |
| I2-G04 | PASS fixture scope | Physical calibrated P/C, key validation, stale/ambiguous fail closed, target-directed mask and a bounded depth-2 proof. Real owner discovery/registry is I5 and not claimed |
| I2-G05 | SPEC_BLOCKED S02/S03 | Pure arithmetic passes with explicitly supplied synthetic cohesion/rho; neither missing scientific producer is invented |
| I2-G06 | SPEC_BLOCKED where S01/S02 arises; otherwise PASS | Cold isolated read-only stepping, PredScore, FULL/CONTROL and immutability execute for supported physical fixtures |
| I2-G07 | PASS local and implementation CI; final-head CI observed after publication | 547 tests including 421 prior regressions; strict local tooling, raw integrity and Ubuntu/Windows implementation CI pass. Final CI must independently finish successfully |
| I2-G08 | PASS report | Results, concrete blockers, empirical boundaries, commands and trace are recorded |

| I2 contract tests | Disposition |
|---|---|
| T01–T05 | PASS: published salts/region mapping, NFC and encoding, decimal grammar and rounding, collisions, role/owner profiles |
| T06–T08 | PASS: uncommitted direct receivers never activate/commit; their raw X participates in column mean; malformed input leaves graph/R unchanged; finite ordered Noisy-OR |
| T09–T12 | PASS for defined/consolidated fixtures: associative `.8 * .3 = .24`, one pass-2 propagation, no third pass, gates before mean. S01 is independently SPEC_BLOCKED |
| T13–T19 | PASS: residual/predicted/spatial cannot become direct; emit threshold and prior frontier; cold reset, coexistence of lanes, fabricated predecessor replacement rejected |
| T20–T24 | PASS physical fixtures: missing/stale/subthreshold/off-context, no gate excitation, depth-2 target exception, ambiguous anchors and frozen prior mask |
| T25–T27 | PASS pure fixture formulas; S02/S03 SPEC_BLOCKED for unspecified scientific inputs |
| T28–T32 | PASS within supported fixtures: FULL/CONTROL, evaluator separation, sealed replay, deterministic traces and fault rollback; S01/S02 remain explicit on affected inputs |
| T33 | PASS local 421-test baseline and raw hashes; Ubuntu/Windows final-head results require the post-publication run |
| T34 | PASS reporting: all scientific LLA-T01–T41 and LG-T01–T16 remain NOT_RUN |

## SPEC_BLOCKED: decisions and minimal reproducers

### I2-S01 — synchronous propagation from nonconsolidated live links

Core RC4.2 §§1.4/5 and LLA RC4.2 §4.1 define neural Q/propagation for live
links without excluding CANDIDATE or EPISODIC_INDEXED. The approved I2
execution contract §3 explicitly says pass 2 uses **consolidated** Q. These
statements produce different `P_S` for a live, nonconsolidated synchronous
key; neither document specifies precedence for this conflict. The handler
raises `SpecBlocked` before producing a disputed step. Temporal ASSOCIATIVE Q
continues to use the specified live-link quality, and consolidated synchronous
links execute normally.

Minimal executable reproducer:

```python
from dgca_next.contracts import CellAddress, SynapseKey, SynapseScope
from dgca_next.dynamics.activation import two_pass
from dgca_next.dynamics.state import GraphSnapshot, Homeostasis
from dgca_next.graph import FixtureBuilder, SparseNetwork, Synapse, SynapseState

g = SparseNetwork()
b = FixtureBuilder(g)
b.commit_cells([8192, 8200], committed_event=0)
b.inject_slot(8192, 0, 8200)
k = SynapseKey(CellAddress.from_cell_id(8192), CellAddress.from_cell_id(8200), SynapseScope.LOCAL)
b.add_synapse(Synapse(k, 0, SynapseState.CANDIDATE, 0.6, 1.0, 0.0, 1, 2, True))
w = GraphSnapshot.capture(g)
h = Homeostasis.uniform_language(w.committed_ids)  # explicit synthetic H
two_pass(w, h, {}, {8192: 1.0}, {}, {})  # raises SpecBlocked: I2-S01
```

For this legal synthetic link, `Q=.6*(1/10)=.06` and the first-pass source
emits. One reading contributes `A1_source*.06` to its target, the other
contributes zero. Owner clarification must state whether NORMAL_W and/or the
I2 pass-2 instruction is restricted to consolidated synchronous keys.

### I2-S02 — Attractor cohesion

Core §2.1 requires `cohesion >= theta_ctx_form=.50` for admission, but neither
authority defines an executable cohesion function. Reciprocal support, member
degree/density and specificity in Core §2.0 are distinct quantities; choosing
one as cohesion would be a new mechanism.

```python
from dgca_next.dynamics.attractor import transition
transition(None, assembly_id=7, fresh_mean=0.4)  # SpecBlocked: I2-S02
```

The pure transition can be checked with `cohesion=0.5` explicitly marked as a
synthetic fixture value. An actual admitted or learned Assembly is not asserted.
The required resolution is a versioned formula, source population and timing for
cohesion; then its producer and related tests can be wired in.

### I2-S03 — instantaneous regional firing

Core §5 defines the EMA using `rho_r(t)` but neither RC4.2 authority defines its
population or denominator. One active of two committed LANGUAGE fixture cells
could yield `1/2` or `1/4096`; these change the threshold update. No denominator
is silently selected. `adapt` requires an explicitly supplied
`fixture_region_firing` for the pure arithmetic; without it:

```python
from dgca_next.contracts import Region
from dgca_next.dynamics.homeostasis import adapt
from dgca_next.dynamics.state import Homeostasis
h = Homeostasis({8192: 1.0, 8193: 1.0}, {8192: 0.0, 8193: 0.0},
                {Region.LANGUAGE: 0.2}, {Region.LANGUAGE: 0.03})
adapt(h, {8192: 1.0})  # SpecBlocked: I2-S03
```

The exercised synthetic alternatives yield threshold `.2` for `rho=1/4096`
and `.20500000000000002` for `rho=1/2`. Owner resolution must define the
numerator, denominator, timing and treatment of uncommitted cells. The pure
per-cell rate/gain law and EMA/threshold arithmetic are exercised separately;
no read-only session calls adaptation.

## Numerical trace and fixture measurements

The following trace uses only `context_fixture()` in `tests/neural_fixtures.py`:
synthetic committed I1 cells, fixture-only consolidated physical links and an
explicit calibrated synthetic binding. It is **not** a learned owner or a real
external training root. Feature names stay in the peripheral test input.

```text
SIC feature a, support .5: X_fixed=[(8606,500000),(9345,500000),
                                    (11795,500000),(12181,500000)]
P step: Aplus[9345]=Aplus[11795]=0.7272727272727273
B step: G_ctx[8192]=true; P_T[8192]=0.9256198347107438
        P_S[8192]=0.9256198347107438; A1[8192]=0.6777609682299546
        Aplus[8192]=0.7236130956078772
        F_step=[8192,8694,10273,10513,11641]
        mu=1 on [8694,10273,10513,11641]
next-step evaluator-only PredScore([8200,8208])=0.7236130956078772
W structural hash before/after: identical
```

The first-pass source `.8`, quality `.3` unit test separately checks neural
temporal contribution `.24`, without the LLA evidence factor. Current input
does not receive evaluator outcome IDs. CONTROL zeroes only temporal input and
then recomputes the same equations; its derived pass-1 emitters, P_S and
normalization can consequently differ from FULL.

The ignored `i2-dynamics-metrics.json` from the final local full-suite run
records a 12,288-logical-cell address space, 512 materialized synthetic
LANGUAGE cells, zero links and four read-only feature events. It measured
`0.2733578000916168` seconds, `784732` retained and `819834` peak bytes using
`tracemalloc`. Final frontier: `[8606,8694]`. These values measure one local
fixture, not RSS, throughput guarantees, learning or a numerical acceptance
threshold. A same-state repeat produces the same trace on this backend; only
the published physical hash vectors are asserted cross-platform bit-identical.

## FAIL, SKIPPED, NOT_RUN and limitations

- **FAIL:** zero final local tests/checks. During development a bounded search
  for a hash-collision fixture missed its real collision, a fixture helper used
  an incorrect slot attribute, an episodic test initially omitted the real
  network capacity, and one moved assertion was placed in the wrong test.
  Each was corrected; the final full suite above passes. Temporary Ruff issues
  were corrected without weakening checks. `gh run list` was unavailable
  (`gh` was not installed); the GitHub connector was used for CI inspection.
- **SKIPPED:** zero final pytest skips/xfails. SPEC_BLOCKED guard tests are
  executed tests, not skipped assertions and not resolved scientific gates.
- **NOT_RUN:** all 57 named scientific LLA-T01–T41 and LG-T01–T16; actual
  learning/evidence, external LEARN root execution, verified novelty and
  recycling, candidate/owner admission, real Assembly formation, generation,
  language output, durable journals/save/load/crash recovery, GPU and
  empirical capability/generalization tests. All I1 cells and links available
  to these traces are explicitly synthetic fixtures. Production automatic
  recycling remains disabled.
- **SPEC_BLOCKED:** I2-S01, I2-S02 and I2-S03 above. VISION/AUDIO initial
  thresholds also remain unspecified, so threshold-dependent execution is
  LANGUAGE-only. Caller-supplied synthetic H values are not scientific defaults.

Session state construction uses in-process single-use permits to reject copied
states with fabricated witnesses; this is not an external security boundary,
a persistent checkpoint or proof of a genuine LEARN event. Derived read-only
support retains bounded actual causal parent objects and never claims external
root evidence. The diagnostic SIC bundle hash is an I2 administrative format,
not a new scientific fingerprint or an owner lookup. Stable FP-ROLE-V1 and
owner-profile bytes follow Core §3.1 exactly.

Stop at **I2 PARTIAL / SPEC_BLOCKED**. Resolve the three decisions in an
authorized versioned contract before claiming I2 complete. Do not begin I3.
