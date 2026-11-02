# I4-R04 autonomous consolidated verification

Verification completed locally on 2026-11-02 (America/New_York).
Both real scoped operators and all local verification gates pass. Final
delivery requires completed SUCCESS on BOTH OS for the commit containing
this report; the final handoff supplies its exact SHA/run and release verdict.
This report is an engineering review submission, not independent acceptance.

## Authority and boundaries

Execution uses `experiment/i4-r04-autonomous-completion`, created directly
from `1af7dab4e82be826380d787e16cfecd8a2224f0f`. The owner approval and Master
Contract were copied to the requested paths. The supplied README provided
packaging context; the user's explicit launch request supplied authorization.
The old pending proposal was superseded only on the specifically approved
C01/C02 decisions. No main merge or protected-feature push is authorized.

The only scientific authorities remain the two unchanged RC4.4 sources:

| Source | SHA256 |
|---|---|
| CORE | `3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c` |
| LLA | `ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0` |

There is no scientific migration, new threshold, automatic recycling,
Attractor, contextual owner, readout, generation, R05 or L5 implementation.

## What was implemented

- C01 binds cooldown to actual completed external EVENT prefixes. A saved
  last-merge/split close reference resolves that close's historical event
  clock. Same-END edited IDs have age0; missing provenance refuses.
- `I4_NATIVE_MULTI_V1` supports actual multiple FORM births, shared-capacity
  multi-live MAINTAIN/GROW, exact cap12/defer behavior and versioned operator
  inspection. A required unsupported operator refuses the entire END.
- `I4_NATIVE_OPERATORS_V1` adds lawful MERGE/SPLIT after actual production
  eligibility was measured. Synaptic evidence settles first; native stages
  preserve the exact frozen post-synaptic physical graph and H at END.
- MERGE keeps the lower ID/birth, advances its generation, archives the
  higher ID with its historical member tuple/generation, and updates both
  membership indexes. Archived identifiers are never reused.
- SPLIT keeps the original ID/birth on L, advances its generation, and
  allocates a derived child on R with generation1 and actual parent/partition
  provenance. The child receives no invented external FORM witness.
- Optional versioned W5 operator records and a separate close envelope allow
  exact historical reconstruction across FORM, MG and native operators.
  Accepted old readers refuse the extension; accepted old records are not
  rewritten. Every published W passes the full graph/current-KEEP audit.
- Read-only forensic exports preserve complete canonical W/H/R, original
  journal birth events, initial slot choices, final L_t and H snapshots.

The default I3, R02 and R03 operator modes retain their original behavior.
Experimental close version1 retains its original generic no-FORM diagnostic
under replay; version2 reports an absent reciprocal triangle precisely.
Operator closes have an additional explicit version. No silent downgrade or
schema3/4 migration occurs.

## Bounded production experiments

Every learning trajectory starts with a new empty production RootStore.
Features are mechanical external harness inputs. No FixtureBuilder, inserted
synapse, manually created native membership or expected-answer authority is
used. Independent evidence roots are independent only within their original
database. Continuations/crash copies preserve the same lineage and never
count as additional independent learning evidence.

| Trial | Roots/events | Actual outcome |
|---|---|---|
| F01 r1 | 7/11 | Accepted single cohort grows to four members. |
| F02 r1 | 8/14 | Two genuine births at root4, then identical seven-member live sets. |
| F03 r1 | 10/17 | Sequential overlap reaches one seven-member Assembly. |
| F04 r1 | 5/93 | Twelve genuine seeds at root4; deferred thirteenth born from root5's new event. |
| F05 r1 | 49/131 | Two identical ten-member sets; specificity remains `.23929273697448764`. |
| F05 r2 | 69/191 | More training changes later admission conditions; original sets remain ten members, specificity `.2982090621746224`. |
| F05 r3 | 59 attempted | Frontloaded lawful commitments yield a real eligible zero-cross SPLIT at root59; old capability refuses END atomically. |
| F06 r1 | 131/373 | Initial distinct identities converge to identical seven-member sets; MERGE has empty exclusives. |
| F06 r2 | 109 attempted | Frontloaded commitments yield distinct six-member sets with a real eligible MERGE at root109. |
| Reference clock | 4 completed roots/201 events, plus3 aborted | Genuine reference ages199/200, with no fabricated Assembly edit. |
| F07 | 4 completed roots/200 events,1 aborted root/3 events | Actual edit ages0/1/6/199/200, unchanged W/generations and complete cold replay PASS. |

F01–F06 use six curriculum families. F05 uses all three allowed revisions;
F06 uses two. F07 is a separately declared actual-stamp control. F08 is unused.
The earlier reference-clock control is separately bounded. No additional
feature curriculum is introduced. The failed F02 reporter's8 completed
roots/14 events and the explicitly nonauthoritative6-root development probe
are logged separately; neither is silently counted as another learning root
in the successful F02 lineage.
Every input screen and revision was declared before execution in the
append-only engineering changelog. No search is extended to force a result.

The first F02 reporter failed after its eight roots had completed because it
passed tuple instead of frozenset to materialization, then lacked Enum JSON
serialization. Its real final state and recovery are retained separately.
The identical curriculum was rerun after those reporting repairs.

The early Pass-1 explanation of admission differences was corrected:
ordinary latent selection uses frozen final **L_t**, not Pass-1 emission.
For F05r2's root55/event148, `theta_active=.6`, cell8606's pre-event gain is
`.7689705360355605`, final activity `.5592512989349532`, and the original
core is absent from L_t. Root40/event105 has final activity
`.6096915743122016` and still includes the core. Increasing repeated evidence
cannot retroactively replace those original physical slot choices.

## Physical MERGE/SPLIT evidence

The authoritative pre-writer receipts are `F05-r3.json`, `F06-r2.json` and
`authorized-pending-operator-witnesses.json`. Their positive calculations are
explicitly **provisional END shadows**, not completed mutations. Both original
OPEN journals cold-replay unchanged. The approved conditional writer work
began only after these genuine eligibility receipts were recorded.

For F06r2 at root109, the real live parent sets are:

- ID0 generation4: `8606,9345,10035,10926,11795,12181`.
- ID1 generation4: `8200,8606,10035,10926,11795,12181`.

They share five cells; Jaccard is `5/7=.7142857142857143`, exclusives are
`9345` and `8200`, and actual reciprocal exclusive support is `.4`. The union
has seven members, all current KEEP/capacity guards pass, and both IDs are
never edited. Committed writer d6da169 publishes ID0 with generation5
on the union and archives ID1 at root109/event prefix307. Original FORM
births remain root4/root16; archived ID1 retains its last live generation4.

For F05r3 at root59, ordinary MAINTAIN removes the four old core members
from each ten-member Assembly. Each real parent reaches generation12 and
members `8200,8467,10035,10512,10744,10926`. The selected partition is:

- L: `8200,10035,10926`, each internal degree2, density1, specificity1/3.
- R: `8467,10512,10744`, each internal degree2, density1, specificity1/3.

Every cross support and the cross mean are exactly zero. Internal supports
are `.4` in L and `.3` in R. No link was deleted or weakened to create the
cut. Committed writer d6da169 publishes IDs0/1 on L, generation13, and
derived IDs2/3 on R, generation1, at root59/event prefix161. Their birth
provenance is derived, not a fabricated external triangle event.

Canonical receipts are `F05-r3-publish.json` and `F06-r2-publish.json`.
Both independently cold-replay the complete historical RootStore and pass
duplicate END, injected in-process BEFORE_COMMIT exception rollback, exact
H-at-END preservation, all prior learned-link/credit preservation and actual
read-only neural-session immutability. All new stamps report age0.

| Published state | DB bytes | Cold DB SHA256 |
|---|---:|---|
| SPLIT | 442466304 | `c4febc61a86b233bd4d0115a9da660e31c3bd4f3c1b5b8a00ab204ac04e23323` |
| MERGE | 298717184 | `c3f0985cb046d38ef5264cafea33c990c26ae1548e292092938fae2dd584adf0` |

Frozen physical post-synaptic W hashes are respectively
`908a01608f9202bf46916754a2473015f903d5546e00e234f8abd08143ba0520`
and `e8d349e4c55c3f7e2553fdf062bd5fe36b1cfcf30bc10509d58e690cbf08a6d8`.
Actual SPLIT source event is160/order2/digest
`b1517a0303ca31e1c594508c1c2d284d48b3dbcd4de42ef672c18fb360aa5867`;
MERGE source event306/order2/digest
`170dc2b12419230d928aeabe90c884367e30ee930a4f124bfe0cffa19717ad24`.
The canonical receipts contain complete W/H/close bytes, operator parent and
child rows, numerical checks, native history, read-only activity and the
before/after W/H/R hashes. These control copies are the SAME original
lineage, not additional independent external confirmations.

These are actual post-settlement reciprocal LOCAL links. Every listed
direction is CONSOLIDATED, has S=1 and E_int=0. Both directed credits have
q=y=1 on each listed independent completed root. Thus each SPLIT side has
all six required directed links; all nine between-side reciprocal supports
are zero. No expected-answer label participates in these calculations.

| Physical pair (both directions) | Q forward/reverse = R | E_ext/count per direction | Genuine root IDs |
|---|---|---|---|
| SPLIT 8200 /10035 | .4/.4 | 4/4 | 2,3,4,5 |
| SPLIT 8200 /10926 | .4/.4 | 4/4 | 2,3,4,5 |
| SPLIT 10035 /10926 | .4/.4 | 4/4 | 2,3,4,5 |
| SPLIT 8467 /10512 | .3/.3 | 3/3 | 7,8,9 |
| SPLIT 8467 /10744 | .3/.3 | 3/3 | 7,8,9 |
| SPLIT 10512 /10744 | .3/.3 | 3/3 | 7,8,9 |
| MERGE exclusive 8200 /9345 | .4/.4 | 4/4 | 106,107,108,109 |

The initial two BEFORE_COMMIT crash reporters failed after real exit73 and
successful cold construction: the expected dictionary had an additional
descriptive `assemblies` key. Their failures are retained. The repair
compares all five checkpoint fields and separately all Assembly rows, then
rechecks the SAME crashed files. It does not replace the crashed databases
or suppress any changed checkpoint field.

Both AFTER_COMMIT controls pass and exactly match canonical W/H/R and completed-root counts.
Both corrected BEFORE_COMMIT recoveries pass on the original crashed files. Both ABORT
controls also pass complete cold replay and exact H_BEGIN restoration.

Both repaired-clock controls reject with INVALID_CLOSE_CHECKPOINT; independent SQL reads
verify that all repaired hashes actually match. Both additional numeric-proof controls
reject after full historical rederivation, with all repaired checksums independently
verified. F07 also passes full independent cold verification, as detailed below.

Bare W decoding checks canonical structure and lineage, not external
historical authority. In particular, an internally coherent altered
historical event clock can pass bare decoding. Full RootStore historical
rederivation must reject the repaired-checksum forged journal; separate
negative control copies test this boundary for BOTH operators.

## Engineering repairs and execution provenance

The final representation audit reproduced a strict-type bug: bare decoding
accepted region2.0 in an operator before-row because Python Enum coercion
converted it to region2. Commit6af1043 requires an integer region and list
member vector before conversion. Actual publisher output always used those
types. Both genuine saved W states still roundtrip, the malformed-row cases
now refuse, and no numerical law or valid historical byte is changed.
A fresh full884 regression passes in1057.77s after this correction. The complete24-case
saved-state suite passes in17.61s. Exact-source both-OS CI also passes884 twice per OS.

The canonical operation driver records the repository SHA at launch and the
initial database revision separately. F07's original driver records gitHEAD
when writing its final receipt; that field must not be read as the launch
SHA. Its parent launched at db80407; the stricter malformed-row validation
was added while long controls ran. Receipts retain their actual recorded
fields; final-source saved-state and full regression checks are separate.
No control copy counts as another independent learning root.

## Completed atomic and forgery controls

Each control starts from a byte-identical source copy. Corrected BEFORE
checks reuse the original actual crashed files. All source metadata and
immutable original root/event witnesses remain distinct from these copies.

| Control | SPLIT seconds / result | MERGE seconds / result |
|---|---|---|
| Canonical publication, in-process rollback, duplicate END, cold replay | 1934.01 /PASS | 1792.93 /PASS |
| BEFORE_COMMIT actual exit73, corrected full cold recovery | 1062.09 /PASS | 763.85 /PASS |
| AFTER_COMMIT actual exit73, full cold recovery | 1692.45 /PASS | 1592.78 /PASS |
| ABORT, exact H_BEGIN, no evidence/operator, cold recovery | 1781.47 /PASS | 1740.14 /PASS |
| Altered historical clock, repaired hashes, full RootStore refusal | 1814.03 /PASS | 1756.12 /PASS |
| Altered numeric proof, repaired hashes and synchronized close checks | 1852.06 /PASS | 1799.54 /PASS |

Both forged-clock values change161 to162 for SPLIT or307 to308 for MERGE.
The numeric controls change only zero cross mean to5e-324, or between
strength.4 to.4000000000000001, respectively. These are deliberate corruptions
of stored proof, not scientific thresholds or new observations. In all four
cases the current strict structural decoder accepts the well-shaped bytes,
independent SQL checks confirm W/close/checkpoint hashes really match, and
full RootStore rederivation refuses `INVALID_CLOSE_CHECKPOINT`.
`forensic-repair-audits.json` retains those independent checks and exact
alterations. The original genuine databases are never edited by forgeries.

## Maintenance and limitations

F06r2 contains actual completed-root MAINTAIN at root69: IDs2/3 remove9345,
change4→3 and generation2→3. Root105 similarly removes8200 from IDs6/7.
Births and underlying learned links remain intact. Root59's F05r3 removals
are staged with the SPLIT and publish only when the operator END succeeds.

The actual failing specificity at root69 is
`2.7/13.773569973539841=.19602760977632683`; at root105 it is
`2.7/13.8=.1956521739130435`. Degree3 and density1 remain valid, so the
whole-region specificity guard causes removal. Both completed roots retain
the learned synapses; the remaining triplets meet KEEP. No terminal
MAINTAIN ARCHIVE was reached in the declared trajectories.

No genuine terminal MAINTAIN ARCHIVE is claimed: observed removals leave
legal three-member cohorts. R03's archival representation/removal components
remain component evidence. MERGE archival of the higher ID is a different
observed operation. No claim is made that structural operators improve
learning, supply language output, or activate a Native Attractor.

The full bounded production curricula and process controls execute locally
on Windows/Python3.14.4. Ubuntu/Windows CI runs the complete regression suite
twice, including actual saved-state codec/lineage checks; it does not rerun
every long curriculum/control driver. Cross-platform bit-identical neural
activity and SQLite file layout are not claimed. Exact cold W/H/R equality
is verified on the same backend, with the accepted physical fingerprint
vectors retained in both CI jobs.

## Verification ledger

The final complete local command is:

```powershell
.venv/Scripts/python.exe -m pytest -q --basetemp=.pytest-tmp/final-884
```

Exact result: `884 passed in 1057.77s (0:17:37)`, zero FAIL/SKIPPED.
All827 accepted baseline tests are unchanged;57 new cases are collected.
`final-verification-receipts.json` independently checks all13 canonical
publication/recovery/forgery/actual-clock receipts and records their hashes.

| Run | Result |
|---|---|
| Initial focused cases | 14 PASS in52.46s. |
| Expanded focused cases | 16 PASS in57.16s. |
| First full collection | 841 PASS in280.49s. |
| Trace/cap focused run | 18 PASS in268.35s. |
| Forensic controls | 3 PASS in5.65s. |
| Full pre-diagnostic collection | 848 PASS in545.97s. |
| Draft diagnostic test insertion | Historical1 FAIL/5 PASS in47.11s; misplaced body caused NameError; fixed without disabling the test. |
| Corrected diagnostic case | 1 PASS in.39s. |
| Full diagnostic-version collection | 850 PASS in960.25s. |
| Operator codec refusal components | 6 PASS in.35s. |
| Operator capability plumbing/real FORM-GROW | 3 PASS in2.45s. |
| Operator-source full collection | 859 PASS in1199.47s. |
| Reporter repair regression | 1 PASS in.20s. |
| Pre-type-hardening full collection | 878 PASS in1309.32s (21:49). |
| Union/partition saved-state components | 22 PASS in22.32s. |
| Strict typed-row saved-state suite | 24 PASS in17.61s. |
| Final complete source collection | 884 PASS in1057.77s (17:37). |
| Ruff | PASS: `All checks passed!` |
| Formatting | PASS: `140 files already formatted` |
| Mypy | PASS: `Success: no issues found in 66 source files` |
| Specification integrity | PASS: both exact unchanged RC4.4 hashes shown above. |
| Dependencies | PASS: `No broken requirements found.` |
| Working `git diff --check` | PASS, empty output. |
| Source/config diff against exact parent | PASS, empty output. |
| Existing test modifications | PASS, empty output; no baseline test changed. |

Exact static commands, stdout/stderr, exit codes and hashes are retained in
`final-static-checks.json` at source6af1043. Supplied authority Markdown has
intentional two-space hard line breaks: its original staged whitespace
warning is retained in the changelog. Byte-exact authority copies are
preserved; no claim of clean whitespace for that entire parent-range is made.

Final FAIL: none. Final SKIPPED: zero. Historical reporter/type/command
failures and failed curriculum hypotheses remain recorded, rather than
being erased by the final passing result. NOT_RUN is separately listed for
unexecuted scientific scenarios. No mandatory scientific/data-policy
ambiguity remains within the approved C01/C02 scope (SPEC_BLOCKED: none).

Exact-source CI6af1043660b1ab9d8bcbc1d0dc65c38839cb9de2 completed BOTH OS
SUCCESS in run[41387112975](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/41387112975):

| Job | First full pytest | Second full pytest | Other required steps |
|---|---|---|---|
| Windows | 884 PASS in459.64s | 884 PASS in448.11s | All SUCCESS |
| Ubuntu | 884 PASS in574.61s | 884 PASS in567.88s | All SUCCESS |

Earlier successful checkpoints d1a0c7b/run41333669673,
779a84a/run41354395615, d6da169/run41380072803,
db80407/run41384537314 and8ac4034/run41385358138 are also retained.
`ci-checkpoints.json` marks ALL of these non-final delivery receipts.
No intermediate source run substitutes for final-head CI. The report/evidence
commit must receive its OWN matching BOTH-OS SUCCESS before REVIEW_READY;
the final handoff records that delivery SHA and run. Current delivery checks:
[experimental branch
Actions](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions?query=branch%3Aexperiment%2Fi4-r04-autonomous-completion).

No skipped scientific scenario is upgraded by unit-test success. Original
OPEN refused trials do not claim read-only neural sessions that were not
executed. The completed publication controls do execute actual read-only
processing and verify exact W/H/caller-state preservation.

## Gate dispositions

These classifications describe actual evidence, not full I4 scientific closure.

| Gate | Disposition / evidence |
|---|---|
| A1 | PRODUCTION_PASS: F02 root4 genuine two-seed eligibility; F04 cap12. |
| A2 | PRODUCTION_PASS: distinct rooted IDs, generations, inverse indexes and cold reconstruction. |
| A3 | PRODUCTION_PASS: actual two-live F02 cohort and later distinct F06r2 parents. |
| A4 | COMPONENT_PASS plus actual rejection/defer evidence: no duplicate, retroactive or ineligible FORM; ABORT and tamper cases. |
| B1 | PRODUCTION_PASS: root109 J=5/7, exclusive R=.4, union7 and KEEP. |
| B2 | PRODUCTION_PASS for actual clock binding: F07 actual stamp at0/1/6/199/200; original parents never edited; no second eligible edit claimed. |
| B3 | PRODUCTION_PASS: real atomic MERGE, survivor0/gen5, archive1, preserved births/physical W/H/credits. |
| B4 | PRODUCTION_PASS: complete cold replay, duplicate END, actual process crashes/ABORT, repaired-clock/numeric-proof RootStore refusals. Parent/union malformed-row checks are COMPONENT_PASS. |
| C1 | PRODUCTION_PASS: real six-member parent, zero-cross structural cut and legal sides. |
| C2 | PRODUCTION_PASS: deterministic real3/3 partition and exact internal/cross support. |
| C3 | PRODUCTION_PASS: two real parent continuations and two derived IDs; no invented FORM. |
| C4 | PRODUCTION_PASS: complete cold replay, duplicate END, process crashes/ABORT, repaired-clock/numeric-proof refusals. Partition/type checks are COMPONENT_PASS. |
| D1 | PRODUCTION_PASS: actual deterministic MAINTAIN removal at roots69/105; links/births preserved. |
| D2 | NOT_RUN: no genuine terminal MAINTAIN ARCHIVE reached; earlier component/codec evidence remains component-only. |
| E1 | PRODUCTION_PASS: genuine1-event and5-event roots after actual SPLIT produce ages1 and6. |
| E2 | PRODUCTION_PASS: actual edit age0 and actual199/200 boundary; same-END touched-set refusal also has COMPONENT_PASS coverage. |
| E3 | PRODUCTION_PASS: both actual operators BEFORE/AFTER_COMMIT, in-process rollback, duplicate END, ABORT/H_BEGIN and cold recovery. |
| E4 | PRODUCTION_PASS: actual OPEN/ABORT/read-only no-age checks; unsupported internal/replay paths remain component refusals, not genuine external roots. |
| F1 | PRODUCTION_PASS for persistence compatibility: old-source W5 histories generated by archived protected/early sources load byte-identically. |
| F2 | PRODUCTION_PASS for complete historical authorities and current real-state audits; structural/type forgery components PASS. |
| F3 | PRODUCTION_PASS: every prior learned link/credit prefix preserved; ordinary settlement precedes native stages. |
| F4 | COMPONENT_PASS: accepted I3/P04/default modes and regressions preserved; no native physical rewiring or automatic recycling. |
| F5 | COMPONENT_PASS: complete884, all827 unchanged baseline cases, all8 final static/compatibility checks. |
| F6 | Exact-source BOTH-OS SUCCESS as above; delivery gate requires matching report-commit BOTH-OS SUCCESS, checked before final handoff. The handoff supplies final SHA/run and verdict. |

No second eligible MERGE/SPLIT after the200-event boundary is claimed.
F07 tests genuine stamp/clock binding, not another edit curriculum.

## Actual-stamp clock and cold recovery

F07 continues a COPY of the genuinely published SPLIT lineage. Actual ID0
references immutable SPLIT close59, completed-event prefix161. No root count
is substituted for completed EVENT count:

| Root | Events | Outcome | Completed serial/prefix | Actual age |
|---|---:|---|---|---:|
| 60 | 1 | COMPLETED | 60/162 | 1 |
| 61 | 5 | COMPLETED | 61/167 | 6 |
| 62 | 3 | ABORTED | unchanged | 6 |
| 63 | 193 | COMPLETED | 62/360 | 199 |
| 64 | 1 | COMPLETED | 63/361 | 200 |

Event IDs are161;162..166; aborted167..169;170..362;363.
All OPEN inspections retain prior age; all read-only operations retain state
and age; ABORT restores H_BEGIN exactly. Duplicate END is idempotent.
Exactly200 completed external empty-feature events age the real stamp; they
produce no learned-link evidence. W and all generations remain identical
to the actual published SPLIT state. These are four additional completed
roots, not200 roots or200 independent learning confirmations.

Full cold process replay PASS after3585.46s total control wall time.
Retained DB size1,292,918,784 bytes, SHA256
`7c962db542fe5b85e4826d94495576c4a079d79426b3eea501871b43a92f7ae2`.
Final W SHA remains
`7ff03caca10a06b1a53ba60e6feaf44f21b920d7eb346bb2cb740b9e67f7d7ea`.
The final completed serial is63; no OPEN root remains.
The F07 raw receipt retains its original end-of-run repository SHA2bbfde7;
its launch was db80407, as distinguished in execution provenance above.

## Reproduction commands and retained evidence

Run from the repository with Python3.14 and installed `.[dev]`:

```powershell
.venv/Scripts/python.exe -m pytest -q --basetemp=.pytest-tmp/final-884
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m ruff format --check .
.venv/Scripts/python.exe -m mypy
.venv/Scripts/python.exe -m dgca_next verify-specs
.venv/Scripts/python.exe -m pip check
git diff --check
git diff 1af7dab4e82be826380d787e16cfecd8a2224f0f -- docs/specs src/dgca_next/config.py
```

Use a separate pytest temporary subdirectory locally: the retained production
SQLite experiments live under `.pytest-tmp/r04-verified` and
`.pytest-tmp/r04-operators`; do not erase those to run tests. CI uses a fresh
checkout and its original two full-suite commands.

Exact independent curriculum commands and predeclared features/order are
recorded in the changelog and trace JSON. Trials use
`tests/experiments/i4_r04_autonomous_trial.py`; full source/root/event inputs
and final physical states are retained, including negative outcomes.
`final-physical-snapshots.json` exports all10 original receipt-bound W/H/R
snapshots and original birth EVENT frontiers. It is archival data, not a
new external observation.

Canonical publication and controls use this exact command template, once
for each `F05-r3` and `F06-r2` family and each case:

```powershell
.venv/Scripts/python.exe tests/experiments/i4_r04_operator_execution.py --source .pytest-tmp/r04-verified --directory .pytest-tmp/r04-operators --evidence docs/implementation/evidence/i4-r04-autonomous --family F05-r3 --case publish --output docs/implementation/evidence/i4-r04-autonomous/F05-r3-publish.json
```

The other cases are `BEFORE_COMMIT`, `AFTER_COMMIT`, `abort`, `tamper_clock`, `tamper_numbers`
and `recover_before`, with matching family/case output filenames. Corrected
BEFORE receipts use `F05-r3-BEFORE_COMMIT-corrected.json` and the corresponding
F06 filename. `recover_before` rechecks the original crashed database.
Process exits intentionally use code73; this is a successful fault injection
only when the separate full cold recovery assertions pass.

```powershell
.venv/Scripts/python.exe tests/experiments/i4_r04_actual_cooldown.py --source .pytest-tmp/r04-operators/F05-r3-publish.sqlite --source-receipt docs/implementation/evidence/i4-r04-autonomous/F05-r3-publish.json --database .pytest-tmp/r04-operators/F07.sqlite --output docs/implementation/evidence/i4-r04-autonomous/F07-actual-cooldown.json
```

These long-running controls deliberately execute full historical neural and
structural rederivation; no trusted-snapshot shortcut is substituted.
Canonical publication took1934.01s/1792.93s under concurrent validation.
Token/cost/peak-memory instrumentation was unavailable; no automation
efficiency or improved-learning claim is made. A read-only process sample
at23:09 observed a Python working set of1,378,459,648 bytes during concurrent
replays; this is neither a measured peak nor aggregate memory use.

## Changed files, commits and final recommendation

The complete inventory and sequential checkpoint SHAs follow. All files
remain on experiment/i4-r04-autonomous-completion, based exactly on1af7dab.
Protected main88fc596 and feature1af7dab were independently rechecked before
delivery. No merge, protected-feature push, force-push or history rewrite
occurred. The final report/evidence commit follows the listed checkpoints;
its exact SHA and matching final-head CI run are supplied in the handoff.

Engineering recommendation: submit bounded R04 multi-Assembly/MERGE/SPLIT
for independent acceptance once final delivery CI is green. Both operators
were genuinely reached and published, without injected connections, changed
thresholds or fabricated evidence. No remaining SPEC_BLOCKED or operator
EMPIRICAL_BLOCKED exists in this approved scope. D2 remains NOT_RUN and
must not be represented as full lifecycle scientific success.

The original failed hypotheses, reporter failures and repairs remain in
the append-only changelog and saved traces. Full local/CI regression and
actual production experiments are different evidence classes. The31 saved
JSON receipts occupy about96.4MB at report freeze; original SQLite journals
and control copies remain locally under the named ignored temporary paths.
Wall times and DB sizes are measured; no cost/token efficiency, resource
scaling, better learning, language capability or global scientific freeze
is asserted.

NOT_RUN/outside scope: terminal production MAINTAIN ARCHIVE; a second
eligible edit after cooldown; rerunning every long curriculum on Ubuntu;
Native Attractor, contextual owners, readout, generation, R05 and L5.
Automatic recycling remains disabled. Stop at R04 review; do not merge,
close I4 globally or begin the next milestone without independent acceptance.

<!-- generated inventory -->

### Complete changed-file inventory

60 changed/added files relative to the exact accepted parent. No baseline test or scientific source was removed.

| File | Purpose |
|---|---|
| `.github/workflows/validate.yml` | Add isolated experiment push trigger; retain both OS jobs and existing checks. |
| `docs/design/I4-R04-C01-C02-OWNER-APPROVAL-RECORD.md` | Byte-exact supplied owner authority. |
| `docs/implementation/I4-R04-AUTONOMOUS-COMPLETION-MASTER-CONTRACT.md` | Byte-exact supplied owner authority. |
| `docs/implementation/I4-R04-AUTONOMOUS-CONSOLIDATED-VERIFICATION-REPORT.md` | Versioned scope/design, append-only decisions or consolidated verification. |
| `docs/implementation/I4-R04-AUTONOMOUS-ENGINEERING-CHANGELOG.md` | Versioned scope/design, append-only decisions or consolidated verification. |
| `docs/implementation/I4-R04-CONDITIONAL-OPERATOR-JOURNAL-DESIGN.md` | Versioned scope/design, append-only decisions or consolidated verification. |
| `docs/implementation/I4-R04-EXPERIMENTAL-CAPABILITY-POLICY.md` | Versioned scope/design, append-only decisions or consolidated verification. |
| `docs/implementation/evidence/i4-r04-autonomous/F01-r1.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F02-r1.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F02-reporter-failure.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F03-r1.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F04-r1.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F05-r1.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F05-r2.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F05-r3-AFTER_COMMIT.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F05-r3-BEFORE_COMMIT-corrected.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F05-r3-abort.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F05-r3-publish.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F05-r3-tamper_clock.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F05-r3-tamper_numbers.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F05-r3.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F06-r1.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F06-r2-AFTER_COMMIT.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F06-r2-BEFORE_COMMIT-corrected.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F06-r2-abort.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F06-r2-publish.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F06-r2-tamper_clock.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F06-r2-tamper_numbers.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F06-r2.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/F07-actual-cooldown.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/authorized-pending-operator-witnesses.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/before-commit-reporter-failures.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/ci-checkpoints.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/clock-r1.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/final-physical-snapshots.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/final-static-checks.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/final-verification-receipts.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `docs/implementation/evidence/i4-r04-autonomous/forensic-repair-audits.json` | Retained genuine production trace/control or explicitly classified forensic receipt. |
| `src/dgca_next/graph/native_assembly.py` | Explicit experimental capability, immutable lineage, canonical persistence or historical audit. |
| `src/dgca_next/graph/native_operator.py` | Explicit experimental capability, immutable lineage, canonical persistence or historical audit. |
| `src/dgca_next/graph/network.py` | Explicit experimental capability, immutable lineage, canonical persistence or historical audit. |
| `src/dgca_next/learning/completed_event_clock.py` | Explicit experimental capability, immutable lineage, canonical persistence or historical audit. |
| `src/dgca_next/learning/native_multi.py` | Explicit experimental capability, immutable lineage, canonical persistence or historical audit. |
| `src/dgca_next/learning/native_operators.py` | Explicit experimental capability, immutable lineage, canonical persistence or historical audit. |
| `src/dgca_next/persistence/multi_store.py` | Explicit experimental capability, immutable lineage, canonical persistence or historical audit. |
| `src/dgca_next/persistence/native_codec.py` | Explicit experimental capability, immutable lineage, canonical persistence or historical audit. |
| `src/dgca_next/persistence/operator_codec.py` | Explicit experimental capability, immutable lineage, canonical persistence or historical audit. |
| `src/dgca_next/persistence/operator_store.py` | Explicit experimental capability, immutable lineage, canonical persistence or historical audit. |
| `src/dgca_next/persistence/store.py` | Explicit experimental capability, immutable lineage, canonical persistence or historical audit. |
| `tests/experiments/i4_r04_actual_cooldown.py` | Bounded reproducible production experiment/control driver; no fixture learning authority. |
| `tests/experiments/i4_r04_autonomous_forensics.py` | Bounded reproducible production experiment/control driver; no fixture learning authority. |
| `tests/experiments/i4_r04_autonomous_trial.py` | Bounded reproducible production experiment/control driver; no fixture learning authority. |
| `tests/experiments/i4_r04_operator_execution.py` | Bounded reproducible production experiment/control driver; no fixture learning authority. |
| `tests/experiments/test_i4_r04_autonomous_trial.py` | Regression, production mechanism or explicitly classified codec/component verification. |
| `tests/experiments/test_i4_r04_operator_reporting.py` | Regression, production mechanism or explicitly classified codec/component verification. |
| `tests/test_i4_r04_autonomous.py` | Regression, production mechanism or explicitly classified codec/component verification. |
| `tests/test_i4_r04_forensics.py` | Regression, production mechanism or explicitly classified codec/component verification. |
| `tests/test_i4_r04_operator_codec.py` | Regression, production mechanism or explicitly classified codec/component verification. |
| `tests/test_i4_r04_operators.py` | Regression, production mechanism or explicitly classified codec/component verification. |
| `tests/test_i4_r04_production_snapshots.py` | Regression, production mechanism or explicitly classified codec/component verification. |

### Committed checkpoints

All checkpoints are on the isolated branch. The final report/evidence commit follows these recorded checkpoints; its exact SHA and matching CI run are supplied in the final handoff. Negative findings are retained without squashing.

| SHA | Change |
|---|---|
| `b83b440c404119c05a5bab9df8dc5df7de0feb11` | Record owner authorization for isolated bounded R04 trial |
| `e902f6781b4cbbba5b63f9b88fd8ad0b2a21d3e4` | Add isolated multi-Assembly capability and authenticated event cooldown |
| `5fca02cdaabf882837556b704c4e9f391a6ea711` | Retain trial failure evidence and bound specificity curriculum |
| `d1a0c7b325f8ba463ba2865b807da01a1f152928` | Record genuine multi-FORM cap and clock evidence; declare exclusive-neighbor trial |
| `ffefdf84a1b3556a03a879b314371aa18febbe2d` | Declare bounded second specificity trial from measured negative result |
| `9519cdfa2387f74de3f8655a237460d434bf3789` | Preserve negative physical trial and protected-source forensic checks |
| `6c869deb08e9797de60f87c7592fa89593149c90` | Retain negative topology evidence and predeclare frontloaded admissions |
| `2c98913c119b0cc18ecdb607694d8a98dc4d4f7e` | Add exact replay-receipt-bound physical checkpoint export |
| `779a84a31eeabcf099dcae9de225a7543dabb3b2` | Version precise FORM diagnostics without rewriting trial histories |
| `2113973d3f3d14600ae51439027f57af65d9dc0c` | Bind topology forensics to final learning frontiers and document conditional lineage |
| `abc4ac084cbda45860a259c5d615cb1c4cfbb213` | Add versioned structural lineage audit without enabling writers |
| `b38e16c5e8ec2bbf9704f3e5d026869952cd8623` | Record genuine reciprocal MERGE and weak-cut SPLIT eligibility |
| `d6da1698a64bbd4ee634379ec7e0aa0d33dc0db7` | Implement proof-gated atomic native MERGE and derived SPLIT |
| `8933bd767b9f4fe6570148e66529f154e9bc5c08` | Declare real edit cooldown experiment and extend forensic reader |
| `85595dd470c18705e4b05f855ab206f36ec1c577` | Retain crash-reporting failure and verify complete checkpoint fields |
| `db804079d17af1c97bc328a5f7161987543460e6` | Record real native operators with cold replay and lineage forgery regressions |
| `8ac4034d1590250c22a9673cb8ee1cfec67afca2` | Cover repaired numeric proofs and explicit union partition forgeries |
| `6af1043660b1ab9d8bcbc1d0dc65c38839cb9de2` | Reject noninteger regions in canonical native operator rows |
| `2bbfde73ef3f828738aeed385ea689f37818a9ef` | Record atomic process crashes aborts and repaired-clock refusals |
