# DGCA NEXT — I4-R05 Native Attractor + I4-R06 Consolidated Review

**ID:** I4-R05-R06-AUTONOMOUS-MASTER-CONTRACT  
**Version:** 1.0 / 2026-11-02  
**Status:** OWNER AUTHORIZED FOR BOUNDED EXECUTION — RESULTS UNVERIFIED  
**Source SHA:** `b4549d2f9c38d665f19a87848ae22b4b950c8fac`  
**New branch:** `experiment/i4-r05-r06-autonomous-completion`  
**Repository:** `naoufelbvb2-arch/DGCA-NEXT-V1`  
**Baseline regression:** reported 884 PASS; final-head R04 Windows/Ubuntu run `41506679340` verified.  
**Protected refs:** `main` at `88fc596c178c8a89c24b991e280d7a0ca8c07779` and `feature/i4-native-assemblies-design` at `1af7dab4e82be826380d787e16cfecd8a2224f0f` when the prior review was performed. Verify again before proceeding.

## 0. Mission and its strict limits

Finish **I4-R05 genuine Native Context Attractor** and then **I4-R06 final integrated I4 engineering verification** in ONE bounded autonomous coding assignment. Keep a live change log and make small, reversible checkpoint commits, but deliver only one final consolidated review package. Fix engineering issues without repeated user consultations. A scientific-law conflict, unsafe data-model change or missing genuine evidence is a blocker, not authority to invent a workaround.

This is **NOT** an assignment to build text generation, SurfaceReadoutLedger, contextual owners/z-binds, REPLAY, automatic recycling, an L5 coding layer or a language agent. Genuine R05 admission and dynamics are about transient physical contextual activity and predictive-error accounting; do not claim language understanding, semantic meanings, or productive composition.

Read completely before coding:
1. Owner authorization file `docs/design/I4-R05-R06-OWNER-EXECUTION-AUTHORIZATION.md`.
2. `docs/specs/DGCA_CORE_RC4_4.md` and `docs/specs/DGCA_LLA_RC4_4.md` (full documents, especially Core §§2.0,2.1,3.1,4,5,9.1,9.2,10.1–10.2,11,12.1,13; LLA §§2,4,7,8.2–8.3).
3. R04 owner decisions, approved R04 master contract, final R04 consolidated report and full engineering changelog.
4. R01–R03 accepted reports, R03 Schema5 journal policy, and P00 reachability/cooldown report.
5. Actual source for `dynamics/attractor.py`, `dynamics/session.py`, `dynamics/activation.py`, `dynamics/state.py`, `dynamics/drive.py`, `dynamics/frontier.py`, `dynamics/provenance.py`, `persistence/production_store.py`, R04 native operator codecs/stores, replay and all tests.

Scientific SHA-256 must stay exactly:
- CORE RC4.4: `3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c`.
- LLA RC4.4: `ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0`.

## 1. Preflight, isolation, preservation

1. Verify exact source SHA, current protected refs and R04 matrix CI. Branch **from the exact source SHA**, not the default branch or latest unreviewed experiments. Create `experiment/i4-r05-r06-autonomous-completion` (fail closed if it already exists with unexpected history).
2. Place both approval/contract documents at these exact repository paths and commit them on the new branch before implementation; preserve their bytes. Do not modify prior owner authority or accepted scientific papers.
3. Run accepted 884-test regression and source hash/static checks to establish the actual baseline. If the environment cannot rerun it, explicitly mark BASELINE_UNVERIFIED and do not manufacture results.
4. The current GitHub Action `validate.yml` explicitly lists the previous R04 experiment branch only; make the **minimal branch-trigger change** needed to run BOTH Ubuntu/Windows full suite at each final head. Do not weaken or skip jobs, source hash checks or clean-state checks.
5. Existing fixtures are for mathematics/legacy regressions: `AssemblyFixture` in `dynamics/attractor.py` is `fixture_only=True` and `transition(...)` is not native production authority. Preserve it, but never count a fixture PASS as the actual R05 positive result.
6. Existing root production `event()` currently calls two_pass with no native attractor sigma. Any new LEARN integration must be isolated to an explicit new native experimental execution mode with intact historical replay and accepted old mode semantics.

## 2. R05 scientific invariant — structural authority versus runtime state

Use **genuine native LIVE AssemblyID + exact structural_generation + region + members**, obtained from an authenticated `RootStore` graph at the event-start frozen W. Verify native member inverse, real reciprocal consolidated LOCAL Q, source authority and KEEP eligibility before use. A synthetic `AssemblyFixture`, forged scalar ID, stale generation, archived ID, post-END newly born member set or readout ledger must not authorize R05.

**W**: learned Cells/Synapses/Assemblies, identity/generation/journals/evidence — R05 event activity MUST NOT alter W or add Assembly links or evidence.  
**H_slow**: legitimate LEARN sensory adaptation only; read-only RETRIEVE must leave it unchanged.  
**R**: transient activity, prior activity, temporal frontier, Attractor strength/age/error, frozen identity/generation and provenance/diagnostics. Cold reset, independent root BEGIN and HARD_BOUNDARY must clear active Attractors. R05 may checkpoint the OPEN root's authentic R when using a genuinely enabled LEARN mode; no Attractor state may be persisted as learned W or be carried over to a fresh independent root.

Do not move a fixture state into W, and do not broaden I2 fixture admission as a shortcut. Prefer an explicit native-only typed runtime view/validator, isolated mode and auditable bridge to existing genuine learned W.

## 3. R05 exact fresh drive and admission

On **a genuine real external EVENT**, freeze its event-start W/H and every eligible LIVE native identity/generation. Compute an independent **fresh scratch** two-pass with:

`A_prev=0; P_T=0; sigma=0; bootstrap=0`, current genuine external mechanical SIC X, normal normalization/gain and **only one synchronized LOCAL/CROSS** propagation. Never substitute normal full A, temporal residual, predicted-only activity, an internal selected event, or learned surface labels for fresh. No external X -> every fresh activity=0.

For each structurally legal native G, compute in sorted physical member order:

`M_G_fresh = sum(fresh_i for i in members) / size`.

For sorted unordered pairs `(i,j)` of real LIVE reciprocal CONSOLIDATED **LOCAL** links with `R^B_ij>=theta_A=.10`, compute:

`Cohesion_G_fresh = sum(R^B_ij * min(fresh_i,fresh_j)) / sum(R^B_ij)`.

Numerically stable deterministic binary64 folds, with existing quantization/sort authority. Zero denominator/nonfinite/invalid structure -> diagnostic and no admission; no fabricated cohesion. A **NEW** native Attractor is admitted only if BOTH:

- `M_G_fresh >= theta_in = .40`;
- `Cohesion_G_fresh >= theta_ctx_form = .50`;

in the SAME current genuine external event and on the SAME frozen W/identity/generation. Initial `C=M_G_fresh`, `age=0`, `err=0`. The fresh-cohesion test is admission only, not an extra excitatory current or alteration of W.

Crucial distinction: CoreCoverage>=.70 is an event-to-surface/FORM concept and MUST NOT be silently used as a replacement for fresh_mean or cohesion.

## 4. R05 continuation, sigma, error and collapse

On subsequent events, use the **previous** valid active native Attractor state for contextual sigma, with `rho_s=.90`; compute the current normal two-pass once. New `C_G(t)` affects sigma **only at t+1**, never recursively at t or in fresh. Preserve normal two-pass physics, source masks, normal temporal contribution and direct SIC. Multiple LIVE Attractors sharing members use the normative operator already defined for overlap (check existing `_context_operators`: max of prior contributions), not sum or repeated stimulation without source authority. Require exact legitimate ID/generation for each contribution.

For an ACTIVE G, update once per processed event: `age_G += 1`; `C_G(t)=max(.90*C_G(t−1), M_G_fresh(t))` unless collapsed. Boundary precedence: **HARD_BOUNDARY > age>=T_max=30 > accumulated error > continuation**. A fresh observation does NOT reset accumulated prediction error. Attractor cannot be immortalized by repetitive fresh events; age grows monotonically until collapse. On fresh zero, strength decays but does not spontaneously gain fresh evidence.

Prediction-error source must come from actual frozen prior member emitters `i in G ∩ F_step(prev)` and genuine LIVE legal ASSOCIATIVE `(i,j)` one-step links: `p_Gj=NoisyOR(A_i(prev)*Q_ij^ASSOCIATIVE)`, eligible only if `p_Gj>=theta_pred=.25`. Compare **only directly witnessed externally comparable current targets**, never a caller-provided expected output Y, synthetic matched target, future information or a readout label. `miss_G=sum[p_Gj*(1−o_j)]/|J_valid|`; if none valid, err unchanged; else `err'=min(Theta_err+1,err+miss)`. Collapse if `err>Theta_err=1.50`. Explicitly measure a legal real comparable outcome if the current learning curriculum can produce one; otherwise mark **ERROR_EXTERNAL_COMPARABLE_NOT_RUN** and do not claim full error-gate production PASS. Numeric-only counterexamples still test exact math.

If no real live native G at event start, no Attractor can be admitted. If G is archived, removed, mutated to a new generation, or failed structure audit between observations, invalidate the prior active reference before it can contribute sigma, never remap it by old ID alone. A newly FORM/GROW/MERGE/SPLIT version created at the same root END cannot backdate activation to its prior observations.

## 5. R05 runtime integration and persistence/recovery

Implement actual native Attractor support for the explicitly selected R05 capability in both:

- **Read-only neural sessions** on genuine learned W: actual SIC features, correct transient F_step/mu, fresh/normal pass, runtime sigma from prior Attractor, ordered traces; W/H and caller R remain byte-identical. Do not inject native assembly via fixture arguments. Attempted stale/archive ID injection must refuse.
- **External LEARN root event stream**, if the current scientific/event journal provides the exact evidence for provenance and R continuity: actual event-start W, pre-current valid native IDs, genuine fresh input, OPEN R checkpoints, H legitimate adaptation, replay consistent with true event witnesses, cold PROCESS recovery. Use an explicit new backend/capability/versioned R record; old END and old event replay must not change. If integration would require an unapproved scientific law/provenance reinterpretation, stop `SPEC_BLOCKED`, not a fake production PASS.

Native Attractor ephemeral records must specify `(assembly_id, structural_generation, strength, age, error)` and sufficient frozen provenance to validate the actual event-start W. Never serialize them into W, recalculate admission from post-END W, or claim H changes in read-only mode. On BEGIN first-event reset, HARD_BOUNDARY, independent root, abort and read-only session exit, clear/restore R lawfully. On crash during OPEN EVENT/END, restore precisely last committed R/H/W with no double aging or error accumulation. Test duplicate/replayed events, old version fallback/refusal, invalid/unknown/stale references, tampered checkpoint re-sign and mismatched W generation.

The implementation may isolate R05 to a new explicit mode such as `I4_NATIVE_ATTRACTOR_V1` deriving from R04's accepted native operator capability, provided the old codepaths remain bit-for-bit compatible; any new event-time checkpoint encoding must be **versioned** and derive its authorization from authenticated root and graph snapshots. Do not silently invent a new evidence lane, change the model's learning updates, or let read-only processing mutate H.

## 6. R05 mandatory falsification experiments (no fixtures as positive authority)

Run at least two separate **genuine** production training trajectories starting from an empty Schema5 RootStore; one must reuse the accepted R04 4-member native clique or another actual authenticated native G. Separate observed R05 runtime events MUST be produced by normal physical input, not by copying historical final activity into R. Report exact original independent learning root IDs, committed cells, directed LOCAL Q/E/S, live AssemblyIDs/generations, pre-event W/H, SIC bundles, fresh raw/final activity, M_fresh/cohesion, R state and sigma applied on next event.

At least these checks are required:

- **R05-T01:** real native identity/generation authorization; fixture, archived, stale and forged subjects fail.
- **R05-T02:** independent fresh scratch frozen zero prior/temporal/sigma/bootstrap, one LOCAL propagation; no input->zero.
- **R05-T03:** real positive same-event dual threshold admission with measured W and computed weighted cohesion; separately one threshold PASS/other FAIL negatives.
- **R05-T04:** previous-Attractor sigma affects only NEXT event, never current fresh, no double drive, current R changes lawfully.
- **R05-T05:** stable C=max(.9*C_old,Mfresh), full age horizon0–30, collapse precedence and boundary reset; no age reset from repeated fresh.
- **R05-T06:** actual valid external ASSOCIATIVE prior prediction and direct comparable targets for miss/err, or an explicit production `NOT_RUN` qualifier with falsifying non-comparable tests. No evaluator Y leakage.
- **R05-T07:** structural GEN change, archive/merge/split, cold snapshot mismatch invalidate prior active identity and sigma before influence.
- **R05-T08:** read-only W/H/caller R invariance; no root or learning/evidence credit or backwards peripheral attestation.
- **R05-T09:** genuine LEARN OPEN root versioned R progression, ABORT exact H_BEGIN, crash before/after EVENT/END COMMIT, historical recovery, duplicate guards, old version and corruption refusal.
- **R05-T10:** reproduced negative/control ablation on SAME frozen learned W/H/R: with-Attractor vs zero-context sigma; distinguish causal activity effect from external learning and report zero benefit if no effect. No performance tuning to force an improvement.

No extra blanket experiments merely to pad test totals. Every scientific-positive result must cite actual production code path, saved trace and self-contained re-executable input.

## 7. Local R05 scientific acceptance gate (mandatory BEFORE R06)

**R05-G01** native eligibility/persistence provenance; **G02** proper fresh-only activity and same-event admission; **G03** lawful next-event strength/sigma and age/boundary collapse; **G04** external-comparable prediction error and refusal of unqualified outcomes (mark PARTIAL if valid real comparable unavailable); **G05** independent production trace and non-retroactivity; **G06** no W/evidence changes in read-only sessions, valid H separation in LEARN; **G07** cold replay and failure atomicity on authentic R; **G08** unchanged 884 baseline and static/source integrity. Record evidence classification for every gate: `PRODUCTION_PASS`, `COMPONENT_PASS`, `NUMERIC_ONLY`, `NOT_RUN`, `EMPIRICAL_BLOCKED`, `SPEC_BLOCKED`, `FAIL`.

**R05 cannot be called complete if only the existing fixture-level `transition(...)` succeeds, if sigma affects the same event that admitted G, or if an externally comparable error is fabricated.** If R05 is partially blocked, STOP before R06 and provide a detailed partial review, keeping the accepted R04 experimental baseline intact.

## 8. R06 Integrated Verification — only after passing R05 gate

R06 is verification/governance, not permission for new scientific features. Execute full integrated I4 on a genuine zero-state learning curriculum:

1. I3 external-cell commitment, legal directed LOCAL learning, live reciprocal consolidation.
2. I4-R02 real FORM, I4-R03 MAINTAIN/GROW, multi-FORM, lawful R04 MERGE/SPLIT, structurally versioned identities and native operator journal. Use authenticated actual R04 input/trace lineages, not injected pre-formed Assemblies.
3. Real R05 Attractor from an already-LIVE legal Assembly, not fixture; show admission, maintained active state and collapse. If full single-database sequence containing all operators is physically unreachable in this lab, use separately authenticated genuine independent trajectories and state the limitation: **do not falsely claim a single experiment performed every operator**.
4. Root isolation, read-only, OPEN/ABORT/END, before-/after-COMMIT process exits, final W/H/R, exact old source history W5 and close compatibility, versioned R snapshots/codec, archived IDs, generation-stale refusals, cross-platform physical fingerprints, deterministic checks and repeated END idempotence.
5. Revisit known R04 gaps honestly: genuine terminal MAINTAIN ARCHIVE and a second MERGE/SPLIT eligible after cooldown. Attempt only a **bounded, declared** real curriculum if feasible, never a synthetic learned claim. If not observed, leave `NOT_RUN` and record whether that prevents a *full lifecycle freeze*, rather than misclassifying an R04 scoped PASS.
6. Model ablations: native Attractor ON/OFF on identical state, W/H/evidence invariance, replay vs actual external input; measure runtime/memory/storage where available. **Attractor response does not prove better learning or language.**
7. Run complete retained 884 tests plus all newly added R05/R06 tests, two CI full runs per OS as in original workflow, Ruff check/format, mypy, pip check, verify-specs, clean git diff and actual source/config unchanged. Final delivered **HEAD** must match final CI run `head_sha` and both Ubuntu/Windows job SUCCESS.

Produce a **coverage matrix** for every I4 claim with exact root/event/member/identity/generation/traces, independent component vs genuine production status. Categorize Core/LLA outstanding requirements outside I4 (context owners, readout, generation, multimodal, etc.) without falsely claiming they were implemented. Old R04 report remains immutable; a new final R06 document may supersede the coverage status ONLY with new evidence.

## 9. Resource and experiment budget

Codex may reuse the existing authenticated R04 physical witnesses to design experiments, but **not** their outputs as artificial new root evidence. Record all proposed curricula before running positive trials, then revisions (at most 6 declared R05 experiment families, at most 3 revisions each, plus separate bounded atomicity/codec controls). Do not brute-force unknown SIC values until a target result appears. Prefer short genuine R05 trials using already learned real Assemblies; copy a real saved physical lineage only for controls, never call a copy an independent learning root.

The previous R04 long controls reached hundreds of MB to >1GB per SQLite database and consumed substantial execution time. Use bounded checks and avoid committing multi-GB SQLite files; only commit reproducible scripts, compact canonical receipts/digests, justified measured summary and optionally compressed data within repo policy. Record actual walltime, peak memory when measured, file sizes and major trial costs. Do not invent token savings or scalability claims; measure if tooling provides cost data.

Keep original failed experiment attempts and repair rationale in the append-only engineering log. Re-run targeted checks at each code checkpoint and full suite after each major stage and final delivery. Do not weaken existing tests or add skip/xfail to hide regressions. No unauthorized branch merges/force pushes.

## 10. R06 deliverables and decision gates

Deliver at least:
- `docs/implementation/I4-R05-NATIVE-ATTRACTOR-VERIFICATION-REPORT.md` with verified genuine and negative trials, native R design and relevant W/H/R hashes.
- `docs/implementation/I4-R06-FINAL-CONSOLIDATED-REVIEW.md` with I0–I4 stage inventory, R04+R05 gate matrix, explicit old unresolved cases, quantitative experiments, cold recovery and scientific classification.
- `docs/implementation/I4-R05-R06-AUTONOMOUS-ENGINEERING-CHANGELOG.md` (append-only checkpoints, bug fixes, failed trials, exact SHAs and verification commands).
- Reproducible experiment drivers and bounded canonical JSON traces with commit/source/witness/digest attribution.
- A **non-binding final freeze recommendation**: `I4_ENGINEERING_FREEZE_CANDIDATE` or `I4_PARTIAL_WITH_OPEN_GATES`, with separate scientific coverage map and protected merge instructions **NOT EXECUTED**.

Final gates: **R06-F1** complete real positive R05, **F2** original R04 and I3/R02/R03 compatibility, **F3** authentic historical W/H/R/identity lineage under crash/replay, **F4** no new scientific or semantic/replay/output capability, **F5** test matrix and static/integrity + final head both-OS CI, **F6** rigorous limitations and freezing/governance decision criteria, **F7** user-visible code-change audit and experiment-efficiency assessment without invented token/time savings.

## 11. Terminal statuses and safe fallback

- **`I4_R05_R06_AUTONOMOUS_REVIEW_READY`**: R05's required genuine gates and R06's scoped engineering verification have passed; independent owner/reviewer acceptance still required. This does NOT automatically imply a global scientific freeze, main merge or L5 launch.
- **`I4_R05_R06_PARTIAL_BLOCKED`**: at least one essential genuine runtime gate is not met; preserve verified subsets, no unsafe freeze.
- **`I4_R05_R06_SPEC_BLOCKED`**: law, source authority or irreversible data-policy decision cannot be resolved without new owner approval.
- **`I4_R05_R06_ENGINEERING_FAILURE`**: source integrity/regression/cold-history/transaction reliability is broken. Provide last verified safe commit and rollback recommendations.
- If final exact-head CI is not green, report **`I4_R05_R06_REVIEW_PENDING_CI`**, never REVIEW_READY.

Never edit `main` or protected I4 branch, never claim L5 started. Stop and deliver ONE consolidated report with exact links, SHA, tests, gate statuses and unresolved limitations for independent review. The owner chooses acceptance, I4 freeze, integration and the next stage.
