# DGCA NEXT — I4 Native Assemblies Scientific & Engineering Readiness Design

**Document ID:** I4-R00-SCIENTIFIC-ENGINEERING-READINESS-DESIGN
**Revision:** PROPOSAL-R01 — 2026-10-30
**Status:** DESIGN PROPOSAL / NOT FROZEN / NOT CODE EXECUTION AUTHORIZATION
**Repository:** naoufelbvb2-arch/DGCA-NEXT-V1
**Design-only branch:** feature/i4-native-assemblies-design
**I3 accepted and merged baseline:** main `88fc596c178c8a89c24b991e280d7a0ca8c07779` (PR #4)
**Authoritative scientific sources:** EXACTLY docs/specs/DGCA_CORE_RC4_4.md and docs/specs/DGCA_LLA_RC4_4.md. Both are DESIGN CANDIDATES, not scientifically frozen/empirically verified.
**Last independently verified I3:** 704 local tests reported, CI success on previous accepted code and PR #4 final head; no local tests independently rerun by reviewer. Do not call I4 implemented.

## A. Mission — one scientific claim at a time

**I4 objective:** Test whether physically learned, bidirectionally consolidated *LOCAL* synapses can produce **native, identity-bearing, reusable LANGUAGE Assemblies** entirely from actual W, genuine root/event observations, deterministic RC4.4 Assembly operators and atomic END, without pre-injected fixture assemblies or semantic labels.

The first falsifiable outcome is narrower than language or generation:

**Cold external-language exposure → ordinary cells and six separately legal directed LOCAL links among three committed cells → enough independent external evidence to CONSOLIDATE each of six edges → actual reciprocal physical triangle with R^B>=.10 on each pair → valid real qualified fresh emitters → a new live size-3 Assembly at a completed root END → same ID and generation after cold reload → no retroactive birth-root outbox attestation.**

If such a physical triangle cannot form, the report MUST say NO_RECIPROCAL_TRIANGLE with physical IDs, attempted directed links, D, q/E/S/roots, and emission/coverage/Spec witnesses. The program MAY predeclare a curriculum after inspecting canonical SIC geometry, but cannot add expected links, force reciprocity, shift constants, use FixtureBuilder, invent Assembly membership or inject labels into Core to force formation.

**Out of I4 initial acceptance:** contextual z owners/role binding, higher-order composition, multimodal Assemblies, lexical surface/readout attestation, peripheral outbox integration, generative text, G1–G3, Replay, automatic recycling and improved cognition claims. Existing RC4.4 has further laws for these, but law definition is not execution proof. Treat Attractor as a **separate dependent subgate** only after authentic live Assembly existence; do not silently substitute fixture Assembly.

## B. Exact inherited Assembly laws (no new mathematics)

Source: CORE RC4.4 §§1.2,1.4,2.0–2.1,10.2,12.1; LLA RC4.4 §§2,7,8.2–8.3.

1. Physical W: 12,288 addressable cells, LANGUAGE region capacity 4,096, 512 microcolumns × 8; a cell has no word/context/semantic task role. Assembly is a **distinct structural W object**, not a cell, not a contextual z and not a hidden semantic label. The administrative Cell.assembly_ids is a bounded membership back-reference, not an encoded concept.
2. Assembly identity: unique monotonic per-region AssemblyID never reused; region LANGUAGE only in first lab; sorted unique members, LIVE/ARCHIVED, structural_generation, birth_close_serial, last_mutation_close_serial, last_merge_split_close_serial and audited reverse membership indices. Membership cap M_max=12 per cell, size 3–16.
3. Structural support is ONLY **two directed live CONSOLIDATED LOCAL** synapses for each first-lab reciprocal pair. For u≠v, R^B_uv = min(Q^LOCAL_uv,Q^LOCAL_vu) in LANGUAGE; Q = d*S*E_total/10 per real current W. Neither ASSOCIATIVE nor staged, fixture-only, CANDIDATE or EPISODIC_INDEXED links count toward Assembly structure. Require pair edge R^B>=theta_A=.10. For a 3-cell triangle, all 3 unordered pairs and therefore all 6 directions must be lawfully consolidated and live.
4. For Assembly A, degree d(x,A) counts valid reciprocal edges, D(x,A)=d/(|A|-1). Specificity Spec(x,A)=sum of R^B_xj for j in A\{x} divided by sum R^B_xk across ALL physical committed reciprocal neighbors in LANGUAGE (0 if no valid denominator). Do not compute specificity against only the candidate triangle. FORM requires each triangle member d=2, D>=.70, Spec>=.30 and correctly qualified participation in an actual root event.
5. K_min=3,K_max=16,d_min=2,rho_core=.70,rho_G=.50,sigma_G=.30,rho_keep=.35,sigma_keep=.20,theta_A=.10; K_FORM_PER_END=12 for all events of one completed root. No hidden override.
6. Core §2.0 specifies deterministic one-pass END stages **MAINTAIN → GROW → FORM → MERGE/SPLIT** on post-synaptic-evidence W*, after any lawful owner/candidate resolution. MAINTAIN removes lowest-ID violators and archives subminimum Assembly; GROW bounded reciprocal-neighbor enumeration and sorted rank; FORM event_order and lexicographic seeded triangles; MERGE by Jaccard>=.70, between strength>=.40, 200 completed-event cooldown; SPLIT for size>=6, all cross-pair support<=.15, cross-mean<.10, same 200 cooldown. No iterate-until-convergence.
7. FORM emits genuine event-time physically committed-before-event and externally witnessed, sufficiently emitting cells; use the completed root's actual frozen event A^+, frontiers, X and witness origin and **post-evidence W*** for structural links; do NOT claim Assembly existed in the root's prior events or grant it historical peripheral confirmations.
8. Fresh-only Attractor admission for an **already pre-existing qualified Assembly** is distinct from FORM: scratch fresh pass with previous activity, temporal prediction, sigma and bootstrap = 0; fresh average >=.40 AND weighted fresh reciprocal cohesion >=.50; gain from C_G only next event. A newly FORM-ed Assembly cannot retroactively host a prior event's Attractor. Its state is runtime R, not semantic W content.
9. Native Assembly test names LG-T01, LG-T02, LG-T03, LG-T16 are the primary I4 acceptance/falsification contracts; LG-T09 is downstream peripheral attestation, not itself a native structural formation proof. Do not claim all 57 prior named tests PASS.
10. The Core definition includes cross-modal support mathematically but only same-LANGUAGE reciprocal CONSOLIDATED LOCAL links are enabled for formation in this first laboratory. Leave AUDIO/VISION initialization unaltered and fail closed on unsupported formation.

## C. Verified current implementation barriers after accepted I3

**C01 — no production Assembly storage:** src/dgca_next/graph/network.py _State has no Assembly registry, Assembly counter/high watermark, reverse membership map or versioned generation. Cell.assembly_ids exists in the Cell type, but src/dgca_next/persistence/graph_codec.py explicitly rejects any nonempty production cell.assembly_ids; only fixture _Editor.set_memberships exists. I4 needs a new audited internal-only atomic W writer and versioned codec, **not** fixture reuse.

**C02 — I2 Assembly and Attractor are fixture-only:** src/dgca_next/dynamics/attractor.py defines AssemblyFixture and numeric fresh cohesion validated against fixture graph identity/generation. Never relabel this type as native. Reuse pure numerical operators only behind correctly typed authentic production identity, generation and graph proof. Native formation must consume genuine learned W, not pre-built triangles.

**C03 — RootStore END only settles synaptic evidence and optional P04 controlled rewiring:** src/dgca_next/persistence/production_store.py currently executes _settle, then optional _rewire_at_end, then root commit; no Assembly stage or membership journal. Core §10.2 requires the future Assembly operators in the same END transaction. A new W snapshot version must preserve I3 learned synapses, evidence, topology and root replay audit, plus exact before/after Assembly registry.

**C04 — identity and lifetime safety:** IDs must not be reused on archive/restart/ABORT; structural_generation increments on membership edits and invalidates any later attestation tied to old generation. Avoid storing Assembly semantics inside cells or replacing Synapse state with an Assembly flag. Persist per-region counter and LIVE/ARCHIVED records under canonical deterministic enumeration with hash/version checks and membership inverse indexes.

**C05 — contextual pin and reserved-key production support remains unverified:** I3 schema-4 W rejects persisted protected slots or pin owners and does not exercise production owner registry. For first-I4 uncontextualized language Assembly tests, keep owner/pins disabled and fail closed on unsupported records. Before I5 can recruit a z or protect a contextual candidate, require a separate reviewed production capability, not a silent I4 stub.

**C06 — I3 append-only event W snapshots and full historic replay load cost:** baseline at ~100 roots had ~14.1 MB SQLite and ~47s cold open with full audit in one bounded traced run. Native Assembly registry will add history and replay work; track 1/10/100+ root growth and avoid a new global quadratic graph scan, but do not silently weaken forensic integrity or retrofit unapproved database compaction in I4.

**C07 — protocol contradiction/decision to resolve before implementation:** Core §10.2 places Assembly stage after evidence AND contextual-owner resolution. P04's already implemented optional manual rewiring occurs immediately after evidence. Which resulting W does Assembly MAINTAIN/FORM see on the same END when controlled rewiring was requested? Read-only P03 eligibility is not permission. Two safe candidate integrations: (A) disallow an I4 Assembly-mutating END with simultaneous P04 manual rewiring (explicit fail-closed conflict until separate law review), or (B) adopt an explicitly approved deterministic ordering that re-evaluates and protects live Assembly memberships after rewiring before any FORM, with full atomic rollback tests. **NO default selection is authorized by this proposal.** This is an integration sequencing question, not license to modify Core RC4.4 silently.

**C08 — event-time qualification and fresh proof:** Stored P02 observation includes direct X_fixed, pass1 emitters, final A, F_step, source digests, per-event W/H and root status; qualify each FORM member from original event and at exact event-time theta_emit, not from post-END regenerated activity. Distinguish existing true external support from future derived-external context (not implemented in I4).

## D. Proposed engineering architecture, not a new neural law

**Source-of-truth W extension:** immutable AssemblyRecord with AssemblyID/region/members/generation/birth/update/cooldown/status; region high-watermark counters, inverse member_cell→AssemblyID set and canonical audit/transition checks. Cell.assembly_ids mirrors the separate Assembly registry and must be checked bidirectionally.

**Pure operators:** graph/assembly_support.py for calculated consolidated reciprocal Q matrix, finite neighborhood candidates and d/D/Spec; graph/assembly_operators.py for MAINTAIN/GROW/FORM/MERGE/SPLIT consuming immutable frozen W* and verified event snapshots. These are pure deterministic shadow-state transformations with named negative reasons, no fixture privileges.

**Trusted publication boundary:** learning/production_assembly.py binds proposal/acceptance to real RootStore root-close authority and existing event journal; persistence/assembly_codec.py adds versioned canonical record serialization. RootStore END invokes one ordered Assembly phase on a shadow AFTER ordinary link settlement and any separate approved owner step; all membership/index/counter/recycle protections and completed root publish in one SQLite transaction. Cold journal replay must reconstruct identical after-W and close result WITHOUT granting a second independent root, event or retroactive confirmation.

**Identity / audit:** inherited RootStore schema-4 W records not arbitrarily reinterpreted. Either explicit version-migration path with real legacy fixtures and rollback, or separate exact unsupported-schema diagnostic; W W-history remains append-only/integrity-checked. All legal existing I3 operations (including post-I3 read-only, novelty, END and P04 when no conflicting Assembly edit) must retain their numeric and journal semantics.

**Attractor integration:** keep optional until there is a real LIVE pre-existing Assembly at event start. Use a new verified native Assembly view and frozen generation; external input only; R_cold and boundary semantics; no synthetic attachment to a freshly formed generation.

**Research-only instrumentation:** record graph reachability, six directed keys, opposite-direction Q values, per-link D_event/D_close, direct verified emitters, event-time theta_emit, candidate triangles, Spec denominator, coverage, Assembly birth/end, true independent root ages and generation changes. No normative labels hidden in W.

## E. Proposed milestone sequence and strict gates

**I4-R00 — Readiness + interface design, NOT IMPLEMENTATION:** audit Core §2.0 and actual source, map state/codec/END sequencing, test reachability of ≥1 physically legal triangle on cold I3 W. Produce an approved design decision for C07 same-END recycling/Assembly interaction; choose versioned schema strategy and record precise treatment of prior schema-3/4 DBs. No science freeze.

**I4-R01 — Pure reciprocal structure and qualification:** independent deterministic reads from real production W, quality R^B, d/D/Spec and triangle enumeration, negative case with unidirectional, candidate, insufficient Q and missing genuine witness. No Assembly births or registry commits. Success: physics/eligibility are measured from learned links, never fixture-memberships.

**I4-R02 — Production Assembly registry and FORM:** canonical identity, monotonic IDs, reversible index and shadow codec; one real root's legal six-link triangle, qualified true emitter set, deterministic size-3 FORM at atomic END with cold save/load; no same-birth event attestation. This is the PRIMARY scientific gate. If actual triangle cannot emerge, stop EMPIRICAL_BLOCKED with complete six-edge/root tracing instead of prewired physical links.

**I4-R03 — MAINTAIN and GROW:** follow Core exact sorted removal/neighbor ranking, 3–16 and per-cell membership max; membership edits increment generation, archive invalid subminimum without deleting synapses; no root-counter/evidence drift, safe reverse-index restore and crash consistency.

**I4-R04 — MERGE/SPLIT + cooldown:** legal first-lab pairs, Jaccard/strength, deterministic bounded bipartition, no ID reuse; 200 completed-external-event cooldown, duplicate END cannot double mutate. Report when high thresholds make actual merge/split physically unreachable; fixture component tests alone are not a native empirical pass.

**I4-R05 — Native Attractor fresh admission (dependent milestone):** only if independently approved I4 scope includes Attractor. Bind real Assembly ID/generation to frozen event; fresh mean, weighted reciprocal cohesion, boundary/error/age and next-event sigma. If deferred to later cognition, mark NOT_RUN and keep fixture I2 transition isolated.

**I4-R06 — Final integrated/forensic gate:** fresh production root history: I3 cell birth → independently consolidated reciprocal triangle → native FORM → persisted repeated no-change/changed generation and negative cases → read-only immutability, crash/recovery/cold proof; LLA/LG named-test matrix + perf/stress analysis. No readout/generation claim. Preserve I3 accepted 704 regressions and exact CORE/LLA SHA-256, Ruff/format/mypy/dependency/integrity and final-head Ubuntu+Windows CI.

## F. Mandatory falsification observations and success criteria

**Primary LG-T01**: one actual production triangle, 3 committed-before-event cells, all SIX independently legitimate directed LOCAL keys CONSOLIDATED and current R^B>=.10, event-time external grounded emitters, non-duplicate deterministic ID/generation, persisted LIVE Assembly size3, inverse index and replay audit; no fixture source.

**LG-T02**: a held-out actual production graph with only one direction or CANDIDATE/EPISODIC reciprocal links creates zero Assemblies. No legal link/evidence manufactured to pass.
**LG-T03**: a real Assembly structural generation change invalidates prior generation-dependent external attestation/outbox eligibility; IDs never reused after archive/split or cold restart. A peripheral surface ledger is not required to claim native structural logic; do not claim full ledger LG-T03 without executing it.
**LG-T16**: measure physical independent-root budget for all SIX directed edges and attestation readiness; do not infer a native surface/G1 PASS merely from the existence of a triangle. Historic 15/9/7/5 idealized post-commitment link-root counts depend on observed A and eligibility. If no legal reciprocal triangle exists, report NO_RECIPROCAL_TRIANGLE, not fabricated readout.

**Crash controls:** malformed transaction, process-kill before/after END, ABORT in root with qualified but unpublished Assembly, dual independent replay, forged root or fixture Assembly, corruption of membership or counter, unsupported previous schema, same-end/manual-recycle conflict resolution explicit.
**Scopes to preserve:** P02 E/S/count and independent root semantics, P03 novelty provenance and W_conf=100, P04 live synapse and bilateral protections, I3 H BEGIN rollback, read-only no W/H/Assembly mutation.
**Resource gates:** local adjacency-based enumeration only for FORM/GROW, finite splitting size<=16, at most K_FORM_PER_END=12, per-cell membership<=12, no 4096-wide triple loop; document time/memory/DB growth and cold validation overhead without inventing fixed performance thresholds.

## G. Decisions needed before an implementation contract is FROZEN

**I4-D01 — same-END coexistence:** select the approved legal relative order, or fail-closed mutual-exclusion of P04 controlled recycling and I4 Assembly mutation, preserving Core §10.2 and no retroactive witness.
**I4-D02 — schema/version compatibility:** authorize a canonical Assembly-capable W/SQLite schema transition, and whether schema-4 historical production DBs must migrate or explicitly fail closed. This is a data/engineering decision (scientific source unchanged).
**I4-D03 — first I4 acceptance boundary:** initially FORM-only actual empirical test with MAINTAIN/GROW/MERGE/SPLIT incrementally, or insist on all §2.0 operators at once; recommendation is staged gates with full §2.0 acceptance before final closure.
**I4-D04 — Attractor deliverable boundary:** dependent native Attractor conversion within I4, versus later cognition, without claiming a synthetic fixture transition is genuine.

**Suggested owner approval position:** first approve R00/readiness and these decisions, THEN write a narrowly scoped I4-R01 implementation contract. No source-code changes or main merge are authorized by this design document.

## H. Exit deliverable

A future I4 readiness review must include the exact current main SHA, source SHA-256 hashes, physical triangle feasibility/candidate traces from genuine learned I3 W, preferred D01–D04 outcomes, W/ledger migration matrix, dependency map, targeted test cases LG-T01/T02/T03/T16, and the named authorizing engineering contract. Until then, status remains **I4 DESIGN IN PROGRESS; NATIVE ASSEMBLY FORMATION NOT RUN**.
