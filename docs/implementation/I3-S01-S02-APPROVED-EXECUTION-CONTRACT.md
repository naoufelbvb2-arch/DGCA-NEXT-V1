# DGCA NEXT — I3 S01/S02 APPROVED EXECUTION & FULL LEARNING REMEDIATION CONTRACT

**Document ID:** I3-S01-S02-APPROVED-EXECUTION-CONTRACT
**Revision:** R01 — 2026-10-28
**Status:** AUTHORIZED FOR CODEX IMPLEMENTATION — NOT COMPLETED / NOT VERIFIED
**Repository / working branch:** naoufelbvb2-arch/DGCA-NEXT-V1 / feature/i3-local-learning
**Reviewed pre-remediation implementation:** 500f5e10c1670ce5a079f531505f68d5a839a5fc (621 PASS, 0 failures; genuine learning NOT_RUN).
**Approved owner decisions:** docs/implementation/I3-S01-S02-RESOLUTION-PROPOSAL.md
**Full inherited I3 scope:** docs/implementation/I3-IMPLEMENTATION-CONTRACT.md
**Only current scientific authorities:** CORE RC4.3 and LLA RC4.3 until coordinated RC4.4 migration; design candidates NOT FROZEN and NOT EMPIRICALLY VERIFIED.

## 0. Mission: rectify scientific blockers AND finish genuine I3

Implement both approved scientific choices, version them in the TWO canonical documents as RC4.4, then continue and finish the full I3-R00 through I3-R06 production implementation. Do not stop after replacing two preflight errors with a selector/default profile. The final success requirement is actual, reproducibly demonstrated LEARN EVENT/END from an empty target-link graph, with real root-local witnesses, independent-root synaptic reinforcement and a preserved read-only causal effect after save/load. No fixture-based proof is sufficient.

If integration cannot satisfy any hard gate, deliver safely completed parts and an exact failure report, NOT an invented learning result. DO NOT merge into main or implement I4–I7.

## 1. Source migration gate — versioned RC4.4

1. Read entire current CORE RC4.3, LLA RC4.3, source manifest, owner-approved proposal, current I3 contract and preflight. Hash raw RC4.3 source files and record archival base SHA.
2. Migrate both entire normative specs in **one auditable Git commit**: docs/specs/DGCA_CORE_RC4_3.md → DGCA_CORE_RC4_4.md and docs/specs/DGCA_LLA_RC4_3.md → DGCA_LLA_RC4_4.md. Maintain exactly TWO current canonical documents; original RC4.3 bytes remain retrievable from an immutable historical Git commit. Scientific version status: RC4.4 DESIGN CANDIDATE / NOT FROZEN / NOT EMPIRICALLY VERIFIED.
3. Core owns S01 event sensory-K_R arithmetic/priority/deferral and S02 per-cell/regional initial H profile, snapshot, virtual defaults, event and ABORT semantics; LLA records corresponding EVENT/END witness/admission compatibility and external-root provenance, without rewriting q or unrelated learning laws. Add exact owner-approved definitions **without modifying independent existing laws/thresholds**.
4. Update docs/specs/SOURCE-MANIFEST.md, src/dgca_next/integrity.py, config declarations/source section labels, tests, provenance golden fixtures, README and all current-doc references consistently in the same migration. Verify raw SHA-256 and Git blob SHA against new exact bytes, and archive RC4.3 historical SHA-256: CORE 41764eea3ddccdbd692325ecf7f03c243bf259bb46cc2b1820f7648125f3a53a; LLA 4c70fd84a8356e7871e6ac5bd14eeb800bf2347342512c4901e1e2191a89e958.
5. No transient mixed-version branch is considered COMPLETE. Preserve immutable I0/I1/I2 science audit trail via historical exact commit. Any older version fixtures must compare with pinned archival bytes, not a moving main branch.

## 2. Approved I3-S01 — sensory selection before latent ranking

For every genuine external LEARN EVENT, project canonical SIC-V1 exactly once, freeze committed-before-event physical W, and compute eligible uncommitted receiver set from X_fixed > eps_p. For I3 LANGUAGE-only lab with I5 contextual admission OFF, the full K_R=12 capacity is available to sensory births; 8/4 is nominal and transferable. Sort candidates by (-exact_integer_X_fixed, physical_cell_id) and accept at most 12 unique physical receiver IDs in ONE simultaneous K_new cohort. Remaining receivers are UNCOMMITTED and diagnosed as SENSORY_BIRTH_CAPACITY_DEFERRED; there is no automatic deferred queue or backdated same-event witness. Repeated real external observations may later admit them if still eligible.

Golden first-cold event features a,ab,c,d each support 1 yield 16 unique SIC LANGUAGE IDs:
8286,8465,8606,8649,8694,9227,9345,9902,9912,10128,10273,10513,11524,11641,11795,12181.
Choose first 12 through 10513, defer last four. All 16 have X_fixed=1,000,000. Verify shuffled feature order, merged SIC physical collisions, ties, unequal supports, NFC, repeated roots and per-event capacity.

Accepted K_new must be initialized through the already approved deterministic L01 fixed/coactive 24-slot policy using a **real validated event snapshot**, not a FixtureEventSnapshot or FixtureBuilder promoted into LEARN. Capture the entire cohort first; publish commitment, slots, reverse index and wiring metadata together atomically at EVENT close. Newborn cells cannot be sources or targets of same-event positive q, F_step or evidence; do not insert them into the pre-event committed set. No automatic "learning" by merely committing a receiver.

## 3. Approved I3-S02 — version-pinned neutral Homeostasis profile

Initial LANGUAGE H profile:

- g_cell_default = 1.0, exactly binary64;
- r_bar_cell_default = rho_cell = 0.05;
- rho_bar_LANGUAGE_initial = rho_target_LANGUAGE = 0.030;
- theta_active_LANGUAGE_initial = 0.20 (unchanged earlier Core value).
- VISION/AUDIO initial theta/homeostasis production remains UNSPECIFIED, fail closed for first LANGUAGE lab.

These are approved NEW initial policy choices; do not change Core/LLA adaptation math, rate denominators, rho_target or thresholds. Birth does not reset current adapted LANGUAGE regional theta/EMA.

**Mandatory ABORT safety:** Core §10.1 requires H_slow equals the immutable H_slow_BEGIN checkpoint byte-for-byte after ABORT while lawful already-committed sensory W may remain. Implement immutable versioned H defaults + sparse per-cell **adaptation overrides**, or another proven byte-equivalent representation. A newborn committed at EVENT close has an effective g=1.0/r_bar=.05 through virtual lookup but does not force a persisted per-cell H override. Expand to a temporary fully explicit immutable H snapshot when using I2 operators; that expansion never mutates durable H or fabricates evidence. Only cells committed BEFORE the event may earn provisional event adaptation overrides. H_BEGIN includes pre-root legitimate overrides and shared region state. ABORT restores exactly H_BEGIN even if born W survives; later read-only numeric evaluation must still resolve that newborn's effective values. Duplicate ABORT cannot revert a subsequent completed root's adaptations.

The zero-committed pre-event region skips regional EMA and theta updates as required by RC4.3 S03. The first later genuine LEARN event can adapt existing newborns. Verify atomic profile/hash/codecs, missing or mismatched schema rejects, H_BEGIN byte-identity across fail/crash/retry, uncommitted read-only W/H no-op, and unsupported VISION/AUDIO.

## 4. Production trust boundary — NO fixture laundering

**Known blockers verified in code:**
- I1 graph Synapse presently rejects fixture_only=False and FixtureBuilder is exclusive fixture authority. Introduce a separate, audited internal production learning/cell/synapse mutation API that obtains capability only from validated root EVENT/END, preserving I1 immutable public graph and all invariant audits.
- Current RootStore.event preflight creates an empty new SparseNetwork() each call; this is ONLY a fail-closed skeleton. A production EVENT must load actual durable graph W and use its frozen pre-event committed IDs, slots, live synapses, budgets and root journal. Repeated observed receivers must not be re-born.
- Current SQLite RootStore uses EMPTY_W / R_COLD markers, no durable full W codec, no completed root records, and raises SpecBlocked for EVENT/END. Replace this in the authorized production path with versioned deterministic binary64-safe W/R/H/journal state and atomic BEGIN/EVENT/END/ABORT boundaries. Preserve the old tested skeleton behavior only where genuine legacy fixtures require it, without a parallel bypassable root authority.
- I2 read_only_step has READ_ONLY provenance; do not convert its output to EXTERNAL_DIRECT evidence. Production LEARN must compute its own typed real external ObservationWitness, frozen pre-event W/H/R, neural A^(1)/A^+, F_step, event-ordered source activity, and hard-boundary histories. The API establishes source-of-event status; it cannot claim factual truth of real-world user content.

No caller-supplied q, y, "novelty", expected text, fixture graph or test oracle may authorize link creation, external root completion or evidence.

## 5. Complete the original I3 contract, not merely its two blockers

Implement according to docs/implementation/I3-IMPLEMENTATION-CONTRACT.md:

**R00** production cell/synapse schema, separate trusted origin, safety audit; **R01** transactional root store including strict BEGIN and H_BEGIN, cold R and nonreused IDs; **R02** real contiguous EVENT ingress, direct witness, sensory birth, H_EVENT provisional adaptation, event checkpoint; **R03** legitimate LOCAL Δ0 and ASSOCIATIVE Δ1 proposals only with frozen witnessed sources and valid target, Pass1 E gate, D_event + D_close, theta_create, one-sided latent OR and budgets, journaled proposals, root MAX paired q/y and END atomic publication; **R04** real evidence E_ext/E_int/S, one accepted independent root/key, no negative/replay, consolidation only under existing thresholds with E>=3/S>=.60/at least 2 independent completed roots, verified saved W/Q causal effect in read-only, complete durable crash/restore; **R05** verified event-bound X_ext and frozen pre-SIC P_T novelty authority with robust fake/ABORT rejection, bilateral age/protection checks; leave automatic production recycling OFF absent separate authorized enabled integration/ablation; **R06** an actual from-zero independent-external-root learning experiment.

Reference q creation and numeric laws EXACTLY from LLA RC4.4, inherited unchanged:
- LOCAL same-event source FINAL and target FINAL, but source **must** be in frozen Pass1 emitter E^(1).
- ASSOCIATIVE one-step source must be prior F_step and prior-frozen final A; target current eligible direct SIC. No Δ>1 learned link.
- q_ext = A_source_learn × A_target^+ × k_evidence(scope) × D for genuine LEARN, with ASSOC k_evidence=0.7408182206817179, LOCAL=1.0; neural propagation k_neural=1.0 and never multiplies k_evidence.
- positive target y = clip(theta_S + (1-theta_S)*(A_target^+−theta_active)/(1−theta_active),theta_S,1), exact inherited formula.
- positive root MAX with paired y (−q,event_order,ordinal); one credited root/key max. E_ext ≤ 10, E_int ≤ phi E_max and E_tot ≤ 10; baseline replay OFF and all negatives OFF.
- H_CONTEXT=5 but learned ASSOCIATIVE Δ fixed 1. Event-time and END latent gates both required; capacity priority and shadow arbitration deterministic. Never silently lower theta_create=.20, cross=.39 or other parameters.

An I3 root can only claim *ordinary* local/associative learning. I4 native Assemblies, I5 candidate owners/probe, I6 hierarchy and I7 readout/generation remain OUTSIDE scope; missing those does not justify learning a semantic relation using expected Y labels.

## 6. Testing requirements and explicit empirical gate

Retain all previously passing **621** I0–I3 partial regression tests and add targeted S01/S02 cases from the approved proposal.

Mandatory additional scientific executable evidence:
1. Root0 from empty physical target links: direct SIC receiver birth, 0 same-event learned q, frozen legitimate H and full K_new. Abort after admitted birth and confirm byte-identical H_BEGIN and retained lawful W.
2. Later independent external roots with lawful committed-before-event source/target, actual neural A, actual physical D and E/F frontiers: one accepted REAL production LOCAL directed edge and one REAL production ASSOCIATIVE edge generated by END without using fixture graph mutation. If no pair legally qualifies, document full physical reason, not a forced edge.
3. Repeated distinct COMPLETED external roots raise actual E_ext and external_root_count once per link/root and can consolidate only with all required evidence thresholds. Same-root repeats, aborted/READ_ONLY/replay/invalid witnesses add zero.
4. SAVE / cold LOAD returns exactly learned W synapse records, root journal high watermark, latent reverse index, budgets and H; read-only two-pass actual Q from learned edges affects neural P_S/P_T with before/after/ablation numeric traces, no caller W/H mutation.
5. Failure-injected crash before/after BEGIN, EVENT, END, ABORT must recover only complete pre/post atomic state with no double adaptation, q, count, phantom birth or root reuse. Tests must include a subprocess-kill scenario, not only exception rollback.
6. Record producer for genuine event-local novelty (X_fixed, frozen pre-SIC P_T, canonical witness/root ID, Q6 threshold), test refusal of forged source; do not enable production periodic recycling merely to make tests pass.
7. Run controlled AB→C / DB→E observation trial *as a diagnostic*; do not require I5 context owner specialization or claim text generation at I3. No hidden labels/expected outcomes in the learner.
8. Preserve all tests/gates required by original I3 contract, including I3-T01–T28 and I3-G01–G08. Report separately which named LLA-T tests were actually executed **as complete scientific integration**, rather than asserting all 41 passed from fixture math; LG-T01–T16 all NOT_RUN.

If the *real learned-link* test fails with no lawful candidates, verdict MUST be I3 PARTIAL / EMPIRICAL_BLOCKED, not PASS. If a new unapproved scientific gap is material, report SPEC_BLOCKED with source, minimal reproducer and affected subgate; finish independent lawful parts.

## 7. Executable sequence and validation

Checkpoint A: atomic RC4.4 source migration and source integrity, document exact changed scientific lines and comparison to RC4.3. Baseline and targeted unit tests.
Checkpoint B: production admissions + H profile + ABORT identity tests.
Checkpoint C: genuine LEARN EVENT/END witnessed proposals and root evidence.
Checkpoint D: complete graph/state serialization and crash/recovery.
Checkpoint E: from-zero empirical LOC/ASSOC learned links and causal read-only persistence verification.
Checkpoint F: full forensic review report and CI.

Exact final validation commands:
- python -m pytest -q --basetemp=.pytest-tmp -rs
- python -m ruff check .
- python -m ruff format --check .
- python -m mypy
- python -m dgca_next verify-specs
- python -m pip check
- git diff --check
- git status --porcelain
- GitHub Actions final branch-head Windows and Ubuntu successful jobs; check final delivery SHA exactly, not an earlier run.

Create docs/implementation/I3-S01-S02-REMEDIATION-VERIFICATION-REPORT.md (or consolidated updated I3-VERIFICATION-REPORT.md), with changed paths, increment commits, exact test outputs/counts and CI URLs, scientific source SHA-256/blob IDs, actual physical source/target cell IDs, event/root order, genuine D/event-close validation, exact q/y/E/S/count and Q logs, H_BEGIN/ABORT bytes, crash witnesses, sampled memory/time, before/after read-only causal traces, current known limitations, and all I3-G01–G08 dispositions. Do not put a self-referential commit SHA inside its own report.

**Hard governance:** Remain on feature/i3-local-learning. Never merge to main, force push, alter independent numerical laws, claim native Assembly formation/owner inference/generation, or start I4. Stop at I3 REVIEW READY only with all mandatory gates evidenced; otherwise I3 PARTIAL / SPEC_BLOCKED / EMPIRICAL_BLOCKED with truthful exact blockers. The owner authorizes future merge after independent review.
