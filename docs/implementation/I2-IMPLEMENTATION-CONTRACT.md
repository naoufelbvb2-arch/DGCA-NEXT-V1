> **2026-10-27 approved supersession:** RC4.3 and
> `I2-S01-S03-APPROVED-EXECUTION-CONTRACT.md` resolve S01–S03. In §3 below,
> the historical phrase requiring consolidated Q in pass 2 is superseded by
> propagation through every structurally legal live link using actual Q; the
> separate consolidated reciprocal Assembly requirement remains. Historical
> RC4.2 source references and original wording below are retained for audit.

# DGCA NEXT — I2 Neural Dynamics Implementation Contract

**ID:** I2-IMPLEMENTATION-CONTRACT · **Revision:** R01 (2026-10-27)
**Status:** AUTHORIZED FOR I2 IMPLEMENTATION — NOT SCIENTIFICALLY FROZEN
**Branch:** feature/i2-neural-dynamics
**Accepted I1 base:** 0b05311fe82dc2e8961bcca226f8d795b3484524
**Scientific authority:** EXACTLY docs/specs/DGCA_CORE_RC4_2.md and docs/specs/DGCA_LLA_RC4_2.md (design candidates, NOT FROZEN / NOT EMPIRICALLY VERIFIED).

## 0. Goal, scope and source rules

Implement a deterministic, sparse, CPU reference neural event computation on the existing I1 physical graph. Given frozen W/H/R and a mechanically encoded input event, I2 computes SIC receivers, two-pass activation, typed causal contribution lanes, real event frontiers, temporal drives and bounded scratch read-only processing. It must explain each active cell's numeric support.

**NO I3 learning/evidence/proposal/root transaction; NO I4 Assembly formation; NO I5 real owner recruitment; NO I6 verified learned hierarchy; NO I7 language generation.** Fixture-driven dynamics are contract verification, not learned intelligence. Read Core §§1.1–1.4, 2.1, 3–6.1, 8–9.2, 11–13 and LLA §§2–4.1 for neuro/evidence separation. Preserve I0/I1 API, configurations and 421 regression tests. Any material ambiguity must be reported SPEC_BLOCKED, never resolved via invented constants.

## 1. Suggested package modules

- src/dgca_next/peripheral/sic.py — exact SIC-V1 projection (no tokenizer or raw-surface interpretation).
- src/dgca_next/peripheral/fingerprint.py — role/owner physical fingerprints.
- src/dgca_next/dynamics/numeric.py — binary64 clip, stable Noisy-OR, exact rational Q6.
- src/dgca_next/dynamics/state.py — isolated R, immutable snapshots, R_cold.
- src/dgca_next/dynamics/drive.py — P_T and P_S from real I1 directed links.
- src/dgca_next/dynamics/activation.py — normalizer, two-pass computation.
- src/dgca_next/dynamics/frontier.py — E_pass1, L, L_cross, fresh F_step.
- src/dgca_next/dynamics/provenance.py — per-contribution physical lanes and event sources.
- src/dgca_next/dynamics/context_gate.py — fail-closed numerical gate on explicit legal fixture descriptors.
- src/dgca_next/dynamics/routing.py — post-event source mask and target-directed mu_ij.
- src/dgca_next/dynamics/attractor.py — optional pure fresh/Attractor calculations on legal *synthetic* Assembly fixtures.
- src/dgca_next/dynamics/homeostasis.py — pure H_slow formulas, no durable writes.
- src/dgca_next/dynamics/session.py — READ_ONLY_EPISODE, PredScore and FULL/CONTROL scratch.
- tests/test_sic_v1.py, test_sic_fingerprints.py, test_dynamics_numeric.py, test_dynamics_two_pass.py, test_dynamics_frontier.py, test_dynamics_context.py, test_dynamics_routing.py, test_dynamics_sessions.py, test_dynamics_attractor.py, test_dynamics_immutability.py.
- docs/implementation/I2-VERIFICATION-REPORT.md — only after execution.

File consolidation is fine when responsibilities and tests are obvious. Never create dense NxN weights or a second incompatible Cell/Graph schema.

## 2. SIC-V1: exact mechanical encoding (Core §3.1)

- Callers supply feature_text and decimal support **strings**, not raw word labels or a tokenizer. Normalize each feature to NFC, strict UTF-8, length 1..4096 bytes. Reject surrogates/invalid UTF-8.
- Input numbers support and salience match Core's grammar exactly: 0, 1, 0.fraction(1–6 digits), 1.000..; reject floats, exponents, signs, nonfinite or negative zero.
- Canonicalize duplicate normalized features, compute exact decimal Noisy-OR and half-even quantize ONCE to integer millionths; multiply by salience and quantize once. Sort features by raw unsigned UTF-8 bytes. Each feature uses four precise SHA-256 salt payloads, k=0..3, distinct cell IDs per feature, region bytes VISION 00/AUDIO 01/LANGUAGE 02, index from first 8 digest bytes unsigned big-endian mod 4096. Across different features colliding at receiver, decimal Noisy-OR and one final half-even integer rounding. Preserve X_fixed and binary64 X separately.
- Golden LANGUAGE vectors from Core: feature a indices [1153,3989,414,3603], ab [3449,2321,502,2081], é [1138,1220,3626,1003], f617 [414,8,1843,2734]. a:.5 + f617:.25 yields global receiver 8606 at 625000. Repeated NFC a:.5 + a:.25 yields 625000 on all four receivers. A-only observed global IDs [8606,9345,11795,12181].
- Implement FP-ROLE-V1 and owner-profile fingerprints as byte-exact Core §3.1. P footprint a:.5 digest MUST be 6cce77c3fc8da8bed4973ec695b267c3430807001563606989f40a3fe383b337. Exposure/root IDs do not enter stable physical fingerprints.
- Uncommitted receiver may have direct X but must not be automatically committed or assigned active A or eligible frontier by I2; note it for future I3 sensory admission. No word/semantic labels in Core.

## 3. Numerical dynamics (Core §§1.4 and 5)

For every step use frozen pre-event W, H_slow, R (no mutation of caller inputs). Numerical law is finite IEEE-754 binary64, stable contributors sorted by (source_cell_id, scope_order, link_key), no extra time factor in neural propagation.

Prior event F_step and prior A_i^+ feed ONLY Δ=1 ASSOCIATIVE links for P_T; neural k=1.0. Do NOT apply k_evidence_ASSOCIATIVE=0.7408182206817179 to P_T. Example A=.8, Q=.3 → P_T=.24. Source-routing mu_ij from prior event is frozen.

Pass 1:
P_T=NoisyOR(previous F_step associative qualified drives);
sigma=rho_s * maximum previous qualified C_G for target;
raw1=NoisyOR(X,P_T,sigma);
D1=raw1/(1+beta_r*mean_column(raw1));
A1=clip((1-delta_r)*A_prev+gamma_r*g_j*D1,0,1).

Freeze Pass1 emitter E1 using committed cells with A1 >= theta_emit. Pass 2 uses only E1 synchronous LOCAL/CROSS source activities A1 and legal consolidated Q for P_S. There is ONE synchronous completion step, never a third iteration:
raw2=NoisyOR(X,P_T,P_S,sigma);
D2=raw2/(1+beta_r*mean_column(raw2));
Aplus=clip((1-delta_r)*A_prev+gamma_r*g_j*D2,0,1).

The permanent contextual gate, if a valid fixture-only descriptor is provided, zeros raw drives before computing the column mean AND zeros residual/activity for off-context z on both passes; even coincidental SIC into z cannot bypass it. No probe in READ_ONLY; production probe/phase lifecycle belongs I5.

theta_active initial LANGUAGE=.20, theta_emit=1.15*theta_active, theta_bind=1.20*theta_active; respect prescribed binary64/Q6 rules. I0 intentionally leaves VISION/AUDIO initial thresholds unresolved: do not invent them; LANGUAGE-only execution for threshold-dependent tests.

Persist event-local Aplus and R timelines immutably across steps; zero all R_witness, R_frontier, mu and Attractor components on R_cold without touching W/H. A residual alone cannot generate a new event.

## 4. Physical provenance and correct F_step (Core §§6–6.1; LLA §2)

Maintain separate tagged contributions per cell: DIRECT_OBSERVED, SPATIALLY_COMPLETED, PREDICTED, RESIDUAL, ATTRACTOR, CONTEXT_MATCHED; never overwrite direct source with predicted classification. Internal candidate BOOTSTRAPPED and LEARN probe are future integrations, not synthesized in I2.

Event origin is typed EXTERNAL_DIRECT, READ_ONLY_OBSERVED, INTERNAL_SELECTED, DERIVED_EXTERNAL_CONTEXT, DERIVED_RUNTIME_CONTEXT and is NOT a license to mint evidence. In I2 real LEARN roots and internal generation sessions are not executed.

F_step requires (a) committed before this event, (b) Aplus >= theta_emit, and (c) positive new directly SIC-observed contribution or verified contextual match, never residual-only / predicted-only / spatial-only. Save prior F_step, actual Aplus, support lanes and source mu before next event. HARD_BOUNDARY resets causal eligibility. No implicit V_ext, q, E_ext or root confirmations.

## 5. Contextual gate and directed routing (Core §§5.1–5.2)

Actual contextual owner discovery, immutable owner registry, StableBindingV2/V3 and legal probe integration are I5. I2 may test physical/numerical operators with explicit separately marked, structurally legal ContextBindingFixture descriptors and I1 physical link fixtures; never claim an owner was learned.

Gate on z requires typed prior P0/P1 witnesses (Q6(min(P0,P1)) >= immutable tau_ctx_q6), current actual selected C witness, no HARD_BOUNDARY and legitimate retained/pinned physical keys. Y is never an input to gate. Gate adds ZERO excitation; positive match does not guarantee crossing theta_emit. Stale/illegal descriptor, missing calibrated threshold, missing P/C must yield G=0 and named diagnostic, including for direct X colliding onto z.

Only after two-pass/F_step, qualified unique complete contextual z may mask its physically retained observed AnchorSourceSet on the next step. If owners overlap one anchor, mu_i=0 there and AMBIGUOUS_CONTEXT_OWNER diagnostic, no arbitrary semantic winner. For legal directed associative key i→j, compute mu_ij = mu_i * (1 if j is NOT a legitimate gated contextual target else 0). Thus a masked observed B source still sends to valid depth-2 contextual z2 but not a generic target. Frozen prior mu drives the following P_T; never recompute from future Y.

If I5 full owner machinery is required to evaluate a production case, keep it as fixture-only and report actual ownership integration DEFERRED. No prediction-only source promoted to DIRECT.

## 6. Optional pure fresh Attractor and H_slow (Core §§2.1,5)

Fresh scratch uses actual current X, A_prev=0,P_T=0,sigma=0,bootstrap=0; pass1 and exactly one LOCAL/CROSS step. No external input ⇒ zero fresh. Real Assembly formation is I4; any Attractor test uses a legal artificial Assembly fixture and clearly states that fact.

With such fixtures test C_G=max(rho_s*C_prev,M_fresh), rho_s=.90, theta_in=.40, theta_ctx_form=.50, age cap 30, error cap 1.50, boundary>age>error collapse order and no same-step sigma feedback. Error changes only for externally comparable genuinely witnessed outcomes. No comparator ⇒ unchanged error.

Implement H_slow g/r_bar/region EMA/theta update law as PURE functions exercised with synthetic active events. Durable LEARN H writes and BEGIN/ABORT rollback are I3. READ_ONLY/FULL/CONTROL must not update H.

## 7. Isolated read-only stepping (Core §§9.1–9.2)

READ_ONLY_EPISODE begins R_cold scratch, consumes ordered caller-provided features with READ_ONLY_OBSERVED origin, holds W/H and caller R unchanged. No OPEN exposure, no direct evidence, no sensory commitment. Show complete diagnostic trace X, P_T, P_S, sigma, A1/Aplus, raw/normalized drives, frozen frontiers and typed lanes.

Implement next-step PredScore from frozen B F_step and mu; evaluator-only physical Y footprint must not enter current neural input. Unresolvable labels/footprints ⇒ UNRESOLVED. Implement FULL/CONTROL on separate clones of identical post-B scratch snapshot, X=0: CONTROL zeros ONLY P_T; other residual, sigma, normalization and P_S remain identical. Scratch next step is never a materialized timeline event. Implement gain_j and eligible-neural-next pure calculations; actual Assembly selection/readout/GENERATE belongs I7.

## 8. Execution increments

**I2-R01:** exact SIC projection and FP-ROLE-V1; golden hashes and strict invalid-input tests; full I0/I1 regressions.

**I2-R02:** frozen sparse W/H/R two-pass, numeric, normalization, Pass1 emitter, P_T/P_S, cold R and independent golden calculations; regressions.

**I2-R03:** typed lanes and fresh F_step, physical origin authority, prior-state continuity, HARD_BOUNDARY and isolated read-only multi-event stepping; regressions.

**I2-R04:** physical fixture-only context gate, mu_i and target mu_ij, ambiguous/stale fail closed; pure fresh Attractor, optional H slow functions and FULL/CONTROL; regressions.

**I2-R05:** fault injection, numerical/cross-platform fingerprints, memory/timing, consolidated forensic report and CI; no I3 work.

## 9. Mandatory tests and verdicts

I2-T01 SIC four-salt vectors and region mapping.
I2-T02 NFC equivalence, Unicode/surrogate/byte/length validation.
I2-T03 Decimal grammar, duplicated supports, half-even at each specified stage.
I2-T04 Shared receiver 8606 and feature/salt dedup.
I2-T05 FP-ROLE-V1 digest and physical owner profile ordering.
I2-T06 Uncommitted direct receiver X does not produce implicit commitment or activity.
I2-T07 Malformed input fails atomically and does not change graph.
I2-T08 NoisyOR stable finite bounds, zero/one and fold ordering.
I2-T09 ASSOCIATIVE .8*.3=.24, no evidence decay.
I2-T10 Pass2 LOCAL source only from committed Pass1 E1.
I2-T11 No third iteration or Δ>1 temporal link.
I2-T12 Column normalization uses gated raw drives.
I2-T13 Residual A without new witness does not enter F_step.
I2-T14 Predicted-only/spatial-only do not become direct observation.
I2-T15 Committed observed emitter enters F_step only if Aplus>=theta_emit.
I2-T16 P_T uses prior frozen Aplus and F_step, not recalculated residual.
I2-T17 Cold session resets prior P/context/Attractor/μ.
I2-T18 Multiple causal lanes coexist on one cell without label overwrite.
I2-T19 Missing/forged provenance fails closed.
I2-T20 Off-context z: missing P/C, below tau or stale descriptor ⇒ A1=Aplus=0.
I2-T21 On-context z has legal neural opportunity but no guaranteed firing.
I2-T22 Masked B→ordinary suppressed, B→valid depth-2 contextual z2 preserved.
I2-T23 Ambiguous owners yield μ=0 and named diagnostic.
I2-T24 μ frozen at event t, no future Y lookup.
I2-T25 Fresh scratch with no genuine X is zero.
I2-T26 Attractor decay/error/age/boundary precedence; previous-only sigma.
I2-T27 Pure H_slow exact formula; read-only H unchanged.
I2-T28 FULL vs CONTROL only P_T differs; frozen W/H/R untouched.
I2-T29 PredScore evaluator Y never feeds neural computation.
I2-T30 Read-only feature replay cannot reopen an external LEARN root.
I2-T31 Same-state deterministic traces, cross-platform SIC/role fingerprints.
I2-T32 Injected failure leaves graph, caller R and H unchanged.
I2-T33 All 421 earlier I0/I1 regressions plus exact RC4.2 hashes and CI.
I2-T34 All LLA-T01–T41 and LG-T01–T16 remain NOT_RUN scientific tests, even if pure numeric fixtures exercise overlapping laws.

If legitimate fixture construction cannot fulfill a required physical/structural predicate, do not weaken validators. Mark that test SPEC_BLOCKED and report a minimal reproducer.

## 10. Acceptance and report

**I2-G01** exact SIC and fingerprints.
**I2-G02** genuine two-pass numerical propagation over I1 physical fixture links, correct scopes/Q.
**I2-G03** frontiers/provenance/residual-vs-fresh/cold reset.
**I2-G04** context gate and directed μ on structurally legal fixture contexts, ambiguity fail closed.
**I2-G05** pure H and Attractor contracts without invented assemblies.
**I2-G06** isolated read-only sessions, PredScore and FULL/CONTROL with W/H/caller R unchanged.
**I2-G07** retain 421 I0/I1 baseline tests, raw RC4.2 hashes, pytest, Ruff check+format, mypy, verify-specs, GitHub Actions Windows/Ubuntu on FINAL head.
**I2-G08** honest evidence report distinguishing PASS / FAIL / SKIPPED / NOT_RUN / SPEC_BLOCKED and fixture physics versus empirical learning.

Write docs/implementation/I2-VERIFICATION-REPORT.md: starting base/commits; exact modified paths; run commands and raw totals; trace samples using physical IDs and supports; CI links; memory/timing; limitations; gate verdicts. Do not embed self-referential final commit SHA in the report. Produce NO artificial training results.

**Preserve main.** Work only on feature/i2-neural-dynamics; no force push, merge, science revision, threshold tuning, external service, GPU, LLM oracle or real language output. I1's production automatic recycling remains DISABLED until real VerifiedLocalNovelty integrated in I2/I3 with externally witnessed X_ext and pre-input P_T. If a normative ambiguity blocks a mandatory gate, finish independent lawful work and report I2 PARTIAL / SPEC_BLOCKED. Otherwise commit and push and stop at I2 REVIEW READY. Do not begin I3 without review.
