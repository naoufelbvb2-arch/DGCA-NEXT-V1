# I4-R02 Native FORM verification

Date: 2026-10-31. Repository: `naoufelbvb2-arch/DGCA-NEXT-V1`.
Branch: `feature/i4-native-assemblies-design`. Scope: owner-approved
D01=A, D02=A and the staged first-Assembly LANGUAGE laboratory experiment.
The engineering result is one actual production native FORM. Full I4 is
still PARTIAL; this report makes no scientific-freeze or language claim.

Implementation commit: `930b7ab70ab28e06731eb7ed300d221a277d03fb`.
Approved-contract parent: `0c132119ad092a487d26f7a5c84dd002b55f6c37`.
The delivery commit adds only this report and the recorded JSON trace; its
own SHA and final-head CI result are supplied in the delivery message and
branch history, avoiding a self-referential commit hash.

## Authority and unchanged sources

Read the R00 readiness design, owner D01/D02 decisions, R01 independent
acceptance review, complete R02 implementation contract and both current
RC4.4 specifications before implementation. No scientific source or
configuration parameter changed.

| Source | SHA-256 |
| --- | --- |
| CORE RC4.4 | `3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c` |
| LLA RC4.4 | `ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0` |
| Configuration manifest | `088363eb89484c9605fa52e7c06743e5a1867be22bf3d87692492221fd317e27` |

## Implemented boundary

Select the fresh experimental database explicitly:

```python
RootStore(path, repository_root=repository_root, code_revision=revision,
          execution_mode="I4_NATIVE_FORM_V1")
```

The default remains `I3_SCHEMA4`. Native mode has SQL schema 5, canonical
W record version 5 and close record version 5. Its envelope retains the
canonical I3 physical graph and learned-link credits and adds the immutable
native registry, per-region high-watermark, per-cell memberships, independent
member inverse and rooted FORM log. An embedded physical-codec component
is not database migration. Native mode refuses schema 3/4 without changing
the file; the default schema-4 API refuses schema 5. No import/migration
or mode auto-detection was added. Existing schema-4 P04 remains available.
Native mode rejects P04 requests before staging, rejects competing saved
intent during validation, and never enables automatic recycling.

END stages ordinary I3 evidence first. The trusted FORM operator then
revalidates original journal events, direct SIC witnesses, original
pre-event W/H, committed-before-event status, event-frozen emission
threshold and activity. Structural eligibility is recomputed from the
post-evidence shadow using the existing reciprocal support and sparse
R01 seed projector. Caller triangles and saved read-only diagnostics are
not publication authority. Membership, inverse, registry, ID counter,
birth log, evidence, W/H and root completion commit together through the
existing SQLite transaction. FORM itself leaves slots and learned links
equal to the post-evidence shadow.

The first ID is 0, initial structural generation 1, and never-merged/split
serial is `None`. These are administrative representations, not new
scientific thresholds. IDs use a retained high-watermark and registry,
including archived entries. Production archive and generation transitions
remain unimplemented; archive non-reuse is a labeled component test only.

Any later native END with an existing registry fails closed with
`I4_UNIMPLEMENTED_MAINTAIN_GROW`, leaving its root OPEN and its evidence
unpublished. BEGIN/EVENT, read-only inspection, ABORT, cold reopen and
duplicate retrieval of a completed END remain available. More than one
lawful disjoint first seed fails the entire END with
`I4_FIRST_FORM_LAB_SCOPE_EXCEEDED`. The scientific limit of 12 seeds was
not changed to 1. A real two-cohort production test verifies this refusal.

## From-zero production evidence

The committed [machine-readable trace](I4-R02-PRODUCTION-TRACE.json) was
generated at the implementation SHA above. SHA-256 of that artifact:
`a283812a709b9f97f44ef8765692b8fb8a726908e49df142db5c74ff0c1a82e0`.
The experiment starts with zero cells, learned synapses and Assemblies.
All positive construction uses RootStore external `begin/event/end` and
canonical `(("a", "1"),)`; no FixtureBuilder, injected link or supplied
Assembly membership participates.

| Root / completed serial | Global EVENT IDs | Result after END |
| --- | --- | --- |
| 1 / 1 | 0 | Sensory commitments 8606, 9345, 11795, 12181; zero LOCAL links; no Assembly. |
| 2 / 2 | 1, 2 | Twelve directed LOCAL links, all CANDIDATE, E_ext=1; no Assembly. |
| 3 / 3 | 3, 4 | Same twelve LOCAL links, all CANDIDATE, E_ext=2; no Assembly. |
| 4 / 4 | 5, 6 | Twelve LOCAL links become CONSOLIDATED, E_ext=3; exactly one native FORM. |

Actual native record: ID **0**, LANGUAGE (region 2), LIVE, sorted members
**[8606, 9345, 11795]**, structural_generation **1**, birth_close_serial
**4**, last_mutation_close_serial **4**, last_merge_split_close_serial
**null**, high-watermark **0**. Each of these three cells has
`assembly_ids={0}` and member inverse `{0}`. Cell 12181 has no membership.
There is exactly one FORM journal entry.

| Directed LOCAL key | State | E_ext / E_int / S | Independent roots | Q |
| --- | --- | --- | --- | --- |
| 8606 -> 9345 | CONSOLIDATED | 3 / 0 / 1 | 2, 3, 4 | .3 |
| 9345 -> 8606 | CONSOLIDATED | 3 / 0 / 1 | 2, 3, 4 | .3 |
| 8606 -> 11795 | CONSOLIDATED | 3 / 0 / 1 | 2, 3, 4 | .3 |
| 11795 -> 8606 | CONSOLIDATED | 3 / 0 / 1 | 2, 3, 4 | .3 |
| 9345 -> 11795 | CONSOLIDATED | 3 / 0 / 1 | 2, 3, 4 | .3 |
| 11795 -> 9345 | CONSOLIDATED | 3 / 0 / 1 | 2, 3, 4 | .3 |

Each key has external_root_count=3, genuine credits from events 2, 4, 6,
and paired q=1, y=1 at each accepted root. Full directional credit
ordinals and original activity/digest/threshold fields are in the JSON.
All six keys pass actual latent structural eligibility. The three
reciprocal pair supports are .3. For each member, d=2, D=1, numerator=.6,
whole-region denominator=.8999999999999999, Spec=.6666666666666667.
The denominator includes the real fourth neighbor 12181; it is not
restricted to the selected triangle.

The first eligible witness is **root 4, event 5, order 0**, not event 6.
Each member was committed at event 0, has direct X_fixed=1,000,000 and
original final A=.7266155086363637 against frozen theta_emit=.253.
The operator selects the lexicographically first triangle at that event.
Other overlapping candidates are excluded by disjoint-vertex selection.
Event 6 also qualifies but does not create a second birth or retrospective
Assembly surface confirmation. Same-END evidence enables the structural
triangle; no claim treats the newborn as existing during event 5.

| Checkpoint | SHA-256 |
| --- | --- |
| Event 5 original observation | `87265149bf7ca770278f06eab98b2f3ee85ced8d1bbea0d2b954648bb6d86b3e` |
| Pre-event W / before END W | `98f5bb8e5f3fa9e1fb1e04a01cedadc1c9016b1f9a02f92adf34f78285cee711` |
| Event 5 frozen H | `5daa60a3aaccc3ee116f5455c66d014afaee89b56aec87a4497c1b3ab7334aed` |
| Post-evidence, pre-FORM W | `68a270f9124da27c9022f7d084f55a57911e308197c251c77f82029cc660d913` |
| After END W | `3b124aeb978bfa5e080b2d5ba9656fc78f1dbaae52ec0b3da9e56bedd1f9cd40` |
| After END H | `6b79ad7e629e8954e99131212265a37e99265206a24c3a932d83c191d3712208` |
| After END R | `235c092696221c8aa82d3d19a597d211a54bffa07d15f74bdc3e1ca1f9396ddb` |
| SQLite logical archive | `cb657bc85a74e43ecf346358c3e1aa917da74cba034ab67545adfbf7090275f2` |

END does not alter the final EVENT H. A separate interpreter cold-opens
the database and recovers identical W/H, ID, generation, members and
completed serial. Read-only activation has maximum synchronous
contribution .5213864547692626; inspection and activation preserve durable
state. This demonstrates retained learned-link neural effects, not native
Attractor behavior or a new learning claim.

The instrumented trial measured 24.858134699985385 seconds, 458,752 bytes
SQLite file/allocated size, 2,982,038 bytes parent tracemalloc peak and
37,216,256 bytes peak parent RSS. It includes instrumentation and ran
alongside regression testing. Child memory is not included. These are
observations, not performance guarantees or scientific constants.

## Atomicity, corruption and negative coverage

Actual child-process exits before and after END COMMIT recover the whole
pre-END or post-END state, respectively; retry creates exactly one ID
and one birth. Child-process exits around ABORT preserve/restore H_BEGIN,
leave completed serial at 3 and consume no Assembly ID. A later genuine
root then forms ID0 at completed serial4. Duplicate completed END returns
the original close without extra evidence or birth.

Schema-5 round-trip rejects wrong cell memberships, inverse, generation,
watermark, missing birth log, candidate-only support and missing reverse
support. A journal-tampering test changes the birth root and repairs all
affected W hashes and close checksums: cold historical replay still
rederives actual evidence settlement and FORM and rejects the forgery
with INVALID_CLOSE_CHECKPOINT. The physical codec alone is not claimed
to authenticate arbitrary SQLite journal rewrites. Recovery uses the
existing authenticated historical event verification path (including
frozen temporal proof); it does not rerun every historical neural pass.

Malformed original event records and competing saved recycling intent
refuse END before publication. Public native record construction cannot
mint trusted authority. Empty roots, roots 1-3 and qualifying ABORTs publish
no Assembly and do not move the ID watermark. Existing R01 component
tests cover EPISODIC/CANDIDATE/one-way/ASSOCIATIVE-only support, threshold
boundaries, full-region specificity, capacity, wrong-region/prebirth,
predicted-only/non-external witness refusals and deterministic disjoint
ordering. Those are component/negative evidence; they are not presented
as additional production learning curricula.

## Changed files

Implementation commit (17 files):

- `.github/workflows/validate.yml`
- `src/dgca_next/graph/audit.py`
- `src/dgca_next/graph/native_assembly.py` (new)
- `src/dgca_next/graph/network.py`
- `src/dgca_next/graph/production.py`
- `src/dgca_next/learning/native_form.py` (new)
- `src/dgca_next/learning/novelty.py`
- `src/dgca_next/learning/settlement.py`
- `src/dgca_next/persistence/form_inspection.py`
- `src/dgca_next/persistence/graph_codec.py`
- `src/dgca_next/persistence/native_codec.py` (new)
- `src/dgca_next/persistence/native_store.py` (new)
- `src/dgca_next/persistence/production_store.py`
- `src/dgca_next/persistence/store.py`
- `tests/experiments/i4_r02_native_form_trace.py` (new)
- `tests/experiments/test_i4_r02_native_form_trace.py` (new)
- `tests/test_i4_r02_native_form.py` (new)

Delivery additions: this report and
`docs/implementation/I4-R02-PRODUCTION-TRACE.json`.

## Verification commands and results

Local Windows, Python 3.14.4. Commands use `.venv/Scripts/python.exe`;
the table spells out that executable rather than implying another Python.

| Exact command | Result |
| --- | --- |
| `.venv/Scripts/python.exe -m pytest -q --basetemp=.pytest-tmp -rs` | PASS: `753 passed in 284.84s (0:04:44)`; all 729 previous tests retained, 24 new cases, zero skips. |
| `.venv/Scripts/python.exe tests/experiments/i4_r02_native_form_trace.py --output docs/implementation/I4-R02-PRODUCTION-TRACE.json` | PASS: exit 0, actual trace and independent recovery above. |
| `.venv/Scripts/python.exe -m ruff check .` | PASS: All checks passed! |
| `.venv/Scripts/python.exe -m ruff format --check .` | PASS: 109 files already formatted. |
| `.venv/Scripts/python.exe -m mypy` | PASS: Success: no issues found in 54 source files. |
| `.venv/Scripts/python.exe -m dgca_next verify-specs` | PASS: both unchanged RC4.4 hashes above. |
| `.venv/Scripts/python.exe -m pip check` | PASS: No broken requirements found. |
| `git diff --check` | PASS. |
| `git diff --exit-code 0c13211 -- docs/specs src/dgca_next/config.py` | PASS: unchanged specifications/configuration. |

Targeted development runs passed: 30 legacy/R01/P02 checks (23.79s), then
23 R02/experiment cases (25.50s), then the added actual multiple-seed
production refusal (1 passed, 2.36s). These overlapping runs are not added
together as a distinct regression count. There are 24 new R02 cases and
729 retained tests, total 753.

Implementation run
[41245926048](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/41245926048)
tests exact code head `930b7ab70ab28e06731eb7ed300d221a277d03fb`.
At report capture both first full pytest executions passed; the Windows
job also completed its repeated suite and all remaining checks SUCCESS.
The Ubuntu repeated suite was still running. This intermediate snapshot
is not used as a final-head acceptance claim.

The documentation/trace delivery triggers a distinct final-head run. Its
exact SHA/result must match the delivered HEAD in the
[branch workflow history](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/workflows/validate.yml?query=branch%3Afeature%2Fi4-native-assemblies-design).
Implementation CI is not substituted for final-head CI; REVIEW READY
requires both final-head matrix jobs to succeed before delivery.

FAIL: none in the final validation commands. SKIPPED: none.
SPEC_BLOCKED/EMPIRICAL_BLOCKED: none in the approved first
FORM scope. Later unimplemented operators are explicitly contained below.

| Acceptance gate | Disposition |
| --- | --- |
| R02-G01 TRUST | PASS: actual external RootStore events, original frozen witnesses and committed-before-event provenance. |
| R02-G02 PHYSICS | PASS: six actual consolidated LOCAL keys, Q/R/d/D/whole-region Spec, chronological lexicographic seed. |
| R02-G03 IDENTITY | PASS: actual LIVE ID0/GEN1, durable registry, membership and inverse; component archived non-reuse distinguished. |
| R02-G04 ATOMICITY | PASS: evidence then FORM in the same END transaction; actual END/ABORT process crashes and duplicate END. |
| R02-G05 PERSISTENCE | PASS: canonical W5, authenticated historical rederivation, repaired-checksum forgery rejected, old-file refusal and schema-4 regressions. |
| R02-G06 NEGATIVES | PASS: new corruption/origin/mode negatives plus retained R01 physical/witness/ordering component cases. |
| R02-G07 REGRESSION | Local PASS: 753 tests and all static/integrity/dependency checks; final-head matrix must pass before the delivery message declares REVIEW READY. |
| R02-G08 REPORT | PASS within approved scope: actual committed trace, identities/hashes/commands, explicit implementation limits. |

## Scope and remaining limitations

LG-T01 first production FORM is executed within this approved vertical
slice. Full LG-T03 lifecycle (GROW/ARCHIVE, later generations, merge/split)
and full LG-T16 peripheral surface attestation are NOT_RUN. Administrative
archive allocator testing is not a production archive scenario. The
earlier I3 scientific-coverage classifications are not upgraded by R02
component success.

MAINTAIN/GROW/MERGE/SPLIT, native Attractor, contextual owners, peripheral
outbox/readout, generation, automatic recycling and native/P04 coexistence
are NOT_RUN/unimplemented. Native END after the first birth is deliberately
fail-closed. No normative ambiguity was silently resolved and no unrelated
neural law, evidence threshold or numerical parameter was changed.
The owner-approved mode/schema/staged-operation decisions are implemented;
future expansion or migration remains subject to independent authorization.

No merge to main or R03 work is included. The stopping point is
**I4-R02 REVIEW READY** only after the final-head Ubuntu and Windows jobs
pass. Independent R02 review is the next authorized decision.
