# I4-R04-P00 reachability and cooldown investigation

Date: 2026-11-01, America/New_York. Repository
`naoufelbvb2-arch/DGCA-NEXT-V1`, branch
`feature/i4-native-assemblies-design`.

Implementation/experiment revision:
**`c50d733f19455fbe82d7a2ae0d90f754b7e0675e`**.
Approved contract parent: `9cddebaa2b2cd818790c40a89649b986e6c022a7`.
Accepted R03 delivery: `439430c14132bc9d139504da46f4278b4fb412e9`.
The report/trace delivery commit and its exact-head CI receipt are supplied
in the delivery response, avoiding a self-referential commit hash.

**Investigation outcome:** MERGE and SPLIT are
**NOT_REACHABLE_IN_CURRENT_LAB** under the existing containment. Mathematical
examples pass as NUMERIC_ONLY. No production MERGE/SPLIT happened or was
implemented. Cooldown binding requires the explicit future decision
**I4-R04-COOLDOWN-SPEC_DECISION_REQUIRED**. These are findings of the
authorized P00 study, not fabricated operator successes or a full R04 PASS.

## Authority and preserved implementation

Read the complete R03 independent acceptance review and P00 contract.
The two scientific specifications had already been read completely in
the preceding implementation work; P00 verified their unchanged bytes
and re-audited the exact relevant laws. Read all eight native graph,
lifecycle, mutation, FORM, codec/store modules specified by the contract,
plus the complete accepted Schema-5 journal policy.

| Sole normative scientific authority | Unchanged SHA-256 |
| --- | --- |
| CORE RC4.4 | `3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c` |
| LLA RC4.4 | `ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0` |

Core §2.0 owns operator equations/order/identity; §3.1 owns numeric/Q6
comparison; §10.2 owns atomic close ordering; §§9.4 and 12.1 own
nonretroactivity and the repeated cooldown wording. LLA §§0, 4.1–4.4,
6.6 and 7–7.1 own genuine link evidence, positive-only updates, provenance
and learning/read-only separation. Neither document is scientifically
frozen by this work.

P00 adds two isolated read-only/numerical modules. Every preexisting file,
including all RootStore END code, graph writers, codecs, persistence
schemas, native identity/generation rules, configuration and the 796
existing regression tests, remains unchanged. No new clock is installed.
Fresh experiment databases use the existing
`I4_NATIVE_MAINTAIN_GROW_V1` capability. The existing FORM/GROW operations
run lawfully through RootStore; no artificial native record is supplied.

`inspect_reachability` accepts only an actual native RootStore and
journal-validated LIVE IDs. Unknown, repeated or scalar/object-substituted
IDs fail closed. It independently validates the stored state, reads
actual directed LOCAL records and reuses the existing physical reciprocal
pair calculation. Candidate/episodic/ASSOCIATIVE/absent/illegal directions
provide no structural R. Mathematical results remain labeled NUMERIC_ONLY;
all result types explicitly provide no mutation authorization.

## MERGE mathematics and identity requirements

Core §2.0 requires the stage after MAINTAIN/GROW/FORM, ascending live ID
pairs, cooldown, Jaccard >=.70, exclusive-side mean R >=.40, union size
<=16, all union members passing KEEP (d>=2,D>=.35,Spec>=.20) and lawful
membership capacity. All missing exclusive cross-pairs count as zero in
the mean. Either empty exclusive side makes the mean zero. Thus identical
or nested memberships fail even with perfect Jaccard/strong internal W.

For shared count c and nonempty exclusive counts p,q, J=c/(c+p+q).
The smallest union satisfying the .70 condition is c=5,p=q=1:
two size6 sets, five shared, union7, J=5/7=.7142857142857143.
Two size5 sets sharing four instead give 4/6=.6666666666666666 and fail.
The exact .70 boundary and .40 strength boundary, including inherited Q6
ties, are tested. No new rounding rule is introduced.

The committed NUMERIC_ONLY example uses two six-element sets in a
seven-element complete scalar graph R=.5. Both sources have d=5,D=1,
Spec=5/6; union members have d=6,D=1,Spec=1. The sole exclusive pair mean
is .5. It passes the mathematics but has no native identities, root
authority or learned synapses. It is not evidence of production MERGE.

Membership capacity coalesces owners: for a union member, subtract its
old membership in each participating ID, then add its one surviving
membership. A cell at capacity12 in both has count11 afterward, and an
exclusive member at12 stays12. No fictitious third-ID debit is charged.
Retention tests use whole-region neighbors, not only proposed members.

Future MERGE must retain the lower ID and its immutable birth, increment
its generation for the union membership change, archive the higher ID
without ID reuse, remove the higher ID's LIVE inverse references and
preserve both source histories. P00 constructs no such records.

There is an additional reachability issue beyond acquiring two IDs:
uniform reinforcement of one complete clique would let GROW fill both
identities to the same union. The resulting empty exclusive sides fail
MERGE. A future lawful curriculum must preserve non-identical overlap
after GROW, for example by genuinely reaching different KEEP/GROW
specificity conditions. No such curriculum or numerical retuning is
claimed here.

## SPLIT mathematics and physical implications

Core §2.0 requires a LIVE source size>=6 after MERGE and cooldown.
Enumerate bounded bipartitions with at least3 on each side and the
smallest member in L; all side members must pass KEEP and capacity.
Every cross R must be <=.15 and mean cross R must be strictly <.10.
Choose the deterministic minimum by inherited Q6 mean then sorted L/R.
The old ID remains on L and advances generation; R would require a new
monotonic ID. No ID is allocated in P00.

Component tests cover two dense 3-cliques with zero/weak scalar cross
support, strict mean equality refusal, a single excessive cross edge,
side KEEP failures and deterministic ties across multiple partitions.
These are equations, not physically learned structures. Sub-threshold
scalar R examples preserve the literal Spec equation even where its
numerator/eligible-neighbor denominator gives a value above1; there is
no invented clipping. Such examples do not establish legal consolidated
synapse provenance.

For size16, streaming enumeration examines **32,631** anchor-normalized
bipartitions. It prunes on the first excessive cross edge, then mean,
then KEEP; it retains only the best accepted partition. The NUMERIC_ONLY
two-8-clique benchmark examines32,631, rejects32,630 on cross support,
and retains exactly the original 8+8 cut, max/mean cross0, each side
d=7,D=1,Spec=1. Measurement: **.6792074999539182 seconds**, peak additional
tracemalloc **6,480 bytes** during analysis (the input mapping was already
allocated). This bounds the candidate-domain search at16; there is no
4096-cell subset search or dense logical-network matrix.

LLA §§4.1–4.4 give a stronger physical constraint for the current
positive-only/no-Replay baseline. A legal consolidated direction has
S>=.60, E>=3, E_max=10, E_int=0, hence Q>=.18. A nonzero reciprocal
consolidated pair therefore cannot satisfy cross R<=.15. A production
SPLIT in this baseline must cut pairs with structural R=0, not merely
slightly weakened consolidated bridges.

Positive y>=.60 and weighted updates preserve S>=.60; external evidence
does not decay when observations stop. Below saturation, Q increases
with valid q. At E=10, Q can decrease if a new y is lower than S, but
remains >=.60, far above the weak-cross threshold. It is incorrect to
assume Q is always monotonic at saturation, or that inactivity weakens a
bridge. The genuine passive-root check below observes unchanged W.

FORM begins from a connected triangle, and GROW adds physically attached
members. An alternative involving lawful MAINTAIN removal of connector
members could change induced connectivity without deleting knowledge;
that needs a complete genuine growth/removal trajectory. R03 did not
prove production removal/archive, and P00 does not prove that trajectory
or impossibility of the broader model. Current size/identity containment
already prevents reaching the required domain.

## Genuine fresh production experiments

The [full production trace](I4-R04-P00-PRODUCTION-TRACE.json) records four
separate new databases. Root numbers are scoped to their database; they
are never pooled as independent credits in one graph. All inputs use
canonical support string1 and genuine RootStore external EVENTs.
Trace SHA-256:
`9d2b408a6ee3c2518530c10cd12b86009959bd251f99cf8ab5fd590de50b1409`.

**A_REINFORCED:** Root1/event0 commits the four `a` receivers. Roots2–4
use two events per root (IDs1–6), reproduce first FORM ID0 GEN1 at close4;
root5/event7 grows it to four members GEN2. Root6/events8–9 reinforce
the graph; root7/event10 is a valid empty external event and leaves W
byte-identical to the preceding close. There are7 completed roots and11
completed external events. LIVE ID0 GEN2 members remain
**[8606,9345,11795,12181]**, birth4, last mutation5, no merge/split timestamp.

All twelve directed LOCAL keys among these four cells are CONSOLIDATED:
E_ext=4.526984324968987, E_int=0, S=.9834267148822992,
Q=.44519573230279136, five accepted roots [2,3,4,5,6]. The six reciprocal
pairs are 8606↔9345, 8606↔11795, 8606↔12181, 9345↔11795,
9345↔12181 and11795↔12181, each R=.44519573230279136. Although these
weights exceed .40, there is only one identity and four members:
**MERGE_NOT_APPLICABLE / SPLIT_NOT_APPLICABLE**.

**B_SEQUENTIAL_OVERLAP:** Reproduce A roots1–5, then root6/event8 supplies
`(("a","1"),("f617","1"))`. The legal new cohort is
[8200,10035,10926], sharing original receiver8606 through the actual SIC
projection. The resulting seven committed receivers are
[8200,8606,9345,10035,10926,11795,12181]. Roots7/8 use two mixed events
each (IDs9–12). Root9/events13–14 have actual direct support1,000,000,
all seven Pass-1 emitters/F_step members and final activity1 on event14.
Its126 pending proposals are staged observations, not accepted root9
evidence. END9 refuses **I4_UNIMPLEMENTED_MERGE_SPLIT** and preserves the
entire pre-close OPEN checkpoint, including W/H/R and next order2.

Persisted state has8 completed roots/13 completed events and one LIVE
ID0 GEN2 of size4. Its twelve original LOCAL directions are CONSOLIDATED,
E_ext=6.053363620285735, S=.9751258287686266,
Q=.5902791217068981, external count7. The remaining thirty LOCAL
directions are CANDIDATE, E_ext=2,S=1,Q=.2, external count2, so their
structural R is **zero**. No size6 or size7 native record was committed.
The actual source guard refuses the potentially affected >=6 domain;
this does not prove a legal weak-cut SPLIT or native MERGE.

**C_SIMULTANEOUS:** Start from zero with the mixed seven-receiver input
at root1/event0, then two events per root. Roots2/3 learn42 LOCAL
directions with E_ext=2,S=1,Q=.2, all CANDIDATE, plus lawful ASSOCIATIVE
learning. Root4/events5–6 stage126 proposals; END refuses
**I4_FIRST_FORM_LAB_SCOPE_EXCEEDED**. The checkpoint remains OPEN/order2,
completed roots3/events5, with **zero native identities**. No extra FORM
is forced, and the rejected root's proposed consolidation is not reported
as persisted learned structural evidence.

Each case begins with zero cells/synapses/Assemblies. Every inspection
compares full StoreView, H bytes, SQL logical archive and database file
bytes before/after. All are identical across inspection. Actual read-only
SIC episodes preserve them too. A separate interpreter cold-opens each
database, including the OPEN B/C cases, and reproduces the complete
inspection and all archive/file bytes exactly. All real Assembly births
and growth use existing RootStore code; no NativeAssemblyRecord is minted
by the P00 analyzers.

| Database / terminal checkpoint | W SHA-256 | H SHA-256 |
| --- | --- | --- |
| A, completed root7 | `38b78f70f512853772689441541d1740b5b36d9949731d2589cbd15548645b0a` | `0af99cdb12f1014c5e99f6ff9fc5a833da4f9a79eee499aadb25a1856489c84b` |
| B, OPEN root9 | `4c0e495d3a31dfb9c9a801c8a23f15a0cc310d410e4f3b507df3a98807975399` | `84c6e9898ee2d097f74401dcc12f8216a08ccf70f0688c7fb8dfa5b27b3f0272` |
| C, OPEN root4 | `43890931fe569ae53cd4ec3f7c987a4eb8a06be8e6752c2ef309d1f9cff35cc6` | `fcf08c0d2b547f57fb3d35339e28bc410f8ee88852c610615c6c8514ddb7739c` |

SQL archive digests: A
`ca95e4f81bde6bcfafa3d95dd808d00862519118926dfbc1a392b92b6988bcdf`;
B `56cf8a8569b7740e5b49ddda2532a5850e0d56f75fe31a2f539c931695f3cd72`;
C `a5823d4d837da6c47b1e0b5e02560a9ee9edd9fc0ec84316b76db44027ff2c45`.
The JSON contains exact R digests, per-direction physical/credit records,
event witnesses, root history and file digests. Database byte/allocated
sizes are A1,007,616; B2,269,184; C1,134,592. Total instrumented trial
29.229234299971722 seconds, peak parent RSS51,838,976 bytes; child memory
is excluded. These are measurements, not new thresholds.

## Cooldown investigation and decision request

Core §2.0 explicitly says **200 completed external events**, repeated in
§12.1. The persisted field is `last_merge_split_close_serial`; the current
close_serial counts completed independent roots. They are not equal when
roots contain multiple events. LLA §7 distinguishes those two concepts;
LLA §7.1's completed-root clock for latent recycling does not silently
redefine Core's Assembly cooldown.

The separate genuine clock trial records:

| Actual root | Actual global EVENT IDs | Status | Close serial | Cumulative completed events |
| --- | --- | --- | --- | --- |
| 1 | 0 | COMPLETED | 1 | 1 |
| 2 | 1,2,3,4,5 | COMPLETED | 2 | 6 |
| 3 | 6,7,8 | ABORTED | none | still6 |

While root3 is OPEN, its three events do not enter the completed prefix.
ABORT restores exact H_BEGIN and does not advance completed roots/events.
A genuine read-only episode creates no root or clock increment. After
cold reopen the history is still two completed roots, six completed
events, three aborted events. W:
`4e096af360e57fc661fcc5dab6fc1a128dc8cb965612926d8546ddbc69a29f90`;
H `37ad564b1f2bffde3a88bfebee412083a1cb0a5bc1c451926ff5c0e73197bb22`.
There was **no real MERGE/SPLIT edit** in this trial; numeric reference0
means start of history, not a fabricated stored edit timestamp.

Two explicit interpretations are reported, never selected by the runtime:

1. **ROOT interpretation:** age=current completed close minus stored last
   close; require >=200 root closes. This yields2 for the diagnostic
   start reference and differs from the literal event wording.
2. **EVENT interpretation, recommended for owner review:** treat the
   stored close serial as a reference to its root-close record; derive
   age=current completed event_clock minus event_clock at that referenced
   close. The current close record already persists/replays this cumulative
   count, so this requires no newly invented production clock. It yields6.

Core's literal wording supports EVENT; the explicit binding between the
named close-reference field and that event prefix, including prospective
END and same-END re-edits, must be approved in the next execution/data
contract. P00 does not install either policy. A request to use ROOT units
instead would require explicit scientific authorization, not an implicit
engineering substitution.

Numeric-only boundary tests show199 fails and200 passes under each chosen
unit; a hypothetical199-event root plus one-event root reaches event200
while having only2 root closes. These are **not** a claim that P00 ran200
genuine completed roots or verified an operational cooldown. The real
1-versus5 experiment is the actual counterexample above.

**Decision C01:** approve literal completed-EVENT age with the existing
close-to-event-prefix mapping, or specify a different authorized law.
Clarify exclusion of OPEN/ABORT/READ_ONLY, stamp after the current root's
events, >=200 boundary and age0 for another merge/split involving a just
edited ID in the same END. Until that decision the diagnostic returns
`I4-R04-COOLDOWN-SPEC_DECISION_REQUIRED`, not guessed mutation eligibility.

If historical close records are later pruned, a proposed versioned cached
`last_merge_split_completed_event_clock` (canonical unsigned64 plus the
close reference) must be cross-checked by replay and preserve accepted
old bytes. That is a future proposal only; no counter/schema/migration is
added here. The full existing journal already supplies the prefix.

## Future multi-object identity and persistence plan — NOT IMPLEMENTED

The R03 audit reveals concrete blockers that must not simply be removed:

- `guard_deferred` blocks multiple LIVE or size>=6; FORM has a separate
  first-seed lab cap. Those need a future authorized domain contract.
- Current native audit rejects non-null last_merge_split_close_serial.
  Mutation v1 accepts only MAINTAIN_REMOVE, GROW_ADD and terminal 3-to-2
  ARCHIVE; it cannot represent multi-object MERGE or a new SPLIT child.
- Every current registry ID requires a `NativeFormRecord` with exactly
  three original genuine witnesses. A SPLIT descendant must not be
  disguised as a newly witnessed FORM or backdated sensory admission.
- Current close codec and replay recompute only accepted R02/R03 stages.
  Unknown record fields/versions fail closed; widening one constructor
  without authentic historical operator replay would be unsafe.

Proposed future data contract, requiring independent approval:

1. Add a separately versioned identity-operation journal preserving all
   old W5/Form/mutation-v1/close bytes until a new operation occurs.
   Record ordered stage, root/event transaction authority, completed close
   and approved clock prefix, both source IDs/generations and immutable
   birth references, post-evidence witness W hash, before/after versions,
   exact members/statuses/generations and inverse deltas. Never renumber
   old mutation ordinals or discard archived identities.
2. MERGE links both parents, retains lower-ID birth, advances the changed
   survivor generation and archives the higher ID with historical members.
   The higher ID's status-only archival must not invent another membership
   change or satisfy the unrelated terminal-MAINTAIN archive shape.
3. SPLIT keeps original ID on L, advances it, and allocates one ID from
   the retained regional high-watermark for R. Add an explicitly derived
   SPLIT-birth record referencing the parent/version and partition proof,
   rather than fabricating three external FORM witnesses. Propose the
   accepted administrative initial generation1 for the new ID for review;
   do not silently change birth namespaces or provenance.
4. Require exact one-pass MAINTAIN→GROW→FORM→MERGE→SPLIT order and
   same-END cooldown state. Validate all affected objects/indexes and
   publish with ordinary evidence/root completion in one transaction.
   Replay each old record under its exact version and rederive each new
   identity operation from its original root snapshot. Test failed-root,
   crash, duplicate-delivery, high-watermark, tamper and old-file behavior.
5. A changed or archived generation cannot inherit earlier peripheral
   attestations or fresh Attractor authority. Core §§2.0/9.4 and LLA §7.1
   require future independent confirmation. P00 adds no ledger, Attractor,
   readout or generation implementation.

Old readers must fail closed on new extensions. Accepted R02/R03 files
must still load/replay without rewrite; schema3/4 migration remains
separately gated. No future field or writer above is implemented by P00.

## Validation, files and gate dispositions

New files in the implementation commit:

- `src/dgca_next/graph/merge_split_analysis.py`
- `src/dgca_next/persistence/reachability_inspection.py`
- `tests/test_i4_r04_p00_math.py`
- `tests/test_i4_r04_p00_inspection.py`
- `tests/experiments/i4_r04_p00_trace.py`
- `tests/experiments/test_i4_r04_p00_trace.py`

Delivery adds this report and
`docs/implementation/I4-R04-P00-PRODUCTION-TRACE.json`. All are additions;
no preexisting implementation/science/test file is changed.

| Exact local Windows command | Result |
| --- | --- |
| `.venv/Scripts/python.exe -m pytest -q --basetemp=.pytest-tmp -rs` | PASS: `827 passed in 587.51s (0:09:47)`; all796 prior regressions plus31 P00 cases; no skips. |
| `.venv/Scripts/python.exe tests/experiments/i4_r04_p00_trace.py --output docs/implementation/I4-R04-P00-PRODUCTION-TRACE.json` | PASS: exit0; genuine separate-process evidence above. |
| `.venv/Scripts/python.exe -m ruff check .` | PASS: All checks passed! |
| `.venv/Scripts/python.exe -m ruff format --check .` | PASS: 122 files already formatted. |
| `.venv/Scripts/python.exe -m mypy` | PASS: Success: no issues found in59 source files. |
| `.venv/Scripts/python.exe -m dgca_next verify-specs` | PASS: both exact RC4.4 hashes above. |
| `.venv/Scripts/python.exe -m pip check` | PASS: No broken requirements found. |
| `git diff --check` | PASS. |
| `git diff --exit-code 9cddeba -- docs/specs src/dgca_next/learning src/dgca_next/persistence/native_codec.py src/dgca_next/persistence/native_store.py src/dgca_next/persistence/production_store.py src/dgca_next/graph/native_assembly.py src/dgca_next/graph/native_lifecycle.py src/dgca_next/graph/native_mutation.py` | PASS: scientific sources, learning/END, native writers and persistence untouched. |

Targeted development: mathematical cases plus genuine experiment
**29 passed in35.22s**; actual-ID/schema4 refusal tests **2 passed in1.52s**.
The complete suite contains **827 = 796 retained +31 new** tests.
Targeted counts are not added again to that full total.

Implementation CI
[41272440664](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/41272440664)
completed SUCCESS on Ubuntu and Windows for exact
`head_sha=c50d733f19455fbe82d7a2ae0d90f754b7e0675e`, including both full
pytest executions and all static/integrity/dependency/cleanliness checks.

The separate report-head CI must match the delivered commit on both OS;
its immutable SHA/run and observed result are in the delivery response and
[branch workflow history](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/workflows/validate.yml?query=branch%3Afeature%2Fi4-native-assemblies-design).
An earlier successful code-head run is not substituted for final-head CI.

| Contract test | Disposition |
| --- | --- |
| P00-T01 | PASS: 827 tests, all static/integrity/dependency checks and code-head CI; final delivery matrix is additionally required. |
| P00-T02 | NUMERIC_ONLY PASS: Jaccard/cardinalities/empty exclusives, .70/.40/Q6 boundaries and capacity. |
| P00-T03 | PASS: actual qualified versus candidate LOCAL pairs; inherited physical reciprocal/ASSOC/missing-D negative regressions retained. |
| P00-T04 | Production PASS: genuine A/B/C measurements; actual one-ID size4 and exact containment refusals. |
| P00-T05 | NUMERIC_ONLY PASS: dense3-clique cuts, single-cross/strict-mean/side-KEEP/ranking negatives. |
| P00-T06 | NUMERIC_ONLY PASS: streaming32,631 size16 cuts and measured pruning/resources. |
| P00-T07 | Investigation PASS: genuine1/5-event roots, OPEN/ABORT/READ_ONLY controls, explicit unresolved policy and numeric-only boundaries. |
| P00-T08 | PASS within present domain: actual LIVE ID validation and scalar/unknown/repeated-ID refusal; no real archived production identity is manufactured. |
| P00-T09 | Production PASS: exact W/H/R/root/credit/identity/archive/file preservation and separate cold processes. |
| P00-T10 | PASS: old compatibility regressions plus byte-unchanged codecs/writers; future migration/lineage proposal only. |
| P00-T11 | PASS: no MERGE/SPLIT writer, artificial identity, forced FORM, recycling or semantic runtime labels. |
| P00-T12 | Local measurements PASS; final exact-head Ubuntu/Windows CI required before delivery. |

| Acceptance gate | Disposition |
| --- | --- |
| G01 | PASS: exact bounded non-mutating mathematical analysis; numeric fixtures labeled. |
| G02 | PASS as investigation: production operators NOT_REACHABLE_IN_CURRENT_LAB, with measured physical/stage reasons. |
| G03 | PASS as investigation: literal-event recommendation, genuine counterexample, explicit owner decision still required. |
| G04 | PASS: current identity/history blockers and auditable future multi-object/versioning plan; no writer. |
| G05 | PASS: immutable actual inspection and cold recovery. |
| G06 | PASS: honest failures/negative controls; no fake production outcome. |
| G07 | Local/code-head PASS: all796 prior regressions plus31 new cases and unchanged science; final-head matrix must pass before delivery. |
| G08 | PASS within P00: factual source-traceable report and clearly gated future authorization. |

## Recommendation and stop

Do not authorize irreversible production MERGE/SPLIT from a mathematical
fixture or the existing four-cell clique. First obtain independent P00
review, decision C01 and the derived-birth/multi-object data contract,
then authorize a genuine reachability curriculum/domain integration.
Current results do not establish which operator should be implemented
first. Both need additional physical evidence; bridge weakening by
inactivity is unsupported by the current laws.

Full R04/I4 remains PARTIAL. Actual MERGE/SPLIT, operational cooldown,
production removal/archive proof, Attractor, owners, readout, Replay,
generation, automatic recycling and schema3/4 migration are NOT_RUN.
The cooldown question blocks **future production implementation**, not
the authorized P00 task of exposing and documenting it. No normative
scientific source or constant has been changed to obtain a result.

Final local validation FAIL: none. SKIPPED: none. Code-head CI: both PASS.
Stop at **I4-R04-P00 REVIEW READY** only after the complete investigation
checks and exact-head matrix pass. No main merge or irreversible R04
implementation is included.
