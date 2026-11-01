# DGCA NEXT — I4-R04 Owner Decisions C01/C02 Before Native Multi-Assembly Work

**ID:** I4-R04-C01-C02-OWNER-DECISION-PROPOSAL
**Date:** 2026-11-01
**Status:** **PENDING OWNER APPROVAL — PROPOSAL ONLY; NOT PRODUCTION MUTATION AUTHORIZATION.**
**Baseline P00 delivery:** `7b6a6a99ac5d9609b0f1dec1bdfee3f0c10168de`
**Independent P00 review:** docs/implementation/I4-R04-P00-INDEPENDENT-ACCEPTANCE-REVIEW.md
**Science authority:** CORE RC4.4 and LLA RC4.4, unchanged DESIGN CANDIDATES.
**Branch:** feature/i4-native-assemblies-design; main remains I3-accepted `88fc596c178c8a89c24b991e280d7a0ca8c07779`.

## C01 — What exactly does T_c=200 count?

**Existing literal scientific rule:** Core §2.0 and §12.1 use `T_c=200 completed external events`, NOT `T_c=200 roots`. Existing `last_merge_split_close_serial` is a stable reference to a **completed-root close**. `RootStore.end` already computes cumulative completed-event clock from prior genuinely completed external roots plus the finalizing current root's actual event count. Both root closure status and event prefix are journal validated.

**C01-A — RECOMMENDED, preserves the current scientific wording:**
- Preserve field `last_merge_split_close_serial` as an immutable reference to actual root CLOSE serial. Its name does not define the cooldown unit.
- Map the close serial to that historical close record's `event_clock` (the committed prefix of genuinely completed external events).
- At the present legitimate END, use its **prospective committed** cumulative `event_clock`, not event IDs or count of attempted/incomplete records.
- Define `age_completed_external_events = event_clock_now - event_clock_at_last_merge_split_close`. Permit an otherwise legal MERGE/SPLIT only when age >= 200. If the Assembly has never merged/split (field None), skip the cooldown gate without fabricating age 200.
- OPEN/ABORTED events, READ_ONLY, REPLAY, INTERNAL_SELECTED and GENERATE do not advance this cooldown. One genuine completed root containing five events advances event age five, not one.
- If an ID has been MERGED or SPLIT earlier in the same atomic END, it cannot be selected for another such operation in that END: effective age=0, even if the root contains multiple valid external events. Enforce the Core one-pass ordering and explicit same-END edit-set guard.
- Historical proofs: 199 actual completed external events since prior edit -> BLOCKED; 200 -> ELIGIBLE FOR FURTHER GUARDS (not automatically mutate). No fictitious completed roots, no arbitrary caller scalar. Verify separate one-event/multi-event completed roots and interspersed ABORT/READ_ONLY under full replay.
- If a past close-record/event prefix is missing because a future retention scheme pruned it, refuse `MISSING_COOLDOWN_CLOCK_PROVENANCE`. Any future redundant cached prefix must be canonical, versioned and cross-checked to original close history; do not silently substitute root serial units.
- Schema5 R02/R03 full history remains unchanged: no new persistent clock field is needed for the current append-only lab.

**C01-B — NOT RECOMMENDED without scientific amendment:** treat `last_merge_split_close_serial` numerical difference in root-close units as age. This would contradict the literal `completed external events` wording for multi-event roots. Do not implement B based solely on the field name.

**OWNER DECISION REQUESTED:** **Approve C01=A** as the engineering binding of the existing Core cooldown, without changing CORE/LLA documents or the value 200.

## C02 — Controlled path to real MERGE/SPLIT reachability

Current P00 empirical results:
- A: one live ID0 GEN2 size4, LOCAL reciprocal R=.44519573230279136; no second identity for MERGE and no size6 for SPLIT.
- B: legitimate seven physical cells; an END that could approach size>=6 is blocked by the existing R03 `I4_UNIMPLEMENTED_MERGE_SPLIT` laboratory guard. No size6 LIVE record exists.
- C: genuine mixed seven-cell first cohort would require >one disjoint FORM seed; R02/R03 containment blocks its END with `I4_FIRST_FORM_LAB_SCOPE_EXCEEDED`, leaving zero identities. Existing numeric fixtures DO NOT prove two real production identities.

**C02-A — RECOMMENDED staged proof-first experimental expansion:**
1. First add a **new explicitly selected experimental execution capability** for multi-Assembly structural reachability, retaining the accepted `I4_NATIVE_FORM_V1`, `I4_NATIVE_MAINTAIN_GROW_V1` and `I3_SCHEMA4` behaviors unchanged.
2. Extend *normal* Core §2.0 FORM from one first seed to its existing `K_FORM_PER_END=12` limit, with real event-time witnesses, sorted disjoint seed selection, persistent distinct never-reused IDs, exact source-root birth proofs and atomic close/replay. No source, scientific constant or ledger shortcut.
3. Extend MAINTAIN/GROW to accept multiple LIVE Assemblies and membership overlap<=M_max with real reverse indexes/history. Continue to **block** any END that would actually require unimplemented MERGE/SPLIT; do not merely disable the safety guard in all scenarios.
4. For an END with two live assemblies where no MERGE is eligible (or every pair is currently on cooldown), and an Assembly size>=6 where no SPLIT partition is eligible, the native full-stage checker must show a *lawful no-op* after complete read-only eligibility evaluation; such END may close only if all Core stages can be safely discharged. Do not presume all possible states are safe. Until the independent native MERGE/SPLIT writer exists, any affirmative eligible MERGE/SPLIT must fail closed, without publishing partial root evidence, generation, identity or membership changes.
5. Test actual first two native identities created from a fresh RootStore graph and independently recovered, real prospective Jaccard/exclusive R and measured overlap after lawful GROW; separately test actual size6+ LIVE retained identity and cross-pair R. Report unreachable states with full actual W/physical link/RootStore witness traces; no injected structural links.
6. Do not treat real production multi-FORM/multi-GROW as proof of an eligible MERGE or SPLIT. A **separate subsequent contract** must authorize irreversible actual MERGE/SPLIT only when its empirical conditions can be lawfully reached, its journal/lineage schema and cooldown clock are accepted, and atomic crash/replay tests are specified.
7. Treat source provenance of a SPLIT-derived Assembly as **derived structural birth** from its actual parent/partition, never three invented external FORM witnesses. MERGE must archive the other parent without falsely reusing its AssemblyID.
8. Maintain Schema5 history, readonly old journal bytes, existing R02/R03 files, no Schema3/4 migration, no P04/automatic-recycling coexistence, no Attractor/owners/readout/generation.

**C02-B — larger, riskier alternative:** implement multi-object formation, MERGE writer and SPLIT writer in one increment before obtaining a real two-identity/six-member physical witness. NOT RECOMMENDED because it widens atomic history and scientific risk and may leave only fixture-confirmed outcomes.

**OWNER DECISION REQUESTED:** **Approve C02=A** to authorize drafting a bounded MULTI-ASSEMBLY REACHABILITY implementation contract (not the MERGE/SPLIT writer itself). Implementation starts only after that contract is reviewed, status AUTHORIZED, and its versioned persistence/forensic gates are complete.

## What owner approval does and does not do

Approval of C01=A and C02=A would:
- Set an unambiguous, directly Core-derived completed-EVENT cooldown binding.
- Permit specifying a new bounded experimental route to *measuring genuine MERGE/SPLIT prerequisites* in the production graph.
- Preserve all earlier science and accepted source/replay contracts.

Approval would NOT:
- Claim the actual 200-event operational cooldown has been executed.
- Give permission to perform native production MERGE/SPLIT now.
- Authorize a new numerical law, physical rewiring, schema3/4 migration, native Attractor, semantic/generative capability, main merge or a fake Assembly identity.
- Declare R04 or I4 scientifically frozen or fully implemented.

**Pending owner response:** C01=A? C02=A? Both decisions remain PENDING until explicitly approved, with written status transition before any runtime integration.
