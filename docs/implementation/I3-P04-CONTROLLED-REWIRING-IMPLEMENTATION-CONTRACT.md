# DGCA NEXT — I3-P04 Controlled Atomic Rewiring Implementation Contract

**ID:** I3-P04-CONTROLLED-REWIRING-IMPLEMENTATION-CONTRACT
**Revision:** R01 — 2026-10-30
**Status:** AUTHORIZED ENGINEERING INCREMENT; NOT YET VERIFIED OR ACCEPTED
**Repo/branch:** naoufelbvb2-arch/DGCA-NEXT-V1 / feature/i3-local-learning
**Reviewed P03 code SHA:** bc2e195946b98a14fc138498761f0e435ea33375
**Accepted P03 review:** docs/implementation/I3-P03-INDEPENDENT-ACCEPTANCE-REVIEW.md
**Only normative science:** docs/specs/DGCA_CORE_RC4_4.md and DGCA_LLA_RC4_4.md, DESIGN CANDIDATES, NOT FROZEN / NOT EMPIRICALLY VERIFIED.
**Prior contracts:** I3-IMPLEMENTATION-CONTRACT.md, P01, P02 and P03 contracts.

## 0. Purpose, scope and hard boundaries

P03 independently established true event-bound novelty and read-only bilateral feasibility. P04 shall implement **one externally requested, internally validated, real atomic physical dynamic-slot rewiring** during a legitimate root END, and persist all affected forward slots, inverse latent references, wiring log, replacement authority and root close record.

A caller may choose a physical pair to INSPECT inside a genuine OPEN root; it CANNOT supply trusted novelty values, replacement targets, completed serial, arbitrary root proofs or hardcoded learning outcomes. The actual END engine validates every necessary condition from stored RootStore events, current physical W, frozen historical input and prospective genuine completed-close serial.

At most ONE controlled pair may be requested per external root in P04. This is bounded engineering test instrumentation, NOT an automatic selector/scheduler. **automatic_recycling_enabled stays FALSE**. A successful P04 cannot be presented as evidence of improved learning or memory retention. Do not implement native Assembly/owner, generation, multimodal thresholds, Replay, candidate expiration cleanup or a broad recycling policy. No RC4.5, no main merge and no I4 work.

## 1. Scientific laws and precise close-order requirement

Use Core RC4.4 §§1.3.4–1.3.6, 10.1–10.2 and LLA RC4.4 §5.1, §7 without alteration:

- Genuine novelty: nu(u,t) = max(0, X_ext(u,t)-min(X_ext(u,t),P_T_u(t))) / max(X_ext(u,t),1e-6), only for committed-before-event direct external SIC receivers with proven frozen PRE-SIC one-step P_T and Q6(nu)>=Q6(theta_R=.30).
- Physical age: completed_external_closes_at_check - assigned_at_completed_close_serial >= W_conf=100 for EVERY affected physical slot occurrence. No OPEN, ABORT, READ_ONLY, REPLAY, GENERATED or duplicate END age credit.
- Inspect ALL occurrences u→v and v→u, not just requested slot. Any fixed LOCAL/TOPO, protected, pinned, reserved or LIVE CANDIDATE/EPISODIC/CONSOLIDATED synapse in EITHER direction and ANY scope blocks the WHOLE bilateral pair.
- For every affected dynamic occurrence, a lawful new target must come from that genuine event's ranked L_t (frozen final Q6 activity of previously committed lawful frontier) plus K_new (direct SIC Q6 from lawful simultaneous births), constrained by category/region, no self/duplicate target, no re-selection of just-removed target. One-sided occupancy is legal. Both sides must find a replacement or no change.
- Existing positive link proposal settlement has priority over rewiring. After applying P02 root MAX and link evidence to a *shadow* WpostEvidence, inspect live protections in that SAME shadow before any replacement. Never delete or degrade accepted links to make rewiring possible.
- The trigger event is the final genuine LEARN EVENT of the root currently being closed. The completion serial used must be the serial actually being committed at this END. An older completed EVENT from a different root or a stale P03 ALLOWED result cannot confer mutation permission.

The P03 event verifier only labels its novelty COMPLETED after a real END. For P04, it is permissible to *stage and evaluate* the same root-bound evidence provisionally within the END transaction, conditional on that exact transaction atomically publishing the COMPLETED root, verified serial and rewiring together; never expose a provisional novelty as an unconditional credential. **If this staged-at-END interpretation contradicts Core or LLA when fully inspected, STOP SPEC_BLOCKED with minimal counterexample; do not silently invent a new scientific rule.**

## 2. Checkpoint A — canonical production W codec and graph audit

P03 current graph codec supports only original unmodified 24-slot layout and rejects nonempty production recycling_log; P03 pin/reservation/protected mechanics were partly fixture-only.

Implement an explicitly versioned production W and journal codec for changed dynamic slot targets, current per-slot assignment and age metadata, fixed unchanged local/topographic original assignments, original cell birth provenance, forward and inverse latent indexes, ordered wiring and auditable replacement records. Production recycling records must have TRUE root/event and completed-close provenance and a distinctly nonfixture trusted origin; do not launder an I1 FixtureRecyclingRecord or a caller-supplied boolean into production.

Persist old target, new target, owner ID, slot index/category, prior/current assignment metadata, actual root/event/order, immutable observation witness digest, validated novelty context or proof reference, completed serial and actual replacement reason. Persist exact cross-record linkage to root CLOSE; recompute and audit on load, preserving legitimate learned synapses S/E/root credits, outgoing budgets and reservations. Any altered fixed slot, dangling reverse ref, repeated target, changed protected live pair or mismatched journal must fail closed.

If production pin/protection/reservation state is unsupported, fail closed on any such production encoding and clearly mark those guard cases NOT_RUN for real persisted W (fixtures alone are not enough). You may implement full supported state only with independent source-compatible audits; do not fabricate I5 owner pins. Preserve prior 693 regression tests. Old production schema may be explicitly rejected with clear version diagnostic if safe automatic migration is not possible; never silently reinterpret old snapshots.

## 3. Checkpoint B — restricted request staging

Add an explicit RootStore-controlled API to stage ONE request (exposure_id, latest_event_order, owner_id, slot_index) during the corresponding OPEN root after a legitimate external EVENT. RootStore verifies root/order and current physical slot and journals the request atomically. A request only nominates a pair for examination; it conveys NO novelty/recycling authority. Repeated identical request may be idempotent; conflicting second request fails closed.

Journal survives a restart of OPEN root, with no new EVENT, duplicate proposal, adaptation or implicit live slot change. ABORT restores exact H_BEGIN, preserves only otherwise lawful sensory births and never performs requested rewiring. END with no request must preserve P02 behavior bit-for-bit, including completed-root evidence and H. Read-only, external float, fixture event or already COMPLETED root may not stage a new request.

## 4. Checkpoint C — atomic real graph mutation at END

In ONE SQLite END transaction:

1. Freeze the actual pre-close W/H/R, event journal and staged optional request; derive normal P02 root-max winners by full q with paired y.
2. Settle real positive root evidence FIRST to WpostEvidence; protect every still-live CANDIDATE, EPISODIC_INDEXED and CONSOLIDATED link, both directions, all scopes. All credits remain intact.
3. For requested latest-event pair only, compute historical pre-current-SIC P_T from saved event W/H and prior F_step, verify true external observation, committed-before-event receiver, correct pair endpoint, and physical guard on WpostEvidence with prospective current genuine completed serial. Re-evaluate replacement ranking from that original event; do NOT trust a previously calculated read-only decision or caller-reported replacement.
4. If any condition fails, record the named refusal and leave WpostEvidence unchanged; ordinary legal root completion/evidence still succeeds. For ALLOWED, create one *shadow* Wrewired changing ALL physical occurrences in both directions together, with new assignment serial, reverse indexes, wiring and production recycling record. Audit full graph including all live links, budgets and current refs before publication. No partial rewiring, and do not create new synaptic evidence from it.
5. Publish W/H/close record/complete root marker/new serial/request disposition/rewiring record atomically. A crash before/after commit yields whole pre/post state, never a split END. Duplicate END is idempotent, cannot rewire again or increment count.
6. Historical journal validation on cold reopen must recompute both P02 evidence settlement and deterministic P04 rewiring using actual saved event and request, including the proper after-W hash, without rerunning neural activity or producing new learning. Reject corrupt/mismatched historical chain.

No unrequested periodic rewire, no auto flag enable. No evidence/pruning shortcut. Link-free comparison and learned W Q use remain unchanged outside the exact rewired dynamic slots.

## 5. Checkpoint D — genuine 100-root controlled experiment

Using a NEW production SQLite database (no fixture graph/synapses, no manual W mutation), issue at least 100 genuine independent COMPLETED external LEARN roots through RootStore, plus ABORT and READ_ONLY non-age control. Choose a physical dynamic pair from actual first-lab W and declare its physical ID selection rule. At the final eligible root, stage a restricted request and submit real external feature event providing actual endpoint novelty and legal candidate replacements. Do not force positive results by changing SIC, theta_R, theta_create, W_conf, thresholds, topology, fixture construction or synapses.

**Mandatory positive result:** one pair genuinely ALLOWED at age >=100 and physically rewired at successful END. Show original and new targets for every affected occurrence, actual source event/root, X_fixed, frozen pre-SIC P_T, nu/Q6, guards, fresh replacement ranking, new completed serial, changed W checksum, unchanged unrelated live q/E/S/root counts and correct root journal. After reopening on an independent connection/process, exact W/latent/reverse/wiring/recycling/learned-link state must match.

Mandatory negative controls: 99 completed roots refuses; one link newly created during SAME END protects the pair after evidence settlement; fixed and live reverse link refuse; no replacement refuses, whole pair stays unchanged; already-rewired new slot cannot rewire again before another 100 completed closes; ABORT/refusal/duplicate END cannot mutate W; read-only never changes it. Complete crash-injection before/after END commit, and corruption tests. If genuine eligible replacement cannot be obtained, return P04 PARTIAL / EMPIRICAL_BLOCKED with actual full physical counterexample, not a synthetic success.

## 6. Detailed acceptance tests

P04-T01 Preserve P02/P03 no-request path, no new behavior or scheduling.
P04-T02 Reject incorrect/rootless/stale/duplicate conflicting pair requests.
P04-T03 Historical P03 ALLOWED object cannot authorize mutation.
P04-T04 Genuine 99/100 age boundary, no credit for ABORT/read-only/OPEN.
P04-T05 All bilateral dynamic occurrences must rewire together; one-sided works without inventing reverse.
P04-T06 Fixed, protected, pinned, reserved and live candidate/episodic/consolidated reverse links block correctly; fixture-only subcases identified.
P04-T07 New synapse at SAME END takes priority and blocks rewire.
P04-T08 No legal current-event replacement means entire refusal and no partial graph change.
P04-T09 One genuinely executed nonfixture bilateral change, forward/reverse/wiring metadata and legal new age clocks.
P04-T10 Correct production recycle record, root/event witness, close serial and source/target identity after independent cold load.
P04-T11 Tampered witness/digest/old target/assignment or missing reverse ref rejected on restore.
P04-T12 End/abort subprocess crash and duplicate retry cannot double rewire/q/count/H.
P04-T13 Learned synapse S/E/root counts and read-only Q effects retained when unrelated dynamic topology changes lawfully.
P04-T14 Unsupported old schema fails closed or explicitly and safely migrates; no silent fake old records.
P04-T15 Never enable automatic recycling; no owner/Assembly/Replay/generation.
P04-T16 Preserve all 693 P03 tests, unchanged RC4.4 hashes, Ruff, formatting, mypy, pip, verify-specs and clean diff.
P04-T17 Ubuntu+Windows final-head CI success, actual root experiment reproducible, report resource/time/storage growth.

**P04-G01:** Valid true last-event/root trigger with completed-close serial, no caller-scalar authority.
**P04-G02:** Trustworthy production W + recyle-journal format and full graph invariants.
**P04-G03:** Post-evidence bilateral guard, protected knowledge wins, pin/reservation production limitations explicit.
**P04-G04:** At least ONE real production atomic physical mutation, all forward/reverse/wiring/age invariants.
**P04-G05:** All-or-nothing failure/crash/duplicate-ROOT/ABORT/READ_ONLY behavior.
**P04-G06:** Cold persistence, historical close-chain audit, learned W and H preservation.
**P04-G07:** 693 baseline+new tests, source hashes and final-head Windows+Ubuntu CI.
**P04-G08:** Complete numerical/physical evidence, explicit NOT_RUN automatic policy and no claim of learning benefit.

## 7. Report and hard STOP

Create docs/implementation/I3-P04-CONTROLLED-REWIRING-VERIFICATION-REPORT.md with exact commits/changed files, original physical slot IDs, new targets and category, real event/root/serial, X_fixed/frozen P_T/nu, assigned slot age before/after, post-evidence link protection, W/H and wire/reverse hashes, crash/tamper witnesses, schema numbers, 100-root elapsed time/memory/SQLite file size, test totals and final-head CI SHA and each G01–G08 status.

Run:
python -m pytest -q --basetemp=.pytest-tmp -rs
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m dgca_next verify-specs
python -m pip check
git diff --check
git status --porcelain

Branch feature/i3-local-learning only; no main merge, no science version change, no unapproved automated scheduler, no P05/I4. Stop at **I3-P04 REVIEW READY** only if actual root-authorized W rewiring and complete gates pass; else **I3-P04 PARTIAL / SPEC_BLOCKED / EMPIRICAL_BLOCKED** with exact reproducer. Full I3 remains PARTIAL pending separate final acceptance.
