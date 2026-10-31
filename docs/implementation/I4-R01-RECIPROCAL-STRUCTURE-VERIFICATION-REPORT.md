# I4-R01 reciprocal structure and FORM eligibility verification

Branch: `feature/i4-native-assemblies-design`. Accepted I3 main baseline:
`88fc596c178c8a89c24b991e280d7a0ca8c07779`; R01 contract base:
`4ec188c`. Implementation and tests:
`dba760dba48455cf59d4a87d6cb6a6a9b562558a`. This report and its numerical
artifact follow that commit; the final report delivery must pass its own
Ubuntu/Windows workflow before R01 is review ready.

## Result and scope

The specified cold production curriculum produced a valid reciprocal triangle
and event-qualified **hypothetical** FORM seed `(8606,9345,11795)` at root 4,
event 5/order 0. Six directed LOCAL links were separately learned and
consolidated. The inspector reports `FORM_ELIGIBLE`; no Assembly identity,
record, membership or native Attractor was created. This is executed R01
readiness evidence, not executed native FORM or a full LG-T01 pass.

The full numerical record is [I4-R01-PRODUCTION-TRACE.json](I4-R01-PRODUCTION-TRACE.json),
SHA-256 `063c361ef70a9b17683b7bceb22286f2ba1e70585de274dd9c50796f839ffa22`
(88,999 bytes). It includes all LOCAL pairs, all original credits, events,
thresholds, candidate alternatives and per-close archive hashes. The saved
database declares the actual implementation commit above as its code revision.

## Changes and scientific authority

- `src/dgca_next/graph/assembly_support.py`: sparse reciprocal adjacency,
  immutable directed/pair/member/triangle diagnostics, ordered d/D/Spec and
  explicit numerical-only Q boundary operator.
- `src/dgca_next/persistence/form_inspection.py`: completed-root historical
  W/H/event binding, original direct-witness and frozen threshold qualification,
  chronological disjoint projected seeds capped at the existing 12 limit.
- `src/dgca_next/persistence/production_store.py`: one read-only
  `inspect_form_eligibility(exposure_id)` method and its import. END is unchanged.
- `tests/test_i4_r01_components.py`, `tests/test_i4_r01_production.py`,
  `tests/experiments/i4_r01_reciprocal_trace.py` and
  `tests/experiments/test_i4_r01_reciprocal_trace.py`: labeled component
  negatives, real production tests and the reproducible instrumented trace.
- `.github/workflows/validate.yml`: include the I4 branch in the existing
  Ubuntu/Windows matrix and run `pip check` after dependency installation.
- This report and `I4-R01-PRODUCTION-TRACE.json`.

Both scientific specifications, graph codec, Cell schema and END implementation
remain unchanged. `python -m dgca_next verify-specs` passed:

| Source | SHA-256 |
| --- | --- |
| CORE RC4.4 | `3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c` |
| LLA RC4.4 | `ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0` |
| Fixed lab configuration manifest | `088363eb89484c9605fa52e7c06743e5a1867be22bf3d87692492221fd317e27` |

## Production roots and six actual directed links

The new schema-4 database began with zero committed cells and zero synapses.
Input was exclusively `(("a","1"),)`. Root 1 had one event; roots 2, 3 and 4
each had two ordered events. All roots completed via the production RootStore
API, without FixtureBuilder, synthetic q or manual topology edits.

| Root | Global events | Physical result | Inspection |
| ---: | --- | --- | --- |
| 1 | 0 | births 8606, 9345, 11795, 12181; no same-event links | `NO_RECIPROCAL_TRIANGLE`; newborns unqualified |
| 2 | 1,2 | all 12 directed LOCAL keys CANDIDATE, E_ext=1 | `NO_RECIPROCAL_TRIANGLE` |
| 3 | 3,4 | the same LOCAL keys CANDIDATE, E_ext=2 | `NO_RECIPROCAL_TRIANGLE` |
| 4 | 5,6 | all 12 directed LOCAL keys CONSOLIDATED, E_ext=3 | four structural triangles; one projected seed |

Each selected directed key below has S=1.0, E_ext=3.0, E_int=0.0,
external_count=3, d_discount=1, Q=0.3 and D=1. Its three genuine credits come
from independent roots 2/3/4 and global same-event IDs 2/4/6. Each winning
credit has q=1.0 and paired y=1.0. The JSON records each directed key's distinct
ordinal, event timing, sampled activity, threshold and observation digests.

| Directed LOCAL key | State | S | E_ext | E_int | Count | Q | D |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 8606 → 9345 | CONSOLIDATED | 1 | 3 | 0 | 3 | .3 | 1 |
| 9345 → 8606 | CONSOLIDATED | 1 | 3 | 0 | 3 | .3 | 1 |
| 8606 → 11795 | CONSOLIDATED | 1 | 3 | 0 | 3 | .3 | 1 |
| 11795 → 8606 | CONSOLIDATED | 1 | 3 | 0 | 3 | .3 | 1 |
| 9345 → 11795 | CONSOLIDATED | 1 | 3 | 0 | 3 | .3 | 1 |
| 11795 → 9345 | CONSOLIDATED | 1 | 3 | 0 | 3 | .3 | 1 |

Thus all three unordered supports are min(.3,.3)=.3, exceeding theta_A=.10.
The fourth receiver is a reciprocal neighbor of every triangle vertex and is
included in the **whole LANGUAGE** specificity denominator:

| Cell | All reciprocal neighbors, each support .3 | d | D | Numerator | Denominator | Spec |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 8606 | 9345,11795,12181 | 2 | 1 | .6 | .8999999999999999 | .6666666666666667 |
| 9345 | 8606,11795,12181 | 2 | 1 | .6 | .8999999999999999 | .6666666666666667 |
| 11795 | 8606,9345,12181 | 2 | 1 | .6 | .8999999999999999 | .6666666666666667 |

Every member meets d_min=2, rho_core=.70 and sigma_G=.30. Actual membership
counts are zero, below M_max=12. These values use `graph.synapse.quality` and
ascending binary64 folds; governance comparisons follow Core's Q6 policy.

## Historical event witnesses and deterministic ordering

All four receivers were committed at event 0, before both events of root 4.
Their canonical direct support was X_fixed=1000000 and their original event
observations have digest
`87265149bf7ca770278f06eab98b2f3ee85ced8d1bbea0d2b954648bb6d86b3e`.
For **each** of 8606,9345,11795 and 12181:

| Root/event/order | Final A+ | Frozen theta_emit | Pass-1 emitter | Original F_step | Witness |
| --- | ---: | ---: | --- | --- | --- |
| 4/5/0 | .7266155086363637 | .253 | yes | yes | OBS_ELIGIBLE_EMISSION |
| 4/6/1 | 1.0 | .25875000000000004 | yes | yes | OBS_ELIGIBLE_EMISSION |

The reader authenticates the completed root and original canonical event,
pre-event commitment and frozen H. It verifies stored dynamics using that
event's historical W/H through the existing verifier; it never substitutes
current W or post-close H for event-time values. Qualification uses direct
OBS_ELIGIBLE support and final A at the frozen emission threshold, as Core FORM
requires; Pass-1 emitter and F_step values are retained as diagnostic evidence.
The structural W* is root 4's actual post-evidence close snapshot. This use of
post-evidence structure with original root events follows Core §2.0; it grants
no historical Assembly existence or attestation.

Sorted structural triangles are `(8606,9345,11795)`, `(8606,9345,12181)`,
`(8606,11795,12181)`, `(9345,11795,12181)`. At event 5/order 0 the first is
selected hypothetically. The other three, and all four at event 6/order 1,
receive `FORM_VERTEX_ALREADY_ASSIGNED`. The selection is chronological then
lexicographic, with disjoint seeds across events and at most 12 projected
seeds. The sparse search intersects actual reciprocal neighborhoods; it does
not enumerate triples over the logical 4096-cell region.

## Persistence and immutability

At root 4 the inspected source checkpoint hashes were:

- W: `70d32584f21a63e7d97ff11f500da5325a354e689945c49dfbf4ac04715049dc`.
- H: `6b79ad7e629e8954e99131212265a37e99265206a24c3a932d83c191d3712208`.
- SQL archive: `6283988a5577abfd4e5e7ae860b2f328cb4146cb32c1536f440c19298bf69d9e`.

Before/after inspection checks compare complete StoreView (including R and
root counters), W and H bytes, source graph hash, exact SQL dump digest and
SQLite file digest. Those comparisons cover persisted evidence, outgoing and
reverse indexes, event journal, topology, commitments and completion status.
Cold reopening and repeated inspection returned an equal immutable diagnostic
and the same source/state hashes. A later genuine root changes current W, but
reinspection of root 4 still returns its original diagnostic and frozen H.
All Cell.assembly_ids remain empty. Neither inspection nor projected selection
publishes anything to the journal or codec.

The implementation refuses a close marked P04 `RECYCLED` with
`UNVERIFIED_FORM_EVENT: POST_EVIDENCE_SNAPSHOT_REWIRED: I4_D01_UNRESOLVED`;
the current API does not reinterpret final rewired W as pre-recycling W*.
This is a conservative read-only limitation while D01 remains pending, not a
new END ordering decision. The combined P04-recycled-close/R01 query was
NOT_RUN in this four-root trial.

## Component falsification versus production evidence

The one-sided, nonconsolidated reverse, ASSOCIATIVE-only, diluted-specificity,
invalid graph and bounded enumeration tests use explicitly marked component
graphs. No component graph enters the trusted RootStore inspector. A scalar
minimum/Q6 threshold test is numerical-only. In the current valid synapse
schema, consolidated S≥.60 and E_total≥3 imply Q≥.18 for external-dominated
LOCAL links (≥.135 with the internal discount), so a valid consolidated Q<.10
or exactly .10 cannot be constructed under those laws. The .10 boundary tests
therefore exercise the numeric operator without claiming such a production
synapse exists. No threshold was altered to manufacture a negative case.

Real production negatives include roots 1–3, newborn commitment timing,
completed empty/below-threshold events and a same-root predicted-only event
with nonzero temporal input but no direct witness. OPEN/ABORTED/unknown roots,
caller objects, malformed/truncated records and untrusted event origins fail
closed with `UNVERIFIED_FORM_EVENT`. Nonempty native Assembly coverage has no
production representation in R01 and is NOT_RUN; no fake IDs were inserted.

## Verification and gate map

Local runtime is Python 3.14.4 on Windows. The new R01 subset passed
`25 passed in 19.23s` before the full regression run. Commands use
`.venv/Scripts/python.exe`:

| Command | Result |
| --- | --- |
| `python -m pytest -q --basetemp=.pytest-tmp -rs` | PASS: 729 passed in 427.94s; no skips. |
| `python tests/experiments/i4_r01_reciprocal_trace.py --output docs/implementation/I4-R01-PRODUCTION-TRACE.json` | PASS: actual four-root trace above, exit 0. |
| `python -m ruff check .` | PASS: All checks passed! |
| `python -m ruff format --check .` | PASS: 102 files already formatted. |
| `python -m mypy` | PASS: no issues in 50 source files. |
| `python -m dgca_next verify-specs` | PASS: exact CORE and LLA hashes above. |
| `python -m pip check` | PASS: No broken requirements found. |
| `git diff --check` | PASS. |
| `git diff --exit-code 4ec188c -- docs/specs src/dgca_next/persistence/graph_codec.py src/dgca_next/graph/cell.py` | PASS: no source, codec or Cell schema changes. |

Implementation CI [41210552521](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/41210552521)
completed SUCCESS on Ubuntu and Windows, including both pytest executions,
for `dba760dba48455cf59d4a87d6cb6a6a9b562558a`. The documentation/trace
delivery commit triggers a distinct final-head run; its exact SHA and result
must be checked in the [I4 branch workflow history](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/workflows/validate.yml?query=branch%3Afeature%2Fi4-native-assemblies-design).
This report does not identify the earlier code-head run as final-head CI.
FAIL: none in the final checks. SKIPPED: none. No R01 scientific or empirical
blocker was found; the explicitly listed later capabilities remain NOT_RUN.

| Contract test | Disposition |
| --- | --- |
| T01 | COMPONENT PASS: one consolidated direction without reverse gives R=0. |
| T02 | COMPONENT PASS: a CANDIDATE or EPISODIC_INDEXED reverse gives R=0; real roots 2/3 also remain ineligible. |
| T03 | COMPONENT PASS: numerical min/Q6 threshold, equality and near-boundary cases; physical reach limitation above. |
| T04 | COMPONENT PASS: ASSOCIATIVE keys supply no LOCAL structural support. |
| T05 | PASS: production fourth-neighbor denominator; component star dilutes Spec to .25 and refuses. |
| T06 | PASS: empty/uncommitted/self/fixture/malformed-graph rejection; production graph audit and I3 credit invariants retained. |
| T07 | PRODUCTION PASS: root-1 newborns never qualify as committed-before-event. |
| T08 | PRODUCTION PASS: the six actual keys and full credits are recorded above and in JSON. |
| T09 | PRODUCTION PASS: historical witness/H, direct support, predicted-only and untrusted origin refusals. |
| T10 | PRODUCTION PASS: later root W cannot change root-4 inspection. |
| T11 | PASS: actual deterministic seed plus component 13-triangle/12-seed chronological disjoint cap. |
| T12 | PASS: malformed/truncated event record is unverified, never guessed. |
| T13 | PRODUCTION PASS: exact state/archive/file equality and independent cold reopen. |
| T14 | PASS: immutable diagnostics only, empty membership fields, no Assembly or journal publication. |
| T15 | PASS: reproducible production trace and explicitly separate component negatives. |
| T16 | Local suite and implementation CI PASS; final-head Ubuntu/Windows CI must pass before delivery is review ready. |

| Acceptance gate | Disposition |
| --- | --- |
| G01 | PASS: actual six directed, audited nonfixture LOCAL keys. |
| G02 | PASS: R/d/D/full-region Spec and labeled numeric negatives. |
| G03 | PASS: authentic event-frozen direct observations and committed-before-event proof. |
| G04 | PASS: chronological lexicographic adjacency selection, disjoint seeds, limit 12. |
| G05 | PASS: immutable output and zero durable state drift across inspection/reload. |
| G06 | PASS: measured positive first-lab FORM eligibility, no forced formation. |
| G07 | Local 729-test regression, static/integrity/dependency checks and implementation CI PASS; final report-head CI must pass before final delivery. |
| G08 | PASS within R01 scope: source-traceable report, pending R02 decisions explicit below. |

## Performance and remaining decisions

The instrumented trial took 13.729707899969071 seconds while the full suite
also ran. Empty-graph inspection took .0015562 s; root-4 inspection took
1.0991793 s; cold reopen plus inspection took 4.7995114 s. Peak parent-process
tracemalloc was 3,116,030 bytes, peak RSS 35,360,768 bytes, and SQLite file and
allocated size were each 458,752 bytes. These diagnostic measurements include
tracing and validation overhead and are not new performance thresholds.

I4-D01 same-END recycling/Assembly coexistence and I4-D02 production
Assembly-capable version/migration policy remain unresolved for R02. R01
changes neither END nor schema and cannot authorize R02. Native FORM,
MAINTAIN/GROW/MERGE/SPLIT, Assembly identity/generation, Native Attractor,
contextual owners, readout, generation and automatic recycling are NOT_RUN.
CORE/LLA remain design candidates; this result is physical readiness evidence.

No merge to main or I4-R02 work is included. Independent review is the next
step once the final-head checks pass.
