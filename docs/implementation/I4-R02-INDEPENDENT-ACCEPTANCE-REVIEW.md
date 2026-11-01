# DGCA NEXT — I4-R02 Independent Engineering Acceptance Review

**Document ID:** I4-R02-INDEPENDENT-ACCEPTANCE-REVIEW
**Date:** 2026-10-31
**Audited delivery SHA:** `c66eb570b03e7653d9fa1f16c1805d52ad5f9072`
**Verdict:** **I4-R02 ACCEPTED — ONE GENUINE PRODUCTION NATIVE FORM IN AN ISOLATED FIRST-LANGUAGE SCHEMA-5 LAB.**
**Final-head CI:** run `41246354720`; head_sha exactly `c66eb570b03e7653d9fa1f16c1805d52ad5f9072`, Ubuntu and Windows jobs both completed SUCCESS.
**Scientific authority:** unchanged CORE RC4.4 and LLA RC4.4; DESIGN CANDIDATES, not a scientific freeze or language understanding demonstration.
**Main:** unchanged at `88fc596c178c8a89c24b991e280d7a0ca8c07779`.

## Independent verification basis

Reviewed the pushed R02 report and changed-file diff, the actual `graph/native_assembly.py`, `learning/native_form.py`, `persistence/native_codec.py`, `persistence/native_store.py`, `tests/test_i4_r02_native_form.py` and the event/root replay integration points. Verified exact final-head CI outcome and matching SHA directly from GitHub. The report records **753 local pytest PASS**, zero failures or skips, Ruff, formatting, mypy, dependency checks and RC4.4 hash integrity; reviewer did NOT independently execute Python tests or subprocess trials.

New explicit `RootStore(..., execution_mode="I4_NATIVE_FORM_V1")` uses experimental SQLite schema-5 and canonical native W/close v5, with schema3/4 rejection instead of migration; the default `I3_SCHEMA4` path remains available and P04 stays disabled in native mode, as explicitly approved D01=A/D02=A.

## Actual physical outcome

A fresh no-link/no-cell/no-Assembly production database receives authentic external `(("a","1"),)` root events. Root 1 commits cells `8606,9345,11795,12181`, no same-birth link or Assembly. Roots 2/3 produce CANDIDATE LOCAL links with distinct root mass 1 and 2. At root 4, event IDs 5/6, actual same-END evidence consolidates all twelve directed LOCAL links among those four cells. Exactly six specified keys of chosen triangle `(8606,9345,11795)` each have `S=1,E_ext=3,E_int=0,Q=.3,external_count=3`, accepted distinct root IDs 2,3,4, legal D and full physical evidence.

Each reciprocal support R=.3, degree=2, density=1, full physical LANGUAGE-neighbor specificity=2/3 (including physical neighbor 12181). First actual externally witnessed eligible event is root 4/event 5/order0, direct X_fixed=1000000, committed_event=0, frozen final A=.7266155086363637, theta_emit=.253. This event is NOT retrospectively credited to the newborn Assembly as an earlier-existing object.

At atomic END root 4/close serial 4, the engine actually publishes ONE distinct native W record: AssemblyID **0**, LANGUAGE, LIVE, `member_cell_ids=(8606,9345,11795)`, `structural_generation=1`, birth and mutation close serial=4, merge/split serial None, high watermark=0. Each member's `Cell.assembly_ids` and independent member inverse index is `{0}`; the fourth physical cell has no Assembly membership. A rooted first-FORM journal entry is persisted with original event provenance.

## Audit and negative evidence

R02 production codec includes a separately auditable W5 envelope with original physical graph and new registry, inverse membership and form journal; historical replay recalculates genuine root synapse settlement then native FORM rather than trusting user-supplied members. Reopen in a separate interpreter and actual injected process exits before/after END commit preserve exact pre/post root, W/H, Assembly identity and no duplicate ID/evidence. ABORT does not create a native record; duplicate END returns original close. Tampered birth lineage, broken inverse/cell membership, wrong counters or missing reciprocal support fail closed. The report gives actual W/H/R/checkpoint hashes and measured time/storage.

The invariant restriction is explicit: **any second native END after first FORM currently raises `I4_UNIMPLEMENTED_MAINTAIN_GROW` and leaves root OPEN**. A real independent multi-cohort scenario with more than one legal disjoint FORM seed fails closed as `I4_FIRST_FORM_LAB_SCOPE_EXCEEDED`. These are safe guards, not passed MAINTAIN/GROW or full multi-Assembly FORM. Archive ID non-reuse has only a COMPONENT simulation. Production P04+native coexistence, schema-4→5 migration, native Attractor, contextual ownership, readout and generation are NOT_RUN. Full LG-T01 is now achieved **for the scoped first native FORM**, while LG-T03 full lifecycle and LG-T16 end-to-end outbox/readout remain NOT_RUN.

## R03 critical implementation obligations

**C01 current birth-membership immutability:** `validate_native_state` currently requires `NativeFormRecord.members == NativeAssemblyRecord.member_cell_ids`, generation exactly 1 and last mutation at birth. R03 MUST distinguish IMMUTABLE birth provenance from CURRENT structural members, preserve the old FORM journal without rewrite, and add a canonical rooted MAINTAIN/GROW mutation ledger and replay audit.

**C02 temporary shadow invalidation:** Before MAINTAIN/ARCHIVE can legitimately repair a degraded Assembly, calling full `graph.validate_graph()` on intermediate post-evidence W may reject it. R03 must separate structural-before/after audit, permitting a bounded in-transaction temporary unsound Assembly only while repairing; only fully valid final W may publish. No relaxed final codec or loaded-state validation.

**C03 stage order and fail-closed deferred work:** The Core specifies MAINTAIN→GROW→FORM→MERGE/SPLIT at each END. R03 must execute correct MAINTAIN and GROW without silently claiming MERGE/SPLIT. An explicit guard must reject any root requiring unsupported MERGE/SPLIT or multiple births beyond allowed lab scope, preserving pre-close OPEN state; no unconditional no-op pretending to implement all §2.0 operators.

**C04 meaningful production evidence:** Native `(8606,9345,11795)` has physical fourth reciprocal neighbor `12181`. On a later lawful completed external root, this existing fourth cell is a promising real GROW candidate (d=3,D=1,Spec≥.3 and size4), but it remains a hypothesis until a genuine completed native END test. R03 must measure it, preserve ID0 and correctly increment generation and mutation serial without changing underlying six-link evidence or adding fabricated memberships.

**C05 persistent future data policy:** schema-5 first-lab databases, including already born native Assemblies, need full deterministic cold replay and corruption tests across revisions. Existing schema-3/4 remain untouched and fail closed under native loader; no silent migration. I3 baseline/regressions remain mandatory.

**Disposition:** I4-R02 ACCEPTED only for its actual first native FORM engineering slice. I4 remains PARTIAL. Authorize R03 design/execution contract preparation under owner-approved staged I4 plan, but not any scientific law change, automatic recycling, contextual pins, readout or main merge.
