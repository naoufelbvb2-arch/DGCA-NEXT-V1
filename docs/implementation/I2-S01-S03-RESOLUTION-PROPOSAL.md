# DGCA NEXT — I2 S01/S02/S03 Scientific Resolution Proposal

**ID:** I2-THREE-BLOCKER-RESOLUTION · **Revision:** PROPOSAL-R01 (2026-10-27)
**Status:** **PENDING OWNER APPROVAL — NOT NORMATIVE — NO SCIENTIFIC SPEC OR CODE CHANGE AUTHORIZED BY THIS DOCUMENT ALONE**
**Source branch:** feature/i2-neural-dynamics
**Reviewed I2 commit:** eabc2b79beec8f97e9d3380a3bd4fa58d6c571fe (547 PASS, 0 FAIL, 0 SKIP; three SPEC_BLOCKED)
**Authority:** Core/LLA RC4.2 exactly; if approved, version both scientific specifications together to RC4.3, without overwriting RC4.2 in Git history.

This proposal resolves only observed implementation blockers. It does not authorize neural learning, evidence or generation, and it does not claim empirical intelligence.

## S01 — Are nonconsolidated live synchronous links allowed to propagate?

### Existing authority
Core §1.4 and §5 and LLA §4.1 explicitly define neural quality and propagation for an **existing live link**. Core §2.0 separately restricts **Assembly structural reciprocity** to CONSOLIDATED links. The I2 implementation contract's pass-2 "consolidated Q" wording is stricter than the two scientific sources and created the conflict. A not-yet-materialized proposal is not a live link.

### Recommended resolution: ALLOW all lawful live links

For both synchronous scopes LOCAL Δ0 and CROSS_TERRITORY Δ0, exactly the physical live-record states CANDIDATE, EPISODIC_INDEXED and CONSOLIDATED can contribute neural P_S if committed source belonged to frozen pass-1 E and the physical link is structurally live/legal and has positive quality Q. The propagation law **does not change**:

`p_ij^S(t) = A_i^(1)(t) * Q_ij^scope`; `P_j^S=NoisyOR(sorted legal p_ij^S)`.

Quality `Q=d*S*(E_ext+E_int)/E_max`; no extra k_evidence penalty in propagation. Q=0 yields no contribution. Unmaterialized LINK_PROPOSAL, illegal, stale, missing-D, expired or released keys contribute zero; no unsafe fallback to a fixture record or stale owner descriptor. This policy is independent of evidence law, consolidation criterion, FORM and Assembly status. In particular, allowing a CANDIDATE neural influence **does not** make it eligible for Assembly birth, stable ownership or learner evidence without their own separate gates.

**Example:** genuine live fixture LOCAL candidate with S=.6 E_ext=1 E_int=0 yields Q=.06. If pass-1 source A_i=.8, target receives a positive `.048` synchronous contribution before Noisy-OR, **not** zero. This is physical propagation, not new learning. For CANDIDATE and EPISODIC indexed links, the existing tiny E naturally limits Q.

**Implementation change:** remove the state==CONSOLIDATED condition from I2 `synchronous_drives`; replace it with a legal-live/structural validity requirement already provided by the trusted I1 frozen GraphSnapshot. Amend the overly restrictive I2 implementation contract, not LLA's actual existing mathematical law. A short RC4.3 editorial line may explicitly list all live states to close future ambiguity.

### S01 tests
- CANDIDATE, EPISODIC_INDEXED and CONSOLIDATED live LOCAL/CROSS links each propagate **their own actual Q** from pass-1 emitters.
- Illegal/missing links, proposal-only, uncommitted/absent E emitters contribute zero.
- ASSOCIATIVE temporal propagation retains one-step F_step rule and no k_evidence factor.
- A candidate contributes nothing to structural Assembly e_ij or qualified ownership just by activating.
- Stable sorted fold and repeated full-suite/regression checks.

## S02 — Executable Attractor cohesion at admission

### Existing authority and missing source
Core §2.1 requires `M_G^fresh >= theta_in=.40` AND `cohesion>=theta_ctx_form=.50`, without defining cohesion. Core §2.0 already supplies lawful Assembly structural pair `R_ij^B` and the fresh operator provides `fresh_i(t)`. Simply choosing density, specificity or M_fresh itself as "cohesion" would be an unapproved change.

### Recommended NEW experimental law: weighted reciprocal fresh coactivity

Let G be an **existing live, physically qualified** LANGUAGE Assembly with frozen ID/generation at the start of event t. Define unordered qualifying reciprocal pairs

`E_G={(i,j) | i<j, i,j in G, R_ij^B>=theta_A=.10}`

where first-lab `R_ij^B=min(Q_ij^LOCAL,Q_ji^LOCAL)` from live CONSOLIDATED reciprocal LOCAL links **only** (Core §2.0), with the pre-event frozen W. Let `f_i=fresh_i(t)` be the exact bounded fresh-only post-pass-2 activity from Core §2.1. Define

`Cohesion_G^fresh(t) = [Σ_(i,j in E_G) R_ij^B * min(f_i,f_j)] / [Σ_(i,j in E_G) R_ij^B]`,

folding pairs lexicographically (i,j) with finite binary64. If E_G is empty/denominator<=0, Assembly is structurally invalid: no admission; do not treat it as an active valid assembly. For an otherwise valid Assembly and no genuine fresh observed event, f_i=0 and cohesion=0.

**Admission:** the **same event** may create a new active attractor only if `M_G^fresh>=theta_in=.40` and `Cohesion_G^fresh>=theta_ctx_form=.50`. Cohesion is a pure check on **simultaneous neural participation connected by actual reciprocal structure**; it is NOT an additional neural force, evidence update, coactivity credit or assembly-forming rule. The newly admitted C_G(t) feeds sigma at t+1, not at t. Once active, inherited decay, age, externally comparable error and collapse laws remain unchanged; cohesion is the specified *admission* criterion, not a new undisclosed per-step collapse trigger.

**Why min, not fresh mean?** With a 3-cell equal-weight reciprocal triangle and `fresh=(1,1,0)`, average fresh is 2/3>=.4 but cohesion=(1+0+0)/3=1/3<.5 ⇒ reject partial activation. For `fresh=(.5,.5,.5)`, mean=.5 and cohesion=.5 ⇒ admit. This is a scientific design choice, not a result from the historical sources.

**Timing:** evaluate on one immutable pre-event W Assembly generation and actual present fresh snapshot; reject stale/changed/unauthorized fixture structure. No external outcome labels, previous C_G or sigma may enter the cohesion computation.

### S02 tests
- Equal triangle above numeric examples (.333333... rejected; .5 accepted).
- Weighted unequal legal reciprocal pairs independently hand-calculated and compared at declared binary64 tolerance.
- One nonconsolidated or one-sided link cannot create a qualifying pair even when it propagates under S01.
- No fresh X ⇒ 0 cohesion/zero admission; no "cached activation" counted as fresh.
- Boundary collapse precedence and sigma(t+1) only; identical state and input deterministic.
- Existing legal Assembly fixture, never fake learned FORM.

## S03 — Population and denominator of regional instantaneous firing rate

### Existing authority and missing source
Core §5 defines `rho_bar_r <- (1-beta_H)rho_bar_r+beta_H*rho_r(t)` and the threshold update but does not define `rho_r(t)`. Choosing all 4096 logical addresses would force low regional firing during early sparse commitment and drive theta down because uncommitted cells cannot fire. Using only emitted F_step also confounds firing with newly witnessed events. Neither follows automatically from existing specification.

### Recommended NEW experimental law: committed-before-event population

For a genuine ordered LEARN EVENT t **after its atomic EVENT checkpoint within an OPEN root** (the root need not have ENDed yet; H_slow remains provisional and must restore H_slow_BEGIN on ABORT as Core §10.1 requires), in active region r, let

`K_r(t)={i | region(i)=r AND i was COMMITTED before EVENT t started}`.

Let `theta_r_pre` be frozen before EVENT t and `A_i^+(t)` its actual final pass-2 numeric activity (including real residual, not just new F_step). Define

`rho_r(t) = [Σ_(i in K_r(t)) 1(A_i^+(t)>=theta_r_pre)] / |K_r(t)|` when `|K_r(t)|>0`.

- Denominator is ALL already committed regional cells, **including dormant** cells. This is *regional activation fraction*, NOT F_step density, and is independent of labels, observed word count or current co-birth size.
- Exclude uncommitted and newly committed during t from numerator/denominator; they join K in the next event. Never silently use materialized Python cells as the denominator unless they are *verified identical* to committed-before-event physical IDs.
- When `|K_r(t)|=0`, regional rho and its EMA/threshold update for that region are **NOT APPLIED**. This is an explicit no-denominator rule, not rho=0.
- Only regions participating in the genuine event protocol and with specified authorized theta_active values are updated. First-lab LANGUAGE-only. Do not treat absent VISION/AUDIO activity on a LANGUAGE event as evidence of silence and reduce their thresholds.
- Calculate using frozen pre-event theta and same post-pass-2 A; update rho_bar once per lawful real LEARN EVENT, then theta using the inherited existing formula. Read-only, FULL/CONTROL, internal generation and replay remain H frozen. I3 owns root transactional H_BEGIN/adaptation/ABORT rollback, root deduplication and event-order publication.
- The pure I2 implementation should take a frozen graph-verified set `K_r`; if absent, raise explicit error rather than use Homeostasis.gains length or 4096 as a guess.

**Worked example:** two committed LANGUAGE cells (prior theta_active=.20), final pass-2 activity `(1,0)` ⇒ rho=1/2, not 1/4096. If previous regional EMA `rho_bar=.03`, beta_H=.05, new EMA is `.0535`; `abs(.0535-.03)>.002`, so theta becomes `.205` (binary64 tolerance applies). The all-4096 choice would leave theta unchanged in this one-step example, but is NOT selected.

**Risk/measurement:** for very small committed populations the fraction is noisy and may push theta upward; do not silently add a warm-up threshold, smoothing window, pseudo-counts, or a region-size replacement. Log |K_r|, rho, EMA, theta before/after and the share of uncommitted cells. Analyze that calibration experimentally in I3; any warm-up policy would need a separate versioned scientific decision.

### S03 tests
- 1/2 versus 1/4096 numerical counterexample and known beta_H/eta_H.
- Same A and same frozen theta, different K counts legitimately change rho.
- Newly committed event receivers excluded; uncommitted SIC support never counts as spike.
- Dormant committed cells included in denominator; predicted-only but genuinely active A contributes to firing numerator (but not F_step).
- Zero committed cell region ⇒ no regional H update; unrelated region unchanged.
- No updates during read-only/full/control; transactional H rollback deferred to I3.
- Deterministic ascending physical-ID count, finite/range validated; no caller-provided arbitrary rho masquerading as measured rate.

## Global revision and acceptance if approved

1. Record owner approval and migrate **both** Core and LLA RC4.2 → versioned **RC4.3** simultaneously. Keep EXACTLY TWO authoritative scientific source files in the working tree; archive RC4.2 bytes via Git history and historical hash pins. Add S01 explicit live-state clarification, S02 exact cohesion equation and S03 exact region firing equation/timing to Core; in LLA add a brief physical coupling reference and preserve its source/evidence authority. Do NOT create a third normative spec.
2. Update source manifest and integrity pinning, configuration source labels and affected tests atomically. Do not change RC4.2's independent equations/constants or I1 L01 policy; do not silently change compiled config defaults.
3. Implement S01 nonconsolidated link propagation, S02 actual Attractor cohesion producer and S03 graph-derived rho producer, remove the three fail-closed blockers only after tests exist and are executed.
4. Run all current 547 regressions plus new numerical edge cases, with pytest, Ruff, format, mypy, verify-specs and Ubuntu/Windows final-head CI. Test that older RC4.2 checkout is reproducible and new branch contains exactly two current science files.
5. Keep production LEARN, LLA evidence, genuine novelty authority/recycling, Assembly FORM, contextual owner discovery, generation and all 57 LLA/LG named experiments **NOT_RUN**. Pure operators and legal fixtures may pass without claiming these experiments.
6. Publish I2 remediation report and exact G01–G08 gate verdicts, or remain `I2 PARTIAL / SPEC_BLOCKED` with a minimal counterexample. Never merge to main or start I3 before independent review.

**Present state remains I2 PARTIAL / SPEC_BLOCKED.** This proposal is not scientific approval and must not be implemented as a normative law until the project owner authorizes it.
