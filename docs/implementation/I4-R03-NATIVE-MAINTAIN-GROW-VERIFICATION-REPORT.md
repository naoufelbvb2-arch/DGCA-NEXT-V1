# I4-R03 Native MAINTAIN/GROW verification

Date: 2026-10-31. Repository `naoufelbvb2-arch/DGCA-NEXT-V1`, branch
`feature/i4-native-assemblies-design`. Scope: the approved single-Assembly
LANGUAGE laboratory continuation. Full I4 remains PARTIAL.

Implementation commit: **`2fd2b5345020b5e506743fb1f1318f22e634e193`**.
Corrected forensic test head / recorded experiment revision:
**`4cfd52d3bbc658a3a841ad61b19fd43626024e8c`**. This second commit changes
only the test expectation for earlier rejection; runtime code is identical.
Approved contract/review parent: `e316d66d00eb5f0df4b55afb18b9e94078e30dc8`.
The documentation delivery adds this report and the actual production
trace. The delivery response identifies its own commit and exact
final-head CI receipt; a report cannot contain its own Git commit hash.

## Sources and implementation boundary

Read the full R02 independent acceptance review, R03 execution contract,
owner D01/D02 decisions and both RC4.4 specifications before changing
code. No scientific source, numerical parameter or configuration changed.

| Scientific source | Unchanged SHA-256 |
| --- | --- |
| CORE RC4.4 | `3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c` |
| LLA RC4.4 | `ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0` |

Use the explicit capability
`RootStore(..., execution_mode="I4_NATIVE_MAINTAIN_GROW_V1")`.
The accepted `I4_NATIVE_FORM_V1` retains its original first-FORM guard,
preserving its regressions. The default `I3_SCHEMA4` and its P04 path are
unchanged. Both native capabilities reject P04; automatic recycling is off.

The [versioned Schema-5 journal policy](I4-R03-SCHEMA5-STRUCTURAL-JOURNAL.md)
documents exact compatibility, record fields and hashing boundaries.
Existing R02 W/close bytes are preserved until an actual structural
mutation/lifecycle close. No SQL migration or schema-3/4 import is performed.
An actual database generated with archived accepted R02 source at
`c66eb570b03e7653d9fa1f16c1805d52ad5f9072` opened in R03 with identical file
bytes, W and H, then completed genuine root5 GROW. Original immutable FORM
records and earlier root checkpoints are not rewritten.

The native END pipeline runs ordinary synaptic evidence settlement,
MAINTAIN, ranked GROW, covered-member FORM evaluation, then the deferred
MERGE/SPLIT guard. A private physical-only settlement/hash boundary allows
temporary non-KEEP native administration to be repaired inside the
transaction. Public codec/load/final-publication validation remains strict.
No fixture can use this boundary to publish production evidence.

MAINTAIN visits IDs ascending, removes the lowest failing physical ID,
recomputes predicates after each removal and archives a subminimum set.
Current LIVE membership uses d_min, rho_keep and sigma_keep. Initial FORM
continues to use the stricter original FORM gates during historical birth
rederivation. GROW ranks the finite reciprocal neighborhood once by
quantized actual support sum and physical ID, inspects each candidate
once, checks prospective candidate and existing-member guards, capacity
and size, then updates both membership indexes with one generation step.
It creates no synapse or evidence.

The terminal 3-to-2 MAINTAIN removal is one ARCHIVE mutation, one membership
change and one generation increment. Its two terminal IDs are historical
membership; all LIVE cell/inverse references are cleared. There is no
additional generation increment for a status-only action. The retained
registry/high-watermark prevents ID reuse. This implements the Core
instruction to archive the subminimum set; it does not create a LIVE
size-2 Assembly. This representation was verified at component/codec
level, not demonstrated by a genuinely degrading production curriculum.

An additional required FORM beyond the first-Assembly lab scope fails
with `I4_FIRST_FORM_LAB_SCOPE_EXCEEDED`. Multiple LIVE Assemblies or a LIVE
size at least N_min after MAINTAIN/GROW conservatively fail with
`I4_UNIMPLEMENTED_MERGE_SPLIT`, as authorized by the contract. These guards
roll back END and preserve the OPEN state. K_FORM_PER_END=12 and K_max=16
are unchanged. No actual MERGE/SPLIT eligibility/operation is claimed.

## Genuine six-root experiment

The committed [production trace](I4-R03-PRODUCTION-TRACE.json) records the
actual implementation SHA, all physical measurements below, subprocess
crashes and an independent interpreter reload. Trace file SHA-256:
`37d1a3eeffda562d4676ffaae1b04f691eead4c3318285a9ad28d4b8be492d4e`.
It starts from a fresh Schema-5 database with zero committed cells, learned
synapses or Assemblies. All positive changes use genuine external
RootStore BEGIN/EVENT/END with canonical `(("a", "1"),)`; no FixtureBuilder,
supplied member, expected output label or manually inserted link is used.

| Root / completed close | Genuine EVENT IDs | Actual result |
| --- | --- | --- |
| 1 / 1 | 0 | Commit 8606, 9345, 11795, 12181; no newborn learning or Assembly. |
| 2 / 2 | 1, 2 | Twelve directed LOCAL keys CANDIDATE, E_ext=1; no Assembly. |
| 3 / 3 | 3, 4 | Same LOCAL keys CANDIDATE, E_ext=2; no Assembly. |
| 4 / 4 | 5, 6 | Twelve LOCAL keys CONSOLIDATED, Q=.3; FORM ID0 GEN1, members [8606,9345,11795]. |
| 5 / 5 | 7 / order0 | Ordinary LOCAL reinforcement, MAINTAIN KEEP, GROW adds 12181; ID0 GEN2. |
| 6 / 6 | 8 / order0 | Valid empty external feature event; MAINTAIN KEEP, zero proposals/structural edits; ID0 GEN2 unchanged. |

The root4 W digest exactly matches accepted R02:
`3b124aeb978bfa5e080b2d5ba9656fc78f1dbaae52ec0b3da9e56bedd1f9cd40`.
The immutable root4 FORM log still identifies root4/event5/order0,
birth_close_serial4 and original three members. It is unchanged after
root5 growth, root6 completion and cold recovery.

Root5 event7 is EXTERNAL_DIRECT / LEARN. All four committed receivers have
X_fixed=1,000,000, are actual frozen Pass-1 emitters and F_step members,
and have final A=.7259368601806818. No receiver is born in root5. Frozen
target theta_active=.23000000000000004. Each of the twelve already learned
directed LOCAL keys accepts exactly one root5 credit:

| Quantity | Actual value for each directed LOCAL key |
| --- | --- |
| q_root5 | .5269843249689868 |
| paired y_root5 | .8576295377561982 |
| E_ext | 3.526984324968987 |
| E_int | 0 |
| S | .9787277189155831 |
| Q | .34519573230279144 (previously .3) |
| External count / roots | 4 / [2,3,4,5] |
| State | CONSOLIDATED |

Actual physical keys are all directed permutations without self-links of
[8606,9345,11795,12181]: 8606->9345/11795/12181;
9345->8606/11795/12181; 11795->8606/9345/12181;
12181->8606/9345/11795. The JSON retains every key, latest q/y/activity,
credit ordinal, digest and root list. All original key identities, latent
slots and reverse latent indexes remain unchanged. Normal root5 evidence
changes E/S/Q; growth itself fabricates none. No new synapse is needed.

| Stage / physical cells | d | D | Numerator | Whole-region denominator | Spec |
| --- | --- | --- | --- | --- | --- |
| MAINTAIN, each original member | 2 | 1 | .6903914646055829 | 1.0355871969083743 | .6666666666666666 |
| Prospective GROW candidate 12181 | 3 | 1 | 1.0355871969083743 | 1.0355871969083743 | 1 |
| Prospective GROW, each original member | 3 | 1 | 1.0355871969083743 | 1.0355871969083743 | 1 |
| Root6 stable MAINTAIN, all four | 3 | 1 | 1.0355871969083743 | 1.0355871969083743 | 1 |

Candidate 12181 has actual rank support 1.0355871969083743 and meets all
GROW conditions. The existing members pass prospective KEEP. Each support
sum is folded over sorted physical members; rank quantization uses exact
binary64-rational ties-even millionths and permits sums above one rather
than incorrectly applying a per-support upper bound.

At root5 FORM exclusion, actual event7 coverage is 4/4=1 for the current
post-GROW live shadow, so no uncovered seed requires another birth. This
is exclusion bookkeeping, not a claim that GEN2 existed during event7 or
earned retrospective surface evidence. Root6 event8 coverage is 0/4, but
there are also no qualified direct FORM witnesses and no new seed.

## Identity, mutation and persisted hashes

After root5: AssemblyID **0**, LANGUAGE, LIVE, members
**[8606,9345,11795,12181]**, structural_generation **2**,
birth_close_serial **4**, last_mutation_close_serial **5**,
last_merge_split_close_serial null. Every member has `assembly_ids={0}`
and independent inverse `{0}`. High-watermark remains **0**.

Exactly one mutation is persisted: version1/ordinal0, GROW_ADD, real
root5/event7/order0/close5, before [8606,9345,11795] GEN1 LIVE, after
[8606,9345,11795,12181] GEN2 LIVE, inverse_added=[12181], inverse_removed=[].
It retains actual score samples and original observation/W/H references.

| Checkpoint | SHA-256 |
| --- | --- |
| Event7 canonical observation | `87265149bf7ca770278f06eab98b2f3ee85ced8d1bbea0d2b954648bb6d86b3e` |
| Event7 pre-W / pre-END5 W | `3b124aeb978bfa5e080b2d5ba9656fc78f1dbaae52ec0b3da9e56bedd1f9cd40` |
| Event7 frozen H | `6b79ad7e629e8954e99131212265a37e99265206a24c3a932d83c191d3712208` |
| Physical post-evidence witness W | `93dea6f8e93cdee6366ed99a44b65bd8cf6d4be52caae971e21f654e3fb33c8e` |
| Full native post-evidence/pre-GROW W | `a30e3f5248401e5b4c56b39b16ec4047419b8178597d763bdecee3547454d91d` |
| Changed shadow before its new record is appended | `fb59e2d1ad1085c38cfd28bed6329ccb592ea7d3d2001f639c1531c869637ba1` |
| Published W after END5 and END6 | `240aa43d90731aeadc2b2f862da0f7e6f2093c6f87afa2d6680cec0595bce66b` |
| H after END5 | `b3eca03ad5c1f9eae079ea82766c0ff64a567780421215354bb9b55603377810` |
| H after END6 | `ea946035ba7ade8eb04561e8f2c98d5a119f911c197526989ec3e1e8b9fa652c` |
| R after END6 | `235c092696221c8aa82d3d19a597d211a54bffa07d15f74bdc3e1ca1f9396ddb` |
| SQLite logical archive | `ce340fc75d4111bb8c365d4deba42a55d907c9cbf494304210b537587382eeae` |

W after END6 is byte-identical to W after END5. Root6 has zero accepted
evidence and no generation, birth, mutation-log or ID drift. H changes
through its lawful empty-event adaptation; it is not falsely reported as
read-only. A separate interpreter independently recovers identical W/H,
ID0 GEN2, current four members, both membership indexes, original FORM
record, full GROW record and completed serial6. Cold root replay recomputes
settlement and each structural transition, rather than trusting current
members or a saved inspection result.

A read-only episode using actual feature `a` has maximum synchronous
contribution .5786495461436663. Durable W/H/root/identity/history stay
unchanged. This is retained neural processing, not Native Attractor or
peripheral readout.

## Crash, rollback and negative verification

Actual subprocess exits with code31 immediately BEFORE and AFTER END5
COMMIT recover respectively:

- OPEN root5, completed serial4, GEN1, zero mutations and original W.
- COMPLETED root5, completed serial5, GEN2, one GROW mutation and published W.

Retry/duplicate END returns the original close and never double-grows or
increments the generation again. Separate before/after-ABORT process
tests restore exact H_BEGIN, retain original GEN1 and zero mutation/close
credit, then permit a later genuine root to grow once. Exception injection
before COMMIT also preserves the full OPEN state. P04 requests refuse
before staging. Schema3/4 loader refusal preserves file bytes.

Forensic tests repair W hashes and close checksums after changing GROW
members, generation, ordering, authorizing root/event, serial, before/after
W hashes, reverse membership, original birth or archived history. Canonical
validation or independent cold historical replay rejects every case.
For root/event/hash/serial/forged-archive examples, the physical
codec alone round-trips the forged record, so passing a checksum is
explicitly not treated as authority. RootStore rederivation still rejects.

Component counterexamples establish KEEP versus FORM, lowest-ID iterative
removal, terminal archive representation and ID non-reuse, actual support
ranking and Q6 ties, no candidate revisit/resort, full-neighbor specificity,
prospective old-member KEEP, membership cap12 and size16. Physical fixture
negatives exclude one-way, CANDIDATE, EPISODIC, ASSOCIATIVE-only and
missing-D support; they confer no production authority. A finite-neighborhood
test forbids iteration over the committed population during recruitment.

A **private-copy fault simulation** exercises the bounded temporary
non-KEEP repair/codec path and produces an archived historical two-member
record. It never writes the faulted graph into RootStore. The actual
RootStore END afterward still uses the intact learned graph and grows
normally. This simulation and a forged-archive rejection are component
evidence only; neither is claimed as genuine production degradation.

A separate genuine curriculum learns an independent `ab` cohort after
the first Assembly. When another FORM becomes required, root8 END refuses
with `I4_FIRST_FORM_LAB_SCOPE_EXCEEDED`; W/H/root stay OPEN and no root8
evidence is published. MERGE/SPLIT containment is tested at component
level, not presented as an executed production MERGE/SPLIT.

## Verification commands

Local Windows Python 3.14.4. All commands below use the actual local
`.venv/Scripts/python.exe`; CI uses Python3.14 on Ubuntu and Windows.

| Exact command | Result |
| --- | --- |
| `.venv/Scripts/python.exe -m pytest -q --basetemp=.pytest-tmp -rs` | PASS: `796 passed in 377.91s (0:06:17)`; all 753 previous tests plus 43 R03 cases; no skips. |
| `.venv/Scripts/python.exe tests/experiments/i4_r03_native_lifecycle_trace.py --output docs/implementation/I4-R03-PRODUCTION-TRACE.json` | PASS, exit0; actual trace and independent recovery above. |
| `.venv/Scripts/python.exe -m ruff check .` | PASS: All checks passed! |
| `.venv/Scripts/python.exe -m ruff format --check .` | PASS: 116 files already formatted. |
| `.venv/Scripts/python.exe -m mypy` | PASS: Success: no issues found in 57 source files. |
| `.venv/Scripts/python.exe -m dgca_next verify-specs` | PASS: unchanged Core/LLA hashes above. |
| `.venv/Scripts/python.exe -m pip check` | PASS: No broken requirements found. |
| `git diff --check` | PASS. |
| `git diff --exit-code e316d66 -- docs/specs src/dgca_next/config.py tests/test_i4_r02_native_form.py` | PASS: unchanged science/configuration and accepted R02 tests. |

Targeted development passes (overlapping, not additional regression totals):

- R03 first continuation plus accepted R02 native cases: 24 passed in 58.99s.
- R03 component/production development suite: 33 passed in 81.10s.
- R03 component/production/independent experiment: 40 passed in 101.78s.
- Added faulted-shadow/forensic cases: 12 passed in 43.19s.
- Corrected forensic expectation: 11 passed in 41.30s.

Resolved development FAILs: the initial rank quantizer rejected a support
sum above one; exact Q6 sum handling corrected it. Two component inputs
initially violated the inherited episodic budget or failed to create the
intended Q6 tie; their test setups were corrected without changing laws.
The first full regression execution at the initial implementation commit
reported **1 failed, 795 passed in 619.06s (0:10:19)**. Its birth-forgery
test incorrectly required codec acceptance even though the newly added
origin-before-mutation check now rejects that forged record earlier.
The expectation was corrected to require rejection without weakening the
lineage check. Initial CI run
[41261756364](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/41261756364)
failed on Windows and cancelled the Ubuntu matrix job; it is not a passing
validation receipt. The complete corrected regression and final-head
results below supersede this resolved development failure.

Corrected implementation CI run
[41269171890](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/41269171890)
targets exactly `4cfd52d3bbc658a3a841ad61b19fd43626024e8c`.
At report capture Ubuntu completed SUCCESS, including both full pytest
runs and all other checks; Windows passed its first full suite and was
executing its repeat. This intermediate snapshot is not substituted for
the separate delivery-head acceptance receipt.

The report/trace delivery triggers a separate exact-head workflow. Its
immutable SHA/run receipt is verified before delivery and included in the
delivery response; the earlier implementation run is not substituted for
final-head CI. See the
[feature-branch workflow history](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/workflows/validate.yml?query=branch%3Afeature%2Fi4-native-assemblies-design).

The measured production trial took 45.78649430000223 seconds with parent
tracemalloc peak4,398,209 bytes, parent peak RSS39,251,968 bytes and
SQLite file/allocated size745,472 bytes. It includes instrumentation,
crash/reload checks and concurrent regression activity; child memory is
excluded. These observations introduce no performance threshold.

## Contract test and gate dispositions

| Contract test | Disposition |
| --- | --- |
| R03-T01 | Production PASS: exact accepted root4 GEN1/birth/W reproduced. |
| R03-T02 | Production PASS: authentic event7 and post-evidence support calculations. |
| R03-T03 | Production PASS: actual 3-to-4 growth, ID0 GEN2, one rooted edit, no link injection. |
| R03-T04 | Production PASS: canonical current members/inverse/history; separate interpreter and historical replay. |
| R03-T05 | Production PASS: root6 completes with unchanged W/GEN2/mutation log and zero q. |
| R03-T06 | Component/codec PASS: iterative removal, archive and non-reuse; genuine production removal/archive NOT_RUN. |
| R03-T07 | PASS: real candidate plus component rank/tie/no-revisit/capacity/size/prospective-KEEP/finite-enumeration tests. |
| R03-T08 | PASS: original FORM preserved, event-frozen coverage after GROW, no extra seed or retroactive attestation. |
| R03-T09 | PASS within staged boundary: actual additional-FORM rollback, component conservative MERGE/SPLIT guard; R04 operators NOT_RUN. |
| R03-T10 | Production PASS: read-only/no-change/ABORT/duplicate/exception/real process crashes. |
| R03-T11 | PASS: canonical and repaired-checksum cold replay forgery refusal, including archived ID retention. |
| R03-T12 | PASS: actual accepted-source Schema5 continuation; old-schema refusal, retained I3/P04 baseline; native P04 refused. |
| R03-T13 | Scope PASS: no Attractor, owners, readout, generation or automatic recycling implemented. |
| R03-T14 | Local PASS: 796 tests and all static/integrity/dependency checks; exact-head matrix is required before declaring delivery REVIEW READY. |
| R03-T15 | PASS within scope: physical trace, root IDs, scores, hashes, explicit empirical caveat. |

| Acceptance gate | Disposition |
| --- | --- |
| R03-G01 | Production PASS: lawful root5 continuation from actual R02 birth. |
| R03-G02 | PASS: deterministic MAINTAIN/GROW, KEEP distinction, immutable birth versus rooted current-generation history. |
| R03-G03 | Production PASS: physical 12181 growth with actual reciprocal Q and no new link. |
| R03-G04 | Production PASS: atomic W/H/identity/index/history persistence and cold replay; process-kill/ABORT/idempotence. |
| R03-G05 | PASS within scope: root6/read-only stability and explicit deferred-stage refusals. |
| R03-G06 | PASS: mode/schema protection, no scientific edits or unauthorized runtime capabilities. |
| R03-G07 | Local PASS: all 753 retained tests plus 43 R03 cases; final delivery requires both exact-head CI jobs SUCCESS. |
| R03-G08 | PASS within scoped engineering review: source-traceable actual experiment and disclosed production-archive limitation. |

## Changed files

Implementation commit changes 15 files:

- `.github/workflows/validate.yml`
- `docs/implementation/I4-R03-SCHEMA5-STRUCTURAL-JOURNAL.md` (new)
- `src/dgca_next/graph/native_assembly.py`
- `src/dgca_next/graph/native_lifecycle.py` (new)
- `src/dgca_next/graph/native_mutation.py` (new)
- `src/dgca_next/graph/network.py`
- `src/dgca_next/learning/native_lifecycle.py` (new)
- `src/dgca_next/persistence/graph_codec.py`
- `src/dgca_next/persistence/native_codec.py`
- `src/dgca_next/persistence/native_store.py`
- `src/dgca_next/persistence/store.py`
- `tests/experiments/i4_r03_native_lifecycle_trace.py` (new)
- `tests/experiments/test_i4_r03_native_lifecycle_trace.py` (new)
- `tests/test_i4_r03_components.py` (new)
- `tests/test_i4_r03_production.py` (new)

The corrective test commit updates only `tests/test_i4_r03_production.py`.

Delivery additions: this report and
`docs/implementation/I4-R03-PRODUCTION-TRACE.json`. The accepted R02 trace
and verification report remain unchanged.

## Remaining limitations and recommendation

Genuine production MAINTAIN **removal/archive is NOT_RUN / EMPIRICAL_LIMITED**.
The approved curriculum yields a stable strongly reciprocal graph; no
lawful degradation curriculum was demonstrated here. The implementation's
removal/archive arithmetic, repair boundary, codec and forensic refusal
are component-tested and explicitly distinguished above. This is the
qualification permitted by the R03 contract, not proof of full lifecycle
science. No inability claim is inferred from an unexecuted experiment.

MERGE/SPLIT, native Attractor, contextual owners/pins, readout/outbox,
Replay, text generation, automatic recycling and schema4 import remain
NOT_RUN/unimplemented. LG-T03 now has production membership-generation
change/restart coverage, but its full merge/split/peripheral-ledger
scenario remains NOT_RUN. Earlier scientific-coverage classifications are
not upgraded by component success. Full native END and full I4 are not
claimed. No unresolved scientific rule was filled with a heuristic.

Final local FAIL: none; SKIPPED: none. The resolved earlier failure is
recorded above, not omitted or counted as a final PASS.
SPEC_BLOCKED/EMPIRICAL_BLOCKED: none in the mandatory 3-to-4 growth scope;
the optional production removal/archive limitation is stated separately.
**I4-R03 REVIEW READY** requires the complete final checks and exact-head
Ubuntu/Windows CI to pass before delivery. Stop for independent R03 review;
no merge into main and no R04 work is included.
