# DGCA NEXT — I3-P02 Production Synaptic Learning and Atomic END

**Document ID:** I3-P02-LEARNING-END-IMPLEMENTATION-CONTRACT
**Revision:** R01 — 2026-10-28
**Status:** AUTHORIZED FOR IMPLEMENTATION; NOT YET VERIFIED
**Repo/branch:** naoufelbvb2-arch/DGCA-NEXT-V1 / feature/i3-local-learning
**Accepted P01 implementation SHA:** 6edb7a8b1aecfa81a2108ba2f5fe28a96f3a9966
**Normative scientific sources:** EXACTLY docs/specs/DGCA_CORE_RC4_4.md and docs/specs/DGCA_LLA_RC4_4.md (DESIGN CANDIDATE — NOT FROZEN — NOT EMPIRICALLY VERIFIED).
**Inherited contracts:** I3-IMPLEMENTATION-CONTRACT.md, I3-S01-S02-APPROVED-EXECUTION-CONTRACT.md, I3-P01-PRODUCTION-EVENT-VERTICAL-SLICE-CONTRACT.md.

## 0. Mission and scope

P01 established a real durable production EVENT but no learning. P02 MUST implement: actual external event observations → physical LOCAL/one-step ASSOCIATIVE witnesses and eligibility → staged LINK_PROPOSAL records in OPEN root → per-link/root MAX q with its paired y → D_event and D_close validation and deterministic capacity arbitration → atomic END_EXPOSURE publication of nonfixture live Synapse records and positive E_ext/S/count → COMPLETED root → cold-reloaded W and causal use in real I2 read-only dynamics.

Do not declare PASS until at least one new LOCAL and one one-step ASSOCIATIVE synapse are produced from actual independently submitted external RootStore events (zero preloaded target links), without FixtureBuilder, synthetic q authority, forced latent edges, semantic oracle outcomes or changed scientific constants. This tests a narrow operational mechanism, NOT contextual language learning or broad intelligence.

Do not implement I4 Assemblies, I5 owners/probe, I6 hierarchical provenance, I7 generation, cross-modal empirical tests, Replay or production automatic recycling. No merge to main or RC4.5 change. Full I3 remains PARTIAL after P02 until other declared gates pass.

## 1. First resolve P01 production schema restrictions — CHECKPOINT A

Read the actual P01 files and tests before editing. Verified limitations:
- persistence/graph_codec.py rejects W with synapses, outgoing indices and reservations; its schema stores sensory cells and latent topology only.
- graph/production.py sensory birth helper rejects ANY existing base.synapses, which would prevent later training events after first END.
- graph/synapse.py and the I1 FixtureBuilder path require fixture_only=True. Real learned Synapse must have distinctly validated nonfixture origin, accepted root/event provenance and confirmation journal. Retain fixture test compatibility; never convert a fixture object to evidence by toggling its boolean.
- persistence/production_store.py _validate rejects nonempty temporal or synchronous event drives, allows only OPEN/ABORTED, assumes zero completed closes and every H_BEGIN equals the original cold H. Each assumption is false once a real learned link/COMPLETED root exists.
- P01 journal records do not yet constitute a verified positive link witness ledger. Extend event source/final/frontier/provenance records, proposal staging and close checkpoints without reinterpreting read-only/fabricated observations as independent EXTERNAL evidence.

Implement a new explicitly versioned P02 W+root+journal codec, stable full-precision binary64 encoding, real synapse S/E/state/provenance/confirmed roots, root-close serial, canonical outgoing/reverse/resource indices, status and checksum validation. On load rerun existing physical graph invariant audit; prevent fixture-origin graph loading into production. Keep one SQLite durable source of truth and one atomic transaction per BEGIN/EVENT/END/ABORT. If old P01-on-disk schema cannot safely migrate, reject it explicitly as unsupported rather than silently treating it as P02. Preserve P01 test behavior and full scientific integrity.

After a COMPLETED root, the next BEGIN snapshots the H of that completed root, not the initial H. A later ABORT restores its own H_BEGIN exactly, without undoing preceding evidence or H. The first accepted END increments completed external root-close serial exactly once; END itself never consumes an event or K_R quota. Any duplicate END or crashed retry cannot double-credit q/S/E/count or closure serial.

## 2. Trusted external witness and proposal laws — CHECKPOINT B

Production EVENT authority comes only from RootStore with an OPEN genuine external LEARN exposure and canonical actual SIC projection. External is an API provenance claim, not a guarantee of semantic truth. Store immutable physical direct-support witnesses, canonical feature/SIC digest, root ID, contiguous order, global event ID, frozen pre-event W/H, committed-before-event population, Pass1 emitter frontier, final A, actual fresh F_step and HARD_BOUNDARY history.

Direct witnessed input on a newborn cell is NOT OBS_ELIGIBLE in its birth event. Predicted-only, residual-only, spatially completed, replay, read-only and internal-selected activity never provide V_ext. A verified target must be committed before its learning event and actually have direct SIC support and final A_target>=frozen theta_active.

LOCAL Δ0: same event, same region, direct verified source and target, source emitted in frozen Pass1 E^(1), no self link, source and target committed before event; use final A_source(t)*final A_target(t) for creation and q, NOT Pass1 neural A_source. ASSOCIATIVE Δ1: source belongs to previous actual event's frozen F_step within same OPEN exposure with no HARD_BOUNDARY, previously verified source and frozen A_source^+(t-1), current verified direct target and final A_target^+(t); no Δ>1 links. The source may not be first-committed at its source event. Cross-region initial thresholds remain unspecified; do not pretend CROSS is production-ready from LANGUAGE-only tests.

For BOTH, require event-time legal physical D(i,j)=1 from an actual frozen event W, coactivity>=theta_create=.20, valid source/frontier, correct scope/delta, q>0 and exact provenance. Enqueue a typed LINK_PROPOSAL with key/root/event IDs, source and target observation digests, chosen source/target activities, correct q/y, D_event, scope/delta, Pass1/F_step proof, and proposal ordinal. Pending proposal has NO live Q and NO E/S/count before END.

Use existing SIC and I2 numerical kernel, not duplicate invented equations or expected lexical Y labels.

## 3. Full-precision local evidence and canonical winner — CHECKPOINT C

The unchanged RC4.4 numerical laws for true witnessed EXTERNAL LEARN:
- q_raw = A_source_learn * A_target_final * k_evidence(scope) with D_event=1 and omega_root=1.
- k_evidence(LOCAL)=1.0, k_evidence(ASSOCIATIVE)=0.7408182206817179 (one stored binary64 literal); k_neural for propagation=1.0, never discounted by k_evidence.
- y_positive = clip(theta_S + (1-theta_S)*(A_target_final-theta_active_pre)/(1-theta_active_pre),theta_S,1), theta_S=.60.
- initial link: CANDIDATE, S=y, E_ext=min(10,q), E_int=0, external_count=1, true winning root+event, valid deadline.
- later different accepted root: S_new=(E_old*S_old+q*y)/(E_old+q), E_ext_new=min(10,E_ext_old+q), E_int=0 baseline, external_count +1 at most once per root/key. Consolidation iff S>=.60 AND E_total>=3 AND external_count>=2, plus existing structural/time guards. Two independent roots alone are not sufficient.

For each key/root, choose the proposal sorted by (-FULL_BINARY64_q,event_order,proposal_ordinal) and take its PAIRED y. LLA §4.2 does not authorize replacing full-q ordering with Q6. Existing synthetic learning/evidence.py root_max uses -q6(q): test near-ties of two valid q values differing by less than 1e-6 and choose the genuinely larger full-precision q, not arbitrary earliest event. Existing Q6 comparisons elsewhere remain unchanged.

Canonical END arbitration sort: (priority_class,-creation_coactivity,-q,source_cell_id,target_cell_id,scope_order) with ordinary priority=1. Freeze ONE pre-close W, check D_close=1 and D_event=1, both commitment timing rules, correct reserved/live key budget ledger, outgoing <=64 and CROSS <=12. Invalid link-specific proposals receive named refusal and no q/count. All accepted links/outgoing/budgets/ledgers, root completion, current H, close serial and W snapshot must publish atomically in one shadow transaction. Existing link never double counted if a reservation transfers. Negative updates and Replay are OFF.

I4 native Assembly MAINTAIN/FORM and I5 owner resolver are NOT_RUN in this scoped ordinary-learning END, even though future full Core §10.2 includes them; do not fabricate a no-op Assembly/Owner claiming completion.

## 4. Operational from-zero experiment and crash recovery — CHECKPOINT D

Use a new production SQLite database with zero learned synapses, real RootStore events and no fixture mutation. First admit SIC receivers by actual sensory birth event(s). Because newborns cannot learn same-event, follow with independently ordered, lawful external roots. The test harness may inspect physical graph geometry to select a PREDECLARED reproducible feature curriculum, with published candidate list and selection method; it cannot pass learned keys/labels/target identities as privileged learning arguments. If no legal physical pair appears, report exact eligibility/latent/frontier data, not a fabricated edge or retuned threshold.

P02 MUST prove separately:
1. A genuine LOCAL edge created on a real completed root from committed-before-event observed source/target meeting Pass1 emitter and D_event/D_close. Trace physical key, witness digests, q/y, selected proposal, winner, E_ext/S/count and current Q.
2. A genuine ASSOCIATIVE Δ1 edge from prior true ordered event F_step and current genuine observed target inside SAME OPEN root with no boundary. Trace frozen prior A, D, q/y and actual END root.
3. Multiple proposals within ONE root credit at most max q and ONE root count. Across independent completed external roots E_ext and count increase; incomplete and aborted roots do not.
4. Newly learned graph survives save/load with identical directed synapse records and journals, and its Q yields a measured actual read-only neural P_S/P_T effect compared with a declared zero-link or same-state ablation. Inference leaves W/H/root status untouched.
5. Crash injection before/after BEGIN, EVENT, END, ABORT commit returns entire pre/post state, with no split link/H/R, duplicate evidence, repeat event adaptation or root reuse. Later abort never overwrites earlier COMPLETED H.
6. Graph with genuine learned synapse can still accept a later sensory K_new cohort without deleting its learned links or resetting outgoing/latent metadata.

A legitimate EMPIRICAL_BLOCKED outcome does not authorize editing RC4.4, latent topology, SIC, θ_create, normalizer or existing weights.

## 5. Minimum required test matrix

P02-T01 production W codec roundtrip with nonfixture Synapse, all indices and journal; fixture graph still fails production trust.
P02-T02 learned Synapse requires trusted END root; cannot be built by caller SyntheticProposal or FixtureBuilder.
P02-T03 birth event q=0; later direct committed witnesses eligible, no backdated learning.
P02-T04 LOCAL Pass1 E and final/final q; ASSOCIATIVE prior true F_step and prior-frozen final A.
P02-T05 D_event and D_close both valid; stale/released latent fails no credit.
P02-T06 root MAX pairs q with y and full-q near-tie is not converted to Q6.
P02-T07 .8*.6 q_LOCAL=.48; q_ASSOC=.3555927459272246; neural p_ASSOC=.24 when A=.8,Q=.3.
P02-T08 q/creation coactivity >=.20, separate from V_ext; missing direct witness fails.
P02-T09 one complete root/key max one accepted count; ABORT/OPEN/replay/read-only count zero.
P02-T10 initial CANDIDATE and subsequent evidence update; E_ext cap10, E_int baseline zero; S formula exact.
P02-T11 consolidation requires E>=3,S>=.6,roots>=2, no two-root shortcut.
P02-T12 atomic END changes W/record/status/serial/H together; duplicate END cannot double credit.
P02-T13 post-COMPLETE H and graph become next BEGIN base; ABORT restores only new BEGIN H.
P02-T14 learned W snapshot loads in real GraphSnapshot/I2, Q numeric causal test and no inference mutation.
P02-T15 later sensory birth while learned links exist preserves them, and indices audit.
P02-T16 process kill just before/after END and EVENT commits, clean recovery and count idempotency.
P02-T17 from-zero physical LOCAL AND one-step ASSOCIATIVE learning actually executed, or exact EMPIRICAL_BLOCKED with physical trace.
P02-T18 no learned context owner, Native Assembly, generation, Replay or production automatic recycling claims.
P02-T19 preserve all 664 I0–I3 P01 regressions; exact RC4.4 hashes unchanged; Python 3.14 Windows and Ubuntu final-head CI success.
P02-T20 explicit full I3 remaining gates and 57 LLA/LG named tests not automatically passed; no false I3 COMPLETE.

## 6. Execution and report

Perform checkpoints A→B→C→D with full regression at each boundary and at final head. Do NOT attempt broad I3-P03 novelty/recycling work until P02 independently reviewed. Keep modifications limited to production evidence, graph schema, root END and tests. No main merge, no force push, no scientific version change.

Final commands:
python -m pytest -q --basetemp=.pytest-tmp -rs
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m dgca_next verify-specs
python -m pip check
git diff --check
git status --porcelain

Write docs/implementation/I3-P02-LEARNING-END-VERIFICATION-REPORT.md with exact code commits/files, schema hashes, authentic root IDs and source event orders, physical source/target IDs and direct X, real neural E/F, D_event/D_close, max q and paired y, actual produced Synapse S/E/count/Q, rebooted snapshots, before/after read-only causal traces, aborted vs completed H bytes, crash witnesses, test commands and counts, final-head Ubuntu and Windows CI links and SHA, and exact scoped gates.

**Verdict:** I3-P02 REVIEW READY only if production END, LOCAL and ASSOCIATIVE positive learning, actual persistence and causal read-only effect, and all tests PASS. Otherwise I3-P02 PARTIAL / SPEC_BLOCKED / EMPIRICAL_BLOCKED with minimal reproducer and no fictional training results. Full I3 remains PARTIAL until separately accepted. Stop and request independent review; no P03, I4 or main merge.
