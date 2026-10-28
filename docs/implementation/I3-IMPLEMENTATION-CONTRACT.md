# DGCA NEXT — I3 Local Learning Algorithm Implementation Contract

**ID:** I3-IMPLEMENTATION-CONTRACT  
**Revision:** I3-R01 (2026-10-28)  
**Status:** AUTHORIZED FOR I3 ENGINEERING IMPLEMENTATION — NOT SCIENTIFICALLY FROZEN  
**Repository:** naoufelbvb2-arch/DGCA-NEXT-V1  
**Working branch:** feature/i3-local-learning  
**Accepted base:** f63935c143b3fa1ef016078a58309f648a51bd22 (merged I2, PR #3)  
**Only scientific normative sources:** docs/specs/DGCA_CORE_RC4_3.md and docs/specs/DGCA_LLA_RC4_3.md. Both remain DESIGN CANDIDATES / NOT FROZEN / NOT EMPIRICALLY VERIFIED.

## 0. Scientific objective, claims and stop conditions

I3 is the first implementation of **genuine external-exposure LOCAL learning** over the physical I1 graph and numeric I2 two-pass kernel. A legitimate caller supplies actual external SIC feature events to a controlled OPEN LEARN root; the engine generates its own observation/provenance records, witnesses and proposals, and publishes bounded synaptic evidence only after atomic END. Merely providing mode=LEARN, an arbitrary scalar, fixture source, replay or synthetic activity is **not** proof.

Success must distinguish three layers of evidence: (1) laws/transactions execute on controlled constructed fixtures, (2) ordinary independently supplied external-feature events, beginning from no learned target synapses, actually cause lawfully learned LOCAL and ASSOCIATIVE links, and (3) full context-dependent AB→C / DB→E, owner specialization, native Assemblies and language are **separate later scientific gates**, not automatically established by (2). No semantic IDs or expected outputs enter a Cell, Synapse selection, root proof, rank or local learning update.

**Preserve all 578 previously passing I0/I1/I2 tests** (the historical baseline at I2). Do not modify RC4.3, configuration constants, SIC salts or source integrity pins. A missing scientific operator must fail closed with SPEC_BLOCKED and a minimal reproducer; do not tune thresholds to force positive learning.

## 1. Existing code integration preflight — mandatory I3-R00

Before writing the learner, inspect the actual constraints in:
- src/dgca_next/graph/network.py, _Editor and FixtureBuilder
- src/dgca_next/graph/synapse.py and audit.py
- src/dgca_next/graph/policy.py and recycling.py
- src/dgca_next/dynamics/activation.py, state.py, frontier.py, session.py, homeostasis.py
- src/dgca_next/peripheral/sic.py; src/dgca_next/contracts.py
- Current tests and I0–I2 verification reports.

**Known production blocker:** I1's Synapse schema presently requires fixture_only=True, and _Editor/FixtureBuilder are explicitly fixture-oriented. I3 MUST implement a properly audited **production-origin LEARNED synapse/state mutation path**; it must not store actual learned links as fixture_only=True or call FixtureBuilder from a production LEARN engine. Retain the old fixture API and all its deterministic tests. Introduce an explicit trusted internal graph transaction/update interface, gated by validated root-close capability, that can atomically publish learnt material while preserving all I1 graph invariants and immutable external snapshots. Reject synthetic/fixture records as independent external evidence. Retain normal public read-only views.

Clearly document the provenance model and trust boundary. The engine can validate a real API caller's canonical external event within a root; it cannot magically verify the real-world truth of caller-supplied content. Do not confuse authenticated event ingress with semantic ground truth or independent human certification.

## 2. Suggested package architecture, not a request for empty modules

src/dgca_next/learning/observation.py — canonical external observation and provenance.  
src/dgca_next/learning/witness.py — externally witnessed scope/time eligibility, external V_ext.  
src/dgca_next/learning/eligibility.py — bounded H_context=5 timed entries, fresh F_step provenance.  
src/dgca_next/learning/proposal.py — ordered physical link proposals and arbitration.  
src/dgca_next/learning/evidence.py — root-maximum q/y, dual ledgers and strength update.  
src/dgca_next/learning/consolidation.py — independent completed-root count and lifecycle.  
src/dgca_next/learning/novelty.py — verified event-bound local residual-novelty producer, disabled production recycling integration unless separately gated.  
src/dgca_next/runtime/exposure.py — begin/event/end/abort controller.  
src/dgca_next/runtime/learn_step.py — LEARN two-pass using I2 pure kernel, NOT I2 READ_ONLY authority.  
src/dgca_next/runtime/close.py — canonical root-close shadow and publication.  
src/dgca_next/graph/learned.py — internal-only root-authorized physical graph mutation; no fixture leakage.  
src/dgca_next/persistence/store.py — local durable transactional store.  
src/dgca_next/persistence/codec.py — deterministic versioned serialization and verified restore.  
src/dgca_next/persistence/journal.py — root/event checkpoints, commit high watermarks and crash recovery.  
tests/test_i3_*.py and tests/experiments/test_i3_cold_learning.py.  
docs/implementation/I3-VERIFICATION-REPORT.md.

Names are suggestions; combine related units when clearer, without a second incompatible Graph/Cell schema. No dense NxN adjacency, LLM, GPU, service or desktop UI. SQLite through Python standard library is the **suggested** durable local store, with one authoritative atomic database transaction per published root state transition. The store choice is an engineering decision, not a new neural law; if another store is chosen, justify equal crash-consistency guarantees. Canonical codec must retain binary64 and fixed-millionth numeric fidelity, physical IDs and scope order. Never rely on unversioned Python pickle to define long-lived scientific state.

## 3. External BEGIN / EVENT / END / ABORT lifecycle — Core §§10–11; LLA §7

BEGIN_EXPOSURE(exposure_id): strictly monotonically new nonrecycled ID, exclusive root lock, mode LEARN, origin EXTERNAL, authoritative R_cold reset BEFORE event 0; persist OPEN, next_order=0, canonical configuration/spec/code identifiers and full immutable H_slow_BEGIN **in the same atomic BEGIN commit**. No root interleaving; no read-only/replay concurrently within OPEN. Repeated OPEN retry must not reset state again.

EVENT(order, features, salience, boundary): only inside OPEN, next contiguous order, valid canonical SIC from supplied external features, typed immutable ObservationWitness (exposure_id,event_order,feature_digest, direct X_fixed, salts/config, scope/status). Snapshot W/H/R and committed-before-event **before** any admissions. Compute I2 numeric two-pass and trace using EXTERNAL_DIRECT authority, never recycle read-only observation as genuine. Stage legal eligible source/time pairs, proposal records, frozen A^(1), final A^+, E_pass1, F_step, pre-current-SIC temporal P_T, H_context/boundary, q/y and true root evidence eligibility; record contextual/collision diagnostics. Admit at most K_R=12 new cells per EVENT, nominal 8 sensory and 4 contextual transferable, using lawful sensory receiver X>eps_p and existing L01 simultaneous cohort selector. Sensory birth/latent/reverse indexes/wiring commit **only at EVENT close**, no same-event evidence from newborns, no fabricated K_new activity; independent later events must provide the confirmation. Same-event source q use final activity only with frozen pass1 emitter gate. After event, adapt H using frozen committed-before-event population (RC4.3 S03) and store H_slow_EVENT checkpoint; adaptations are provisional until END. Publish EVENT checkpoint, permitted sensory W admissions, journal/order and current H together atomically. Invalid EVENT must leave state exactly at last checkpoint.

END_EXPOSURE: freeze pre-close W and pending event journal. Reduce eligible (link_key,exposure_id) to one max q with **its paired y** (ties earliest event_order then proposal_ordinal); validate both D_event and D_close, valid scope, source/target committed-before-relevant-event, capacity, initial coactivity, preserved witness and event order. Canonical order of proposals: (priority_class, -coactivity, -q, source_cell_id, target_cell_id, scope_order) with contextual reserved priority when applicable. Use one shared shadow budget/reservation ledger; an identical reserved/live key is charged once. FIRST CREATION only at accepted END; no link/evidence from a pending proposal alone. Update W/S/E/count, root journal and COMPLETED marker, then any actually implemented later-milestone operations *only if their milestones have separately been authorized*; do not silently create owner, z, Assembly or peripheral attestation during I3. END consumes no new event/K_R allowance. If an incompletely integrated later Core §10.2 step would block atomic END, explicitly defer that **later-milestone mechanism** with a recorded status; never fake its result. The I3 legal ordinary-root close must remain atomic.

ABORT_EXPOSURE: atomic status ABORTED and R_cold reset, drop staged proposal/phase/contrast changes, no q/S/E or external root confirmations, restore H_slow_BEGIN **byte/exact binary64 fields**; keep only already legally committed sensory W structures if authorized. A failed ABORT must leave root OPEN with last checkpoint and retry restore exactly once. Duplicate ABORT is status-only, cannot overwrite subsequent H.

Restore/retry: crash before BEGIN => no OPEN. Crash during EVENT => prior complete event checkpoint or new complete checkpoint. Crash during END => entire pre-close or entire post-close, never partial. Restoring OPEN must not recapture BEGIN, repeat a committed EVENT, duplicate root evidence, skip event index or reuse root IDs. Persist verified high watermark COMPLETED/ABORTED and never silently synthesize a completed exposure. SQLite BEGIN/COMMIT boundary or equivalent must include all logically published W/H/R and journal pointers in that transaction. Test process-crash injection, not only Python exception rollback.

## 4. Genuine observation, witness, time and link creation — LLA §§2,3,5

A valid direct OBS_DIRECT requires direct SIC X_ext>0 from a canonical external OPEN event, regardless of whether receiver was uncommitted. OBS_ELIGIBLE further requires committed BEFORE the event. Predicted-only, SPATIALLY_COMPLETED-only, residual, Attractor, READ_ONLY_OBSERVED, internally selected, replay and synthetic fixture provenance NEVER become external evidence.

Both source and target must be eligible in proper event(s):
- LOCAL Δ=0: same event, region same, valid V_ext and final A_target>=theta_active; source must have been emitted in frozen Pass1 E_t^(1). Training a link uses **final/final** coactivity, never the Pass1 neural value as q.
- CROSS_TERRITORY Δ=0: same event, different regions, additional cross bind gates; for LANGUAGE-only initial trial the other region's missing theta initialization is NOT guessed. Keep pure legality/proposal guard tests for CROSS; do not fabricate an external multimodal success.
- ASSOCIATIVE Δ=1: previous event F_step source A_i^+(t-1) frozen at that real event and the genuine direct current observed target A_j^+(t), no intervening hard boundary, same OPEN root; NO learned Δ>1 synapses. Up to H_context=5 older history may support later context discovery, not an automatic longer-lag link.

Create_coactivity = A_source_final * A_target_final; for ASSOC A_source_final is the **prior recorded** source activity. LOCAL/ASSOC theta_create=.20, CROSS theta_create_x=.39. This gate is separate from q. Exclude newborns admitted at end of their own event, regardless of strong SIC. D_event and D_close must both hold; root-level dropped/recycled dynamic eligibility means STALE_LATENT_ELIGIBILITY without update. Capture source and target at event time, not at END reactivation. Actual link becomes visible to I2 only after END.

At I3, implement LLA pure witness checks strictly. Full context candidate P/C/Y and DERIVED_EXTERNAL_CONTEXT sources depend on I5/I6: represent typed contracts and fail-closed without fabricating a completed owner. Do not preemptively build context-specific probing or semantic discrimination.

## 5. Local evidence and consolidation — LLA §4

For a valid witnessed proposal with q>0:
q_raw = omega_root * D_event * a_source_learn * A_target^+ * k_evidence(scope).
omega_root=1 for true external LEARN. k_evidence=1 for LOCAL/CROSS, stored binary64 0.7408182206817179 for ASSOCIATIVE. The evidence factor NEVER multiplies P_T, P_S or PredScore. y_positive = clip(theta_S + (1-theta_S)*(A_target^+-theta_active_target)/(1-theta_active_target), theta_S, 1).

Root MAX is max one accepted positive q/key/root with that proposal's paired y. Root q=.20 and .50 should contribute .50 and one root count, not .70. No negative updates in any scope, even when a predicted outcome was absent.

First accepted link: state CANDIDATE, S=y, E_ext=min(10,q), E_int=0, external_count=1, no retroactive events, true root/event provenance and deadline age W_conf=100 completed external closes. Existing accepted link updates:
S_new = (E_old*S_old + q*y)/(E_old+q), with E_old=E_ext+E_int. Then E_ext_new=min(10,E_ext+q), E_int_new=min(phi*10,E_int+q_int,10-E_ext_new), total E<=10. Preserve exact two-ledger order/caps, intern_support flag, root IDs and last evidence clock. No spurious E or count for invalid proposals/ABORT/READ_ONLY. Two independent completed genuine roots necessary but NOT sufficient to consolidate; also S>=.60 and E_total/10>=.30. Fully saturated E remains bounded while later accepted genuine q can update S lawfully. Demotion/pruning/episodic transitions must follow the RC4.3 explicit laws; the baseline Replay is disabled, no fake internal evidence. If a partial episodic algorithm is unsupported in this phase, report it NOT_RUN and keep impossible to invoke; do not invent an eviction scheduler.

**Reference checks:** LOCAL q=.48 at A_src=.8,A_target=.6. ASSOCIATIVE q=.3555927459272246. One link with neural Q=.3 and preceding A=.8 yields P_T=.24. Replay comparator would yield q=.08889818648180615 but REPLAY remains OFF. For a_source=a_target=.5, create product .25 and ASSOC q≈.18520455517; consolidating E>=3 needs at least ceil(3/.18520455517)=17 distinct accepted roots when otherwise eligible. Do not mistake a numerical lower bound for demonstrated physical formation.

## 6. Verified local novelty and recycling integration — LLA §5.1, Core §1.3.5

Implement a trusted, non-fixture **VerifiedLocalNovelty** producer bound to actual root ID, contiguous event order, physical receiver, X_fixed, source witness digest, frozen pre-current-SIC P_T and canonical Q6 numeric comparison. The novelty formula remains exactly RC4.3 inherited L01:
nu(u,t)=max(0,X_ext(u,t)-min(X_ext(u,t),P_T_u(t)))/max(X_ext(u,t),1e-6), else zero.

Reject caller-supplied novelty floats, fixture-only proofs, read-only, predicted-only, replay and mismatched event/witness/root. Validate theta_R=.30 and 100 **COMPLETED external roots** for each affected dynamic slot, bilateral protection including reverse links/candidate states/reservations/pins/fixed slots, deterministic replacement and full reverse index shadow rollback. Ordinary pending proposals have lower priority than protected knowledge.

**Safety rollout:** the production novelty authority and verified guard are mandatory I3 contracts, but **automatic periodic production recycling stays OFF BY DEFAULT** pending a separately reviewed enabled integration test/ablation that proves bounded, auditable event-time replacements and no protected-link deletion. Do not mark full automatic recycling operational merely because a mathematical residual was computed. If formal live-provenance integration cannot be implemented without an uncontracted trust model, report NOVELTY_INTEGRATION_BLOCKED, not a fake root.

## 7. Durability, identity and diagnostic observability

Use a bounded append-only or checkpointed root/event journal storing: event order, canonical witness digest, provenance, source sampled activity, pass1 emitter/frontiers, Δ and scope, q/y proposals, per-root accepted link IDs, H_slow_BEGIN and H_slow_EVENT versions, accepted/aborted root high watermark, logical completed-close serial and original cell birth event. Persist only real graph records in W; do not use synthetic fixture blobs as learning evidence. On load, validate versioned schema, actual two RC4.3 source hashes, config fingerprint, latent policy version, physical IDs, slot inverse indices, directed keys, capacities, Synapse evidence bounds and causal record integrity. Handle mismatched/missing version as hard error, not a silent data migration. Tests must check that a saved learned link has the same Q and causal effect after cold load as before.

A root-scoped read-only diagnostic may expose physical IDs and evaluator comparison summaries, but raw expected output is not a neural training signal. Repeated identical canonical input and prior frozen state must be deterministic. Log per root: SIC aliases, births, D_event/D_close failures, attempted/accepted proposals, q_root_max and paired y, source/target activity and scope, W/H before-after structural/evidence digests, rejected cause, read-only next score, retained memory, completed serial, and recovery origin.

## 8. Implementation increments (each with regressions and report)

**I3-R00 — production graph authority review.** Identify hard-coded fixture-only Synapse/write path and design a safe production provenance schema, transaction boundary and versioned codec; audit with pure tests; **do not weaken I1 fixture invariants**.

**I3-R01 — root controller and persistence skeleton.** BEGIN/CLOSED/OPEN lifecycle, strictly increasing nonreusable IDs, isolated R_cold, SQLite schema/codec, atomic H_BEGIN, no evidence updates. Real event input must remain invalid before R02.

**I3-R02 — genuine EVENT + sensory admissions.** Canonical SIC witness, I2 LEARN two-pass, real F_step and born-at-event-end cohort, latent initialization, H_EVENT pure adaptation staged into durable checkpoints, ordered eligibility journal; abort rollback and crash tests.

**I3-R03 — witnessed proposals and END.** LOCAL/ASSOC positive witness, frozen source/timing, q/y, D_event and D_close, per-root MAX, deterministic budget arbitration, one atomic production candidate creation; no root evidence before END.

**I3-R04 — consolidation and persistence verification.** Bounded S/E_ext/E_int, genuine root_count, two-root+mass threshold, expiration protection, deep save/reload and END/ABORT/crash/retry injection; read-only learned-link Q effect.

**I3-R05 — verified local novelty authority.** Produce genuine event-local X/P_T witness; execute pure production-grade guarded feasibility tests; keep automatic recycling disabled unless its dedicated lawful integration gate passes.

**I3-R06 — cold-start empirical/falsification trial.** Start from empty target links and uncommitted LANGUAGE physical receivers. Use ordinary externally submitted SIC feature events, not FixtureBuilder, seeded links or hidden labels. Require at least one independently audited learned LOCAL link and one independently audited learned one-step ASSOCIATIVE link across legal completed roots, visible after save/load and causally affecting frozen read-only neural P_S/P_T. Repetition test must show root_count and q mass from independent roots. Also attempt the designated A/B/C versus D/B/E curriculum and **report AB/DB next-event outcome without pretending to have I5 contextual owners**; inability to specialize is expected to be scientifically measured, not silently patched.

I3 is **not complete** if R00 production fixture barrier is bypassed or R06's ordinary learned-link empirical gate fails. If real events cannot yield a lawful link, report **I3 PARTIAL / EMPIRICAL_BLOCKED** with full per-step physical trace and denominator; do not synthesize an eligible pair or adjust theta_create/SIC/geometry as a hidden fix.

## 9. Contract tests and scientific scope map

I3-T01: BEGIN immediately cold-resets R but retains W/H; monotonic nonreused roots, exclusive OPEN, duplicate retry.  
I3-T02: invalid origin/order/feature/duplicate EVENT is atomic no-op/reject; status and journal unchanged.  
I3-T03: first uncommitted SIC event permits bounded cohort/24-slot initialized physical births; no same-event q or learned link.  
I3-T04: overlapping/co-birth source ranking is immutable/deterministic and not vocabulary-driven.  
I3-T05: external direct observed vs predicted-only/residual/spatial/replay/read-only provenance classification; counterfeit witness fails.  
I3-T06: same-event LOCAL creation uses final/final, frozen Pass1 E; ASSOC prior frozen F_step and Δ=1; strict HARD_BOUNDARY.  
I3-T07: prior event frozen A and witness survive H_EVENT changes; no END resimulation.  
I3-T08: q numeric goldens .48, .3555927459272246; neural .24 independent; theta_create vs q separate.  
I3-T09: same root two proposals .20/.50 settle .50 with its paired y; exactly one accepted root count.  
I3-T10: first creation only on END; true nonfixture Synapse, lawful D_event AND D_close, same source budget shadow.  
I3-T11: 64/65th source, cross 12/13th, expired D_close, fixed/protected/reserved collision reject without partial changes.  
I3-T12: E/S saturation and dual evidence caps, external_count distinct, two-root necessary + E>=3 + S>=.6; no false consolidated.  
I3-T13: negative missing outcome updates disabled; absence/prediction never credits an expected target.  
I3-T14: ABORT restores H_BEGIN exactly, discards staged q, allows only lawful committed sensory birth, idempotent duplicate abort.  
I3-T15: failed END/ABORT + injected crash/restart produces exactly pre or post atomic state; journal no split-root evidence.  
I3-T16: restore OPEN checkpoint resumes expected event order, never silently re-evaluates already committed event or adaptation.  
I3-T17: save/load learned W/latent/inverse/budget/root journals, Q and cold read-only effect identical; corrupt schema/hash fails.  
I3-T18: READ_ONLY, FULL/CONTROL, REPLAY-disabled do not mutate W/H/root status; read-only never opens training exposure.  
I3-T19: real event-bound novelty residual X/P_T, Q6, theta_R; fake witness not trusted; 100 completed-close guard.  
I3-T20: bilateral protected/one-sided/fixed/reverse/key reservation recycling eligibility; auto production switch remains OFF.  
I3-T21: no Assembly/Owner/Context z fabricated, no semantic labels or expected Y in Cell/graph, no hidden backprop.  
I3-T22: cold empty-link LANGUAGE external training produces at least one lawful new LOCAL link and one ASSOC link or **EMPIRICAL_BLOCKED**, with full evidence roots.  
I3-T23: genuinely learned links survive cold restart, affect later read-only P_S/P_T, no fixture contamination; comparator-only effect isolated.  
I3-T24: repeated independent external roots increase E_ext and accepted root_count, one-root repetition within same root capped; no passive drift.  
I3-T25: initial ABC/DBE observational contrast report distinguishes neural-next score, collision/ambiguity and lack of I5 owners; no claimed context-generation success.  
I3-T26: all I0–I2 578 regressions PASS (adapt version-dependent assertion only if strictly required; no value tuning).  
I3-T27: exact immutable RC4.3 source hash and no config drift; Python 3.14 CI Ubuntu/Windows final head, pytest, Ruff, format, mypy.  
I3-T28: cross-platform persistence/recovery and deterministic golden serialization; high watermark; no counterfeit fixtures in restored production W.

**Named scientific LLA test scope:** target actual integration of LLA-T01–T07, T13–T15, T17, T19, T21, T24, T30 (plus relevant already implemented physical law subsets). LLA-T18/T20 Replay-comparator and T08–T12/T22–T23/T25–T29/T31–T41 needing contextual owner/candidate machinery remain **NOT_RUN for complete scientific scenarios**, even if their physical sub-operators have unit tests. LG-T01–LG-T16 remain NOT_RUN. Do not claim "all 41 LLA tests PASS" by running numeric fixtures or relabeling tests.

## 10. Acceptance gates

- **I3-G01:** Trusted external root ingress, strictly ordered events, cold BEGIN, committed-before-event witnesses and provenance.
- **I3-G02:** Real sensory cohort/latent geometry, no newborn retroactivity, deterministic K_R=12.
- **I3-G03:** Fully witnessed scope-local proposals, frozen sampled activities, D_event/D_close and resource arbitration.
- **I3-G04:** Root MAX q/y, E_ext/S/independent counts, legal consolidation and absolute evidence bounds.
- **I3-G05:** SQLite-equivalent atomic BEGIN/EVENT/END/ABORT and H_BEGIN restore; crash/retry, save/load and root high watermark.
- **I3-G06:** Verified event-local novelty producer, authentic witness/candidate guards; production recycling remains disabled unless separately authorized/tested.
- **I3-G07:** Cold-start **actual external-feature learning** of LOCAL and ASSOCIATIVE links from zero learned links; repetition, persistence and read-only causal effect, no fixture source.
- **I3-G08:** Preserve 578 baseline regressions, integrity, lint/type, CI and honest scientific gate statuses.

G01–G08 must each have PASS, FAIL, NOT_RUN, SPEC_BLOCKED or EMPIRICAL_BLOCKED with exact evidence. Success on fixture-only contracts CANNOT substitute for G07. Any unsolved production root authority/schema/atomicity issue blocks I3 rather than being bypassed.

**REPORT:** docs/implementation/I3-VERIFICATION-REPORT.md should include branch/base/head, all modified paths/commits, raw CI links and exact executed commands, test counts, novel numerical roots/physical cell IDs/directed links, root_max q/y, E/S/count and H logs, live Q read-only before/after, root journaling high-watermark, memory/time, 100-close age audit, crash witnesses, failure counterexamples, explicitly deferred contexts/Assemblies/57 scientific named tests, and all gates. No invented results.

**REPOSITORY POLICY:** Work exclusively on feature/i3-local-learning. No main merge, force push, scientific spec version change or I4–I7 production code. Commit/push incrementally, stop at I3 REVIEW READY only after all mandatory I3 gates actually pass, otherwise I3 PARTIAL with precise reason. Owner approves merge and I4 start only after independent review.
