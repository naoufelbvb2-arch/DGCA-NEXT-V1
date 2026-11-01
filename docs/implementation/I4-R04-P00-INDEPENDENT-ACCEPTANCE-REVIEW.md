# DGCA NEXT — I4-R04-P00 Independent Feasibility Acceptance Review

**ID:** I4-R04-P00-INDEPENDENT-ACCEPTANCE-REVIEW
**Date:** 2026-11-01
**Reviewed delivered report/implementation SHA:** `7b6a6a99ac5d9609b0f1dec1bdfee3f0c10168de`
**Decision:** **I4-R04-P00 ACCEPTED — BOUNDED READ-ONLY MATHEMATICAL & PHYSICAL REACHABILITY INVESTIGATION. NATIVE MERGE/SPLIT NOT IMPLEMENTED OR PROVEN.**
**Verified exact-head CI:** GitHub Actions run `41324518123`, `head_sha=7b6a6a99ac5d9609b0f1dec1bdfee3f0c10168de`, Ubuntu and Windows both COMPLETED/SUCCESS.
**Scientific authorities:** CORE RC4.4 SHA `3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c`; LLA RC4.4 SHA `ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0`; unchanged, DESIGN CANDIDATES, NOT FROZEN.

## Independent evidence reviewed

Independently retrieved the complete P00 verification report, exact commit diff, pure `graph/merge_split_analysis.py`, read-only authenticated `persistence/reachability_inspection.py`, component/falsification tests and official RootStore production experiment source. Matched final GitHub Actions head SHA and both platform jobs. Reviewer **did not independently execute** 827 pytest tests or reproduce the full production experiment and did **not independently retrieve/parse the large JSON trace**; claims are audited against committed report and code, not a second experiment run.

Local verification as recorded: **827 tests PASS** (796 retained+31 new), 0 final FAIL/SKIP, Ruff/check/format, mypy, source integrity, pip checks PASS. The diff creates only two read-only/numeric source modules, tests, trace and report; **no change** to previous writers, native END, canonical W/RootStore codec, config or scientific sources.

## Actual measured physical scope

- **A_REINFORCED:** actual fresh production roots, one LIVE Assembly ID0 GEN2 size4 `8606,9345,11795,12181`; 12 lawful directed CONSOLIDATED LOCAL keys each `Q=.44519573230279136`, reciprocal pair R same. Only one real LIVE ID and size<6: `MERGE_NOT_APPLICABLE` and `SPLIT_NOT_APPLICABLE`. Root7 empty external event preserves W (no passive forgetting).
- **B_SEQUENTIAL_OVERLAP:** genuine `a` plus `f617` SIC produces seven committed receivers; existing ID0 remains size4. Additional links are candidate-only and provide no Assembly structural R. Root9 END refuses `I4_UNIMPLEMENTED_MERGE_SPLIT` with exact OPEN rollback; this does NOT constitute a real six-member Assembly or SPLIT.
- **C_SIMULTANEOUS:** seven receivers from legitimate mixed first event; first multiple disjoint FORM need at root4 hits `I4_FIRST_FORM_LAB_SCOPE_EXCEEDED`, leaving 0 native IDs, OPEN root, no evidence from rejected END. No permission was bypassed to fabricate a second Assembly.
- Read-only inspection and independent cold reopen keep W/H/R, actual root journals, Assembly registry, synaptic evidence and SQLite bytes immutable.
- Separate genuine clock trial shows one completed root of 1 EVENT plus one of 5 EVENTs yields completed roots=2 but **completed events=6**. Three later events of an ABORTED root and READ_ONLY do not contribute to either completed-prefix count.

## Strict numerical-only scope (NOT production identity)

- **MERGE:** nonempty exclusive sets in each parent, Jaccard≥.70, between-exclusive mean reciprocal R≥.40, lawful union KEEP and capacity. Two size-6 sets sharing five (union7) yield `5/7=.7142857142857143`, while two size5 sharing four yield `4/6=.6666666666666666`. In the actual uniform four-cell clique only one ID exists; uniform GROW of two future overlapping identities may absorb the same union and make exclusive sets empty, so structural reachability still needs a genuine differentiated curriculum.
- **SPLIT:** source size≥6, two sides each≥3, all cross supports≤.15 AND cross mean strictly<.10, within-side KEEP. Numeric-only 16-member bounded splitter evaluated 32,631 anchor-normalized cuts, measured .6792s / 6480 bytes additional tracemalloc. This is no evidence of a physical split.
- In current positive-only external learned baseline E_int=0 and CONSOLIDATED directed S≥.60,E≥3 gives Q≥.18. Thus any genuine nonzero reciprocal CONSOLIDATED LOCAL cross pair has R≥.18 and fails the weak-cross ceiling .15. A valid split cut must have **zero structural reciprocal cross edges** (unless an as-yet-unexecuted change to legal scope/evidence policy applies). Inactivity alone does not decay E/S; numeric tests at saturation do not confer a legal forgetting operation.
- Component tests exercise exact Jaccard, strength, capacity, partition ranking and safety but **cannot** authorize an actual Assembly birth/archive/merge/split.

## Cooldown governance finding

CORE RC4.4 §2.0 and §12.1 explicitly say **`T_c=200 completed external events`**, while native Assembly stores a root-based `last_merge_split_close_serial`. These are different counters when a completed root contains more than one event. CORE and LLA distinguish completed external events from completed exposure roots; LLA root-based latent recycling clock does not redefine Assembly cooldown.

**Recommended owner decision C01:** treat the saved close serial as a reference to the actual completed-root close record, then derive that close's cumulative `event_clock` and compare it with the prospective END's true completed external event prefix. `age = event_clock_at_current_completed_END − event_clock_at_last_merge_or_split_close`. Require age>=200. An ID edited in the same END remains ineligible for another MERGE/SPLIT in that END (age0), regardless of multiple event snapshots. OPEN/ABORT/READ_ONLY do not age. No new counter is needed while complete close history is retained and root close records are immutable; future pruning must explicitly preserve event-prefix provenance.

This **binding is a proposal**, NOT installed code or owner-approved policy. If alternative root-unit binding is requested, it conflicts with the literal completed-event wording and requires an explicit scientific-law decision. Operational 199/200 and real re-edit were NOT_RUN; their tests were numeric-only.

## Next blockers and approved action boundary

- Need owner approval for exact close-to-event-prefix binding C01 and same-END age0/cooldown semantics before irreversible writer.
- Need lawful production reachability of ≥2 distinct LIVE Assemblies with nonempty exclusive members for MERGE and/or ≥6-member valid Assembly with weak genuine partition for SPLIT; current lab modes explicitly contain those domains. No promise that lifting a guard will manufacture eligibility.
- Need separately reviewed multi-object lineage, immutable true FORM births versus derived SPLIT identity, MERGE archive/reuse-safe ID ledger, versioned W5 and close-record replay/checkpoint policy. Preserve accepted R02/R03 journals.
- Full I4 and R04 remain PARTIAL; no production MAINTAIN removal/archive proof, MERGE/SPLIT, native Attractor, surface readout, language generation, contextual ownership or automatic recycling.
- **No main merge** and no RC4.4 source edits or production MERGE/SPLIT execution are approved by this independent review.

**Final disposition:** Accept P00 as a scoped negative/feasibility research result with no mutation authority. Prepare explicit owner C01 decision and a separate next investigation/integration contract once prerequisites are approved; do not label mathematical positive examples as native production MERGE/SPLIT successes.
