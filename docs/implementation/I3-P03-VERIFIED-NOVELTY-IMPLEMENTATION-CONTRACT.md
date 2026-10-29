# DGCA NEXT — I3-P03 Verified Local Novelty & Recycling Feasibility Contract

**Document ID:** I3-P03-VERIFIED-NOVELTY-IMPLEMENTATION-CONTRACT
**Revision:** R01 — 2026-10-29
**Status:** AUTHORIZED FOR IMPLEMENTATION — NOT YET VERIFIED
**Repository / branch:** naoufelbvb2-arch/DGCA-NEXT-V1 / feature/i3-local-learning
**Accepted P02 implementation SHA:** 80ae771283bb9397660b740338e169bf6cbe8c32
**P02 audit:** docs/implementation/I3-P02-INDEPENDENT-ACCEPTANCE-REVIEW.md
**Only normative science:** CORE RC4.4 + LLA RC4.4, DESIGN CANDIDATES, NOT FROZEN and NOT EMPIRICALLY VERIFIED.
**Earlier contracts:** I3-IMPLEMENTATION-CONTRACT.md, I3-S01-S02-APPROVED-EXECUTION-CONTRACT.md, I3-P01 and I3-P02 contracts.

## 0. Purpose — one bounded vertical slice, not mass rewiring

P02 ACCEPTED proves bounded genuine API-ingress LOCAL and one-step ASSOCIATIVE synaptic learning. P03 now implements a **real event-bound VerifiedLocalNovelty producer** and a **read-only, production-graph-derived bilateral recycling eligibility checker**. The explicit engineering stop is a real event/root trace that can say **novelty TRUE/FALSE and recycling ALLOWED/BLOCKED for a particular actual dynamic slot**, without changing a single latent connection.

This P03 intentionally DOES NOT apply any physical recycling, change W slots/reverse index/wiring, enable automatic production recycling, prune expired candidates, invent a new synaptic law or create contextual owners. A separate reviewed P04 contract may authorize ONE controlled atomic production replacement with full saved W codec and a genuine event-bound trigger, followed by independent ablations before any automatic recycling. This decomposition avoids the earlier failure mode of a broad request whose unit tests succeed while its real executor is unfinished.

**P03 acceptance does NOT require a positive rewiring result**; it DOES require a genuine root- and event-authorized novelty value, correct one-hundred-completed-root aging, and true graph guard decisions on production W. A positive structural feasibility verdict may be impossible when protection or replacement targets block; report that as genuine measured outcome, not a reason to synthesize a graph. P03 acceptance fails if its asserted "verified novelty" came from caller-supplied floating-point scalars or fixture-only input.

## 1. Existing scientific authority and exact formula

LLA RC4.4 §5.1 and Core RC4.4 §1.3.5 define:

nu(u,t) = max(0, X_ext(u,t) - min(X_ext(u,t), P_T_u(t))) / max(X_ext(u,t), 1e-6)

with nu=0 when u lacks a direct genuine external observed SIC receiver. P_T must be the **real canonical frozen prior-event one-step temporal prediction computed BEFORE current SIC**, not after X, not Pass2/synchronous/residual response, and never a target-guided expected label.

- Use canonical true SIC integer X_fixed/1,000,000 with existing declared Q6 comparison; theta_R=.30.
- At most the same physical observed receiver ID per event; SIC feature collisions cannot create two witnesses.
- A trained, directly observed cell can legitimately have high novelty when the physical predictor misses; P_T=0 may produce nu=1. Such a numeric result is NOT a claim of useful knowledge, semantic novelty, or a new link.
- A birthday/uncommitted receiver may be observed but is not automatically trusted as a recycling endpoint: the first-lab production trigger must be a physically committed-before-event receiver and a valid genuine LEARN witness.
- STRICTLY separate branch novelty nu_ctx=c*dP*dY from local residual novelty nu(u,t). Never use nu_ctx for dynamic slot recycling.

## 2. Trusted event and completion provenance

The I3-P02 production RootStore persists the immutable ExternalEventObservation, x_fixed, event global ID, order, root, pre-W/H digests, final A, prior F_step, pre-SIC temporal lane, and completed/aborted root journal. Build a **root-journal-authorized VerifiedLocalNovelty record**, not a public factory:

- Physical receiver cell ID, event ID and root/exposure ID, event order, direct SIC X_fixed, actual frozen pre-input temporal P_T numeric value for this receiver, Q6 nu, source observation digest and pre-event W hash, model config/spec hashes, and completion attribution.
- Verify a valid original recorded external LEARN event, receiver committed **before** that event, positive DIRECT X_fixed, original graph state and temporal lane integrity (including boundary and previous-source F_step), and either the authentic completed-root close record or a clear **PROVISIONAL only** state until END.
- An OPEN root may compute and journal provisional novelty for debugging, but **only COMPLETED** valid genuine external roots may authorize irreversible recycling changes in later P04. ABORTED, READ_ONLY, REPLAY, INTERNAL_SELECTED, GENERATE, missing/mismatched event/root and fixture records must never yield a completed VerifiedLocalNovelty authority.
- Verification must query the root journal/store, not accept caller-provided root IDs/digests/scalars as self-certifying; stored hashes alone do not authenticate an attacker with arbitrary SQLite modification, and no real-world semantic truth is claimed.
- Maintain pure deterministic calculations and explicit diagnostics for missing P_T, absent source, X=0, wrong event, wrong boundary and malformed/corrupted digest; an unpredicted valid direct target has P_T=0 if the genuine runtime lane actually was zero.
- Production event already has pre-current-SIC temporal aggregate; tests MUST confirm that persisted temporal is the temporal input to the I2 first/second passes and is recomputable from frozen pre-event W and previous actual F_step. Do not use read_only_step to issue LEARN proof and do not recompute from post-link W (END may change the graph).
- Saved pre-event historical W may contain previously verified REAL synapses. A completion verification must use the EVENT's frozen W for that event, not later END state.

## 3. Real completed-root age and full physical guard

Core §1.3.5: a physical dynamic slot occurrence at (owner_id,index) carries assigned_at_completed_close_serial and must age through **at least 100 genuine COMPLETED external LEARN root closes**. No credit for EVENT steps, OPEN roots, ABORT, READ_ONLY, internal/replay, or duplicate END. Source ages are physical per-slot metadata. The current production close_serial exists; derive trusted current serial from validated RootStore, not an arbitrary supplied integer.

For a candidate physical pair (u,v), inspect ALL actual u→v and v→u slot occurrences in the current committed production graph, including all 24 slots and fixed/dynamic categories; one-sided occupancy is allowed but requires checking every occurrence present.

Refusal rules (use existing names and documented precedence):
- RECYCLE_BLOCKED_FIXED: any occurrence is fixed LOCAL/topographic, regardless of nominal novelty or age.
- RECYCLE_BLOCKED_LIVE_OR_PROTECTED: any live directed synapse across any scope in either orientation, live reservation, or protected slot on the pair. A weak or expired but still-live CANDIDATE counts as live protection until a separately lawful removal; never silently prune to make recycling pass.
- RECYCLE_BLOCKED_CANDIDATE: any pinned contextual/real candidate slot (I5 remains unavailable, still handle real pin state if encountered in validated graph).
- CONFIRMATION_WINDOW_NOT_ELAPSED: every affected dynamic occurrence must have assigned_at_completed_close_serial and age >=100 relative to trusted completed-close serial.
- UNVERIFIED_NOVELTY: no authenticated actual COMPLETE event-bound endpoint novelty at >=theta_R; caller floats/fixture or internally selected witnesses rejected.
- NO_RECYCLING_REPLACEMENT: no legal current-event ranked replacement (category-compatible region, distinct target, no self/duplication, and no violation of other owners' constraints); reject the entire bilateral pair, never partially allow one side.

**Eligibility checker must be pure/read-only:** produce a typed immutable diagnostic decision referencing physical pair, current audited graph hash and completed-close serial, every affected occurrence's age and guard evidence, source original event/root identity, and the actual candidate replacement choices if required by the law. It cannot itself mutate W, perform recycling, change capacities, or mint E/S/count. A caller cannot claim a positive diagnosis is a mutation permit; future P04 must recheck in an atomic current-state shadow.

### Current P02 schema trap

P02 graph_codec currently supports unmodified original 24-slot assignments per sensory cell, rejects production recycling_log and does not encode changed per-slot assignment/wiring replacement. That is OK for this P03 pure guard, but NOT for P04 actual rewiring. Do not change this schema just to claim recycling in P03. Preserve P02 normal learned W with synapses, evidence, H, completed roots and read-only effects exactly.

## 4. Test matrix

**P03-T01:** valid production real COMPLETED external event & positive direct committed-before-event SIC support generates exact bounded nu at X=1,P_T=0 (nu=1), with attached event/root evidence. No post-Pass2 substitution.
**P03-T02:** X=.6,P_T=.5 -> nu=(.6-.5)/.6=1/6; correctly below theta_R=.30. X=.6,P_T=.1 -> nu=5/6; Q6 threshold conforms to Core numeric policy. Numeric fixtures are auxiliary; actual authority MUST come from RootStore.
**P03-T03:** prediction-only high P_T, residual-only or purely spatial activity without EXTERNAL DIRECT receiver cannot generate positive externally witnessed nu.
**P03-T04:** newborn in same event has X but not committed-before-event, so cannot authorize recycling; later true observed event may.
**P03-T05:** event 0 cold boundary zeroes preceding temporal P_T; subsequent same-root transition yields actual one-step predicted value under real trained W and correct F_step; cold new root starts with R_cold, no previous-root P_T contamination.
**P03-T06:** mismatched root, event, digest, pre-W hash, forged caller float, FixtureLocalNovelty, replay/read-only/internal, unsupported regions and malformed SIC all fail closed.
**P03-T07:** OPEN event provisional only, ABORT discards irreversible authorization, COMPLETED root has a genuinely valid newly checkable event witness; duplicate END does not make a second independent novelty root.
**P03-T08:** pair with live LOCAL or ASSOCIATIVE link in either direction refuses recycling regardless of nu=1 and 100 serial age; evidence/S/Q remains bit-identical.
**P03-T09:** fixed LOCAL/TOPO slots refuse, protected/pinned/reserved slots refuse according to precedence, one-sided dynamic pair separately handled.
**P03-T10:** exactly 99 completed closes is insufficient, exactly 100 is eligible for further checks; age is measured from stored slot assignment serial, not event count, and not root ID. Test with authentic completed roots, including ABORT and extra events that do not age it.
**P03-T11:** bilateral occurrences both must independently pass age and structural guards; one recent reverse occurrence blocks both. No duplicate slot references or partial feasible decision.
**P03-T12:** no legal replacement yields NO_RECYCLING_REPLACEMENT; rank from genuine current-event L_t ∪ K_new per approved L01 and respect distinct target/category/scope.
**P03-T13:** read-only novelty and guard calls leave W bytes, H bytes, R/root status, synapse evidence, outgoing/reverse index and completed serial byte-identical.
**P03-T14:** persisted journal and cold restore authenticate same completed-event nu and physical guard; corrupted/mismatched schema fails.
**P03-T15:** no "100-root fixture speed-up" or arbitrary injected completed serial; a bounded official harness must issue 100 actual completed independent external LEARN roots for the positive age test. Report runtime/memory so performance isn't hidden. If too expensive, mark this test NOT_RUN and do not claim full gate PASS.
**P03-T16:** no actual slot mutation, no automatic production recycling enabled, no Assembly/owner/generation claims, no source/config drift; all 682 previous regressions PASS.
**P03-T17:** final-head Ubuntu + Windows CI, pytest, Ruff, format, mypy, pip, spec integrity and clean diff PASS.
**P03-T18:** report distinguishes VERIFIED NOVELTY from RECYCLING ELIGIBLE; genuine high novelty does not imply a legal physical replacement, learning benefit, retention improvement or active recycling.

## 5. Execution checkpoints and acceptance gates

**P03-A — production novelty record and authority.** Integrate event pre-SIC temporal and committed-before-event direct X into one immutable, auditable root/event-bound producer. Add negative provenance tests. Run regressions.

**P03-B — genuine root completion and serial.** Verify completed root identity and exactly 100 completed-close eligibility, independent of event count; no phantom serial or root reuse. Run tests and performance measurement.

**P03-C — pure physical bilateral guard.** Reuse I1 selectors and physical guard semantics but NOT fixture APIs. Inspect current production graph and original immutable slot metadata, live/protection/fixed guards and genuine current-event ranked alternatives; return immutable reasoned decision, ZERO graph mutation. Do not enable production auto wiring.

**P03-D — cold restart / cross-platform acceptance.** Prove roots and decisions survive save/reload, source hashes unchanged, all regression/new tests and final-head CI success.

**G01:** Authentic RootStore event-bound local novelty, pre-SIC P_T, direct SIC, root completion proof, validated numeric formula.
**G02:** Proper provisional/COMPLETED/ABORT/READ_ONLY/fixture separation.
**G03:** Real completed-close serial + 100-root per-slot age with genuine external events, boundary at 99/100.
**G04:** Exhaustive bilateral physical fixed/live/reserved/pin/protection guards, one-sided/two-sided scope, no hidden deletions.
**G05:** Bounded lawful replacement feasibility from physical current-event sources without mutating slots or resource ledgers.
**G06:** Byte-identical W/H/R and evidence before/after inspection, complete cold persistence, corrupt/tampered authority refusals.
**G07:** Preserve all 682 P02/I0–I3 regressions, exact CORE+LLA RC4.4 hashes, tests, mypy/Ruff/format/pip and final-head Ubuntu/Windows CI.
**G08:** Forensic report shows exact genuine event/root IDs, X_fixed/P_T/nu, eligible/ineligible pairs, assigned/completed serial, 99/100 traces, current after-reload W/H hashes, limitations and all gate dispositions.

## 6. Report and stop

Deliver docs/implementation/I3-P03-VERIFIED-NOVELTY-VERIFICATION-REPORT.md with:
- exact changed files/implementation commits, current branch/head and reviewed P02 base;
- official source hashes and no changes to RC4.4;
- actual genuine API events and completed-root journal evidence used to derive nu and calculate guard;
- exact physical receiver and pair IDs, X_fixed, frozen P_T, nu/q6, current serial/slot assigned serial/age, blockers, replacement candidates or precise unavailable reason;
- how the 100 genuinely completed roots were created (including runtime and storage growth), ABORT and read-only no-age counterexamples, clean post-restart state;
- full raw test commands, results/count, CI runs tied to last delivery SHA and P03 G01–G08;
- explicit scientific claims that remain NOT_RUN: actual production rewiring, enabled auto-recycling ablation, full I3 end-to-end novelty benefit, contextual owner, Assemblies, Replay, multimodal and language generation.

Final commands:
python -m pytest -q --basetemp=.pytest-tmp -rs
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m dgca_next verify-specs
python -m pip check
git diff --check
git status --porcelain

**Stop at I3-P03 REVIEW READY** only when all G01–G08 pass with real authenticated RootStore evidence and no production graph mutation. Otherwise **I3-P03 PARTIAL / SPEC_BLOCKED / EMPIRICAL_BLOCKED** with minimal reproducer and no manufactured authority. Do not merge into main, alter science versions, enable recycling, or start P04/I4 until independent review. Full I3 remains PARTIAL.
