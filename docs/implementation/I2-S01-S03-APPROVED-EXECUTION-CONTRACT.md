# DGCA NEXT — I2 S01–S03 APPROVED REMEDIATION CONTRACT

**ID:** I2-S01-S03-APPROVED-EXECUTION-CONTRACT
**Revision:** R01 · 2026-10-27
**Status:** AUTHORIZED FOR IMPLEMENTATION ON I2 BRANCH; NOT YET VERIFIED
**Repository:** naoufelbvb2-arch/DGCA-NEXT-V1
**Branch:** feature/i2-neural-dynamics
**Reviewed implementation baseline:** eabc2b79beec8f97e9d3380a3bd4fa58d6c571fe
**Approved decision record:** docs/implementation/I2-S01-S03-RESOLUTION-PROPOSAL.md
**Historical scientific baseline:** docs/specs/DGCA_CORE_RC4_2.md and DGCA_LLA_RC4_2.md — NOT FROZEN / NOT EMPIRICALLY VERIFIED.

## 1. Mission and non-negotiable scientific boundaries

The owner approved **exactly three** targeted scientific choices (S01, S02, S03). Resolve the I2 blockers without changing the unrelated scientific rules or implementing later milestones. The approval licenses a versioned, audited **Core/LLA RC4.2 → RC4.3** source migration and corresponding code/tests on the existing feature branch.

**Only two normative scientific specifications**, Core and LLA, may exist in the current working tree. Preserve original RC4.2 content byte-for-byte in Git history and archival provenance. Mark RC4.3 as DESIGN CANDIDATE / NOT FROZEN / NOT EMPIRICALLY VERIFIED.

Do not enable LEARN root execution, external q/E/S updates, production novelty/recycling, autonomous Assembly birth, actual context-owner recruitment, generation or a language model claim. LLA-T01–T41 and LG-T01–T16 remain NOT_RUN. Do not weaken earlier 421 tests or silently tune thresholds.

## 2. Normative change S01 — live neural propagation

### Decision

The scientific **live** synapse states CANDIDATE, EPISODIC_INDEXED, CONSOLIDATED are all eligible for neural LOCAL/CROSS same-event propagation when and only when their structural scope, commitment, latent D, direction and frozen pass-1 E^(1) membership are valid. Same-event neural source activity is exactly A_i^(1)(t).

p_ij^S = A_i^(1)(t) * Q_ij; Q_ij = d*S*(E_ext+E_int)/E_max.

No further factor k_evidence, no mandatory consolidation state for neural propagation, and no propagation from absent/rejected/staged LINK_PROPOSAL (not yet materialized). Temporal ASSOCIATIVE Δ=1 retains prior F_step and frozen prior A^+ exactly.

A fixture candidate with S=.60, E_ext=1, E_int=0, E_max=10 has Q=.06. With source A^(1)=.80 its target contribution is **.048**, before Noisy-OR. Quality is calculated using I1's existing lawful record. A link with quality zero contributes zero.

**Assembly formation remains CONSOLIDATED-reciprocal LOCAL only; S01 must not relax that gate.** Any owner or LLA learning gate remains unchanged.

### Implementation

- Update I2 synchronous_drives / its helpers to accept all lawful LIVE states, not arbitrary construction shortcuts. Preserve deterministic contribution ordering, I1 GraphSnapshot immutability and fail-closed invalid structural keys.
- Remove or revise the overly restrictive "consolidated pass-2 Q" clause in the historical I2 execution contract by explicit dated supersession note (do not erase its historic wording/evidence). Integrate the scientific live-state clarification into Core §1.4/§5 and a confirming note in LLA §4.1 with no independent formula replacement.
- Add tests for CANDIDATE, EPISODIC_INDEXED, CONSOLIDATED on LOCAL and CROSS; forbidden/absent/no-E sources yield zero; proposed-but-not-live gives zero; Assembly eligibility still rejects nonconsolidated reciprocity; temporal association unchanged.
- If an I1 graph fixture cannot legally create a nonconsolidated state without missing evidence/root history, use the existing documented I1 fixture builder **within its actual invariants**; never weaken graph validation to force a test.

## 3. Normative change S02 — fresh weighted reciprocal Attractor cohesion

### Decision

For an existing live, qualified LANGUAGE Assembly G at the **start** of event t, freeze its exact Assembly ID/generation and pre-event W and select only unordered pairs i<j inside G whose reciprocally CONSOLIDATED LOCAL links produce R_B(i,j)>=theta_A=.10, using Core §2.0 unchanged:

R_B(i,j)=min(Q_LOCAL_ij, Q_LOCAL_ji) for first-lab LANGUAGE.

Let E_G be these qualifying unordered pairs. Let f_i(t) be Core §2.1's actual post-second-pass FRESH activity, computed separately from normal R with A_prev=0, P_T=0, sigma=0, bootstrap=0 and one LOCAL/CROSS synchronous completion.

Cohesion_G(t) = sum_over_pairs_EG( R_B(i,j) * min(f_i(t), f_j(t)) )
                 / sum_over_pairs_EG( R_B(i,j) ).

If E_G empty or denominator is zero: no legal admission; return an explicit invalid-structure diagnostic (not cohesion=1, division by zero or a guessed denominator). Accumulate over pair IDs in ascending lexicographic order using finite binary64. The producer must require a valid current physical Assembly/generation; no caller-supplied number may masquerade as calculated cohesion in the production path.

An INACTIVE Attractor becomes ACTIVE only if **both** M_G^fresh>=theta_in=.40 and Cohesion_G>=theta_ctx_form=.50 in the same event, with all structural/causal gates. A previously active Attractor retains the existing age/decay/external-error/collapse rules (cohesion is an admission gate, not a new undocumented collapse gate). Fresh from no valid direct input is identically zero. New C_G(t) affects sigma(t+1), never current-event input.

The cohesion law does not create links, strengthen evidence, alter Assembly construction, or make a fixture Assembly "learned."

### Required independent numerical examples

- Equal-weight legal 3-node triangle, fresh=(1,1,0): M=2/3, cohesion=1/3, **reject** Attractor admission.
- Equal-weight legal triangle, fresh=(.5,.5,.5): M=.5, cohesion=.5, **allow** admission.
- Unequal edge weights: compute a second independent hand-derived golden quotient, compare binary64 within declared precision; ensure directed pair is counted ONCE only.
- Nonconsolidated or one-sided edges may propagate via S01 but **cannot** enter E_G; zero X implies zero cohesion; a stale Assembly/generation is not a legal provider; error remains unchanged without genuine comparable external target.

### Implementation

Define pure cohesion_from_graph_and_fresh(snapshot, assembly, fresh) or equivalent and wire into the existing Attractor admission path; fixture-only scalar argument may remain solely in explicitly labeled tests, never as production admission authority. Do not run I4 FORM or use raw word labels to select G.

## 4. Normative change S03 — regional firing denominator and timing

### Decision

For each genuine ordered LEARN EVENT t, after its **real EVENT execution/checkpoint** within an OPEN exposure and under its BEGIN/ABORT rollback protocol (implementation of that transaction is I3), define the frozen population

K_r(t) = all physical cells in region r COMMITTED BEFORE event t began.

With pre-event theta_active^r and final real pass-2 A_i^+(t), define

rho_r(t) = count{i in K_r(t) : A_i^+(t)>=theta_active^r_pre} / |K_r(t)|

for nonempty K_r. This is the activity/firing fraction over previously committed cells, **not** F_step, 4096 logical addresses, newly admitted event cells, SIC receiver count, or Homeostasis.gains entries. Residual/predicted activity genuinely above threshold counts in firing; it still cannot become a fresh F_step witness without new observed source.

If K_r empty: do not update that region's rho_bar, theta_active or regional H entries on that event (not rho=0). No region is updated absent a genuine authorized activity region and known official theta. The first lab is LANGUAGE only; never invent VISION/AUDIO initial theta.

Keep the existing Core §5 EMA/threshold equations unchanged:
rho_bar'_r=(1-beta_H)*rho_bar_r+beta_H*rho_r(t).
theta'_r=clip(theta_r + eta_H*1[abs(rho_bar'_r-rho_target_r)>epsilon_dead]*sign(rho_bar'_r-rho_target_r),theta_min,theta_max).

For LANGUAGE beta_H=.05, eta_H=.005, epsilon_dead=.002, theta_active=.20, rho_target=.030. Example two previously committed cells with A+=(1,0): rho=.5, prior rho_bar=.03, updated rho_bar=.0535 and theta_active approximately .205. The all-4096 denominator is explicitly NOT chosen.

- Freeze membership, theta and A snapshot at event-time; sort physical IDs for reproducible accounting.
- I2 should implement a *pure graph-verified rho producer* using frozen committed-before-event identifiers and supplied final activity. If population proof is absent or fabricated, reject.
- I2 tests pure adaptation and correct producer; actual W/H durable mutation, checkpoint, ABORT restoration, completed-root dedupe and production LEARN event execution remain I3 obligations.
- No homeostasis update in READ_ONLY, FULL, CONTROL, REPLAY or GENERATE.

### Additional tests

Two committed cells versus 4096 counterexample, correct beta_H/eta_H, dormant committed cells counted in denominator, event-newborn excluded, pure predicted/residual A counts for firing but not F_step, zero committed population skips ONLY that region, other regions unchanged, read-only H identity, cross-platform deterministic reporting and invalid provenance rejection.

## 5. Scientific source migration: atomic RC4.3

1. Start from verified I2 branch, never rebase or alter main. Snapshot and record original RC4.2 files/hashes/blob IDs as historical evidence.
2. Prepare BOTH complete new scientific documents, named docs/specs/DGCA_CORE_RC4_3.md and docs/specs/DGCA_LLA_RC4_3.md; update internal revision/status and mutual companion references. Migrate/rename both sources within **one Git commit**, removing the RC4.2 current-path copies so the working tree contains exactly TWO current science specs. Original bytes remain recoverable at the pinned parent SHA.
3. Core owns explicit live neural states, cohesion equation, regional population & timing. LLA owns its original evidence law unchanged and only a consistency confirmation for Q/live-state versus consolidation and witnessed/slow adaptation provenance. All other RC4.2 laws, numbers, L01, owner, μ_ij and SIC must be preserved.
4. Update docs/specs/SOURCE-MANIFEST.md, src/dgca_next/integrity.py, config source origin strings, pinned schema fingerprint fixtures, tests/test_spec_integrity.py, README and any version-dependent tests **together**. Pin SHA-256 and Git blob SHA of new bytes; keep the previous RC4.2 pins as immutable archival history. Do not rename away an old spec without updating all paths and tests.
5. Historical I0/I1 provenance tests must use immutable archived SHA, never assume main always holds the old paths. Baseline config parameter values unchanged unless explicitly authorized (none newly introduced).
6. Commit atomic science migration before the code remediation, then verify all unchanged-law regression assertions (document any legitimate section-limited diffs). Preserve auditability. Do not claim a new hash is validated without checking raw bytes.

## 6. Targeted implementation sequence

- **R06-A — scientific migration:** exact Core/LLA RC4.3, pinned integrity/fixtures and no stale third authority.
- **R06-B — S01 implementation:** all live synchronous links propagate by quality. Remove the S01 SpecBlocked path and test exact independent .048 fixture and full legal states.
- **R06-C — S02 implementation:** fresh-weighted cohesion computed from frozen actual legal Assembly; remove S02 SpecBlocked path only for valid scenarios and test sparse/invalid cases.
- **R06-D — S03 implementation:** frozen pre-event committed-population rho, preserve slow adaptation pure functions, disallow caller-asserted rho as real authority.
- **R06-E — full verification:** all original 547 tests (adapt intentional historical-version assertions), new tests, strict tooling, integrity, final-head cross-platform CI and forensic report.

Do not weaken any test to force success. Previously passing S01/S02/S03 fail-closed guard tests must be **replaced with actual successful-operation tests** plus invalid-input rejection, not left artificially passing against an obsolete blocker.

## 7. Required verification and evidence

Run and capture exact output:

- python -m pytest -q --basetemp=.pytest-tmp -rs (full I0/I1/I2 regression)
- python -m ruff check .
- python -m ruff format --check .
- python -m mypy
- python -m dgca_next verify-specs
- python -m pip check
- git diff --check; git status --porcelain
- GitHub Actions validation on Ubuntu and Windows at **the final delivery head commit**, not merely an earlier implementation commit.

Explicitly execute new **I2-R06-S01** (states/scopes/no fake consolidation), **I2-R06-S02** (reciprocal pair weighting/fresh/threshold/absence), **I2-R06-S03** (pre-event population, denominator and slow update boundary) suites. Include independent numerical golden vectors, no guessed tolerances, and test that metadata/graph W, H and caller R do not change in read-only modes.

Record report at docs/implementation/I2-S01-S03-REMEDIATION-VERIFICATION-REPORT.md: exact changed file list and increment commits, old/current spec hashes, full command outputs/count, CI run IDs, before/after numerical trace for three previously blocked cases, acceptance disposition I2-G01–I2-G08, and remaining NOT_RUN I3/generation/actual root tests. Do not put a self-referential final report commit SHA in the report; reference it from final delivery message.

## 8. Hard stop conditions

- Any rule needed beyond approved S01–S03 that is absent/contradictory ⇒ report remaining SPEC_BLOCKED; never guess.
- No production LEARN or evidence creation, no training examples as semantic labels, no Assembly FORM, no real owners, no text generation, no production recycling enablement.
- Previously passed SIC, FP-ROLE, contextual target routing, root boundaries and accepted physical graph invariants must remain unchanged and tested.
- **Main stays unchanged; do not merge.** Work exclusively on feature/i2-neural-dynamics. Finish at I2-R06 REVIEW READY only when all three formerly blocked operations really execute and tests/CI pass; otherwise I2 PARTIAL / SPEC_BLOCKED. Never start I3 without independent review.
