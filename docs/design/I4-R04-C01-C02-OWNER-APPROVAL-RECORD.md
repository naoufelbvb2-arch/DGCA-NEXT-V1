# DGCA NEXT — I4-R04 Owner Decisions and One-Time Autonomous Trial

**ID:** I4-R04-C01-C02-OWNER-APPROVAL-RECORD  
**Date:** 2026-11-01  
**Status:** APPROVED BY PROJECT OWNER — ONE-TIME BOUNDED R04 EXPERIMENT  
**Repository:** `naoufelbvb2-arch/DGCA-NEXT-V1`  
**Accepted source:** `feature/i4-native-assemblies-design` at `1af7dab4e82be826380d787e16cfecd8a2224f0f`  
**Normative science:** `docs/specs/DGCA_CORE_RC4_4.md`, `docs/specs/DGCA_LLA_RC4_4.md` (both design candidates, not frozen).

## Decision C01 = A — completed EXTERNAL EVENT clock

The owner approves the literal Core RC4.4 §2.0/§12.1 cooldown interpretation: `T_c=200` counts **genuinely completed external events**, not completed roots, attempted events, event IDs or elapsed time. Preserve `last_merge_split_close_serial` as a reference to the immutable historical root close. Resolve the historical close's cumulative `event_clock` and compute `age = current prospective committed event_clock - referenced close event_clock`; only `age >= 200` passes the clock gate. `None` means no prior merge/split and does not mint age. OPEN, ABORT, READ_ONLY, internal generation and REPLAY events contribute zero completed-event age. Any ID modified earlier in the SAME END is ineligible for another merge/split during that END. If historical clock provenance is missing or inconsistent, fail closed. At the 199/200 boundary use the original Core numerical rules, not new thresholds. Keep the existing schema-5 historical close records byte-stable; no extra persistent clock invented unless separately reviewed.

## Decision C02 = A — proof-first Multi-Assembly progression

The owner approves staged production MULTI-FORM and multi-Assembly MAINTAIN/GROW **through a new explicitly selected experimental capability**, without changing accepted `I3_SCHEMA4`, `I4_NATIVE_FORM_V1`, or `I4_NATIVE_MAINTAIN_GROW_V1` behavior. Respect `K_FORM_PER_END=12`, physical event-time witnesses, current W post-evidence reciprocity and true identity/history constraints. If an unimplemented/unsupported MERGE or SPLIT is actually required, fail closed rather than publish a partial END.

## Additional one-time delegation — autonomous R04 trial

The owner approves ONE trial of **bounded autonomous engineering** to complete as much of R04 as legally provable and safe. Codex may design, implement, debug, test and rework software within the written R04 master contract without requesting approval for ordinary implementation choices. Conditionally, Codex may implement real MERGE and/or SPLIT **only after producing genuine live RootStore provenance/eligibility witnesses and satisfying all versioned transaction, lineage, replay, negative and crash gates detailed in the master contract**. This is NOT unconditional permission to force the operation or to replace missing physics with fabricated assemblies, evidence or altered laws.

**Hard boundaries:** no edit to Core/LLA RC4.4, physics, thresholds or evidence policies; no unsafe migration; no automatic recycling; no generation, Attractor, contextual owner/pins or surface readout; no merge into main; no modifications to the accepted source branch. Do not label component-only scenarios as empirical production success. Any material scientific ambiguity, unsatisfied evidence gate or irreversible data-policy change without compatible versioning requires stop/isolated partial report and owner review.

## Workflow evaluation and fallback

- Run only on an isolated `experiment/i4-r04-autonomous-completion` branch created from the exact accepted source SHA. No force push, rewriting prior history or main merge.
- Codex maintains internal checkpoint commits and provenance records; one final consolidated report is required.
- If unsafe, empirically blocked or incomplete: preserve experiment branch and report; resume the accepted incremental contract/review process from the protected baseline. Do not apply experimental changes to future layers.
- If successfully independently verified: the owner **may** adopt bounded autonomous workflow for L5 in a separate decision. No automatic adoption by this record.
- An honest `PARTIAL_BLOCKED` can demonstrate good workflow discipline, but is **not** equivalent to completion or scientific acceptance of R04.

**The earlier PENDING proposal is superseded by this owner record only for the decisions explicitly named above.**
