# DGCA NEXT — I4-R01 Real Reciprocal Structure & FORM Eligibility Contract

**Document ID:** I4-R01-RECIPROCAL-STRUCTURE-IMPLEMENTATION-CONTRACT
**Revision:** R01 — 2026-10-30
**Status:** AUTHORIZED FOR CODEX IMPLEMENTATION — PURE READ-ONLY INVESTIGATION ONLY; NOT VERIFIED
**Repository/branch:** naoufelbvb2-arch/DGCA-NEXT-V1 / feature/i4-native-assemblies-design
**Accepted I3 main baseline:** 88fc596c178c8a89c24b991e280d7a0ca8c07779
**Preflight decisions:** docs/design/I4-R00-READINESS-REVIEW-AND-DECISIONS.md
**Original design:** docs/design/I4-R00-SCIENTIFIC-ENGINEERING-READINESS-DESIGN.md
**Only normative scientific sources:** docs/specs/DGCA_CORE_RC4_4.md and DGCA_LLA_RC4_4.md; both DESIGN CANDIDATES, NOT FROZEN / NOT EMPIRICALLY VERIFIED.

## 0. Exactly ONE investigation, NO native FORM publication

Implement a **pure, deterministic, read-only reciprocal LOCAL structural analyzer** and a RootStore-authenticated event-qualification INSPECTOR for the Core RC4.4 §2.0 future FORM operation.

At the end of R01, execute one real cold production RootStore curriculum and output a reproducible, real physical triangle/no-triangle trace. The key question is whether genuine I3 learning and actual observation produce the precise **preconditions** of a first Native Assembly: six separate directed live CONSOLIDATED LOCAL edges among three committed cells; three reciprocal physical edges `R^B>=.10`; correct d/D/Spec; witnessed event-time emitters from the same root; deterministic first triangle under Core's event-order/lexicographic policy.

**Forbidden in R01:** create AssemblyRecord, allocate AssemblyID, write Cell.assembly_ids, start native assembly registry, alter graph_codec, rewrite RootStore END, change W/H/R/evidence/journal/schema, enable periodic recycling, create new owner/pin/reservation state, copy AssemblyFixture as a production Assembly, change thresholds, edit either scientific source, or claim actual FORM/readout/Attractor/generation. Do not merge into main. Exit with I4-R01 REVIEW READY or a truthful PARTIAL/EMPIRICAL_BLOCKED trace.

Pure component tests may construct small synthetic graphs solely for falsification arithmetic and MUST label them COMPONENT, never production formation.

## 1. Exact existing scientific mathematics

**Physical directed support.** For first LANGUAGE lab:
- A directed LOCAL key i→j counts for structural support only if it is a lawful current W synapse, `state=CONSOLIDATED`, committed LANGUAGE endpoints, no self-link, legal physical D(i,j), current live Q_ij calculated from stored actual S,E_ext,E_int,d and Core Q formula. `ASSOCIATIVE`, `CROSS_TERRITORY` (first-language formation), `CANDIDATE`, `EPISODIC_INDEXED`, fixture-only, pending root proposals and zero-Q do NOT count.
- For unordered i<j: `R^B_ij=min(Q^LOCAL_ij,Q^LOCAL_ji)` only if BOTH directed keys qualify; otherwise zero. Reciprocal physical edge exists iff `R^B_ij>=theta_A=.10`.
- For candidate A={a,b,c}: `d(x,A)=number of reciprocal eligible neighbors among A\{x}`; `D(x,A)=d(x,A)/(|A|-1)`; `Spec(x,A)=sum_{j in A\{x}} R^B_xj / sum_{k in N_rec(x)} R^B_xk`, with denominator over **all committed live reciprocal neighbors in the whole LANGUAGE region**, not only A. Zero denominator ⇒ Spec=0.
- FORM checks `d>=2, D>=rho_core=.70, Spec>=sigma_G=.30` for each of 3 nodes, `R^B>=.10` per pair, `M_max=12` membership headroom, genuine RootStore event, pre-event committed cells with legal externally grounded event participation, `A^+_i(t)>=theta_emit(t)` at the **event-frozen** threshold. If an implementation gate identifies other explicit Core §2.0 constraints, apply them without inventing new defaults.
- Exclude cells already covered by a pre-existing LIVE Assembly with CoreCoverage>=.70, but in R01 the **current real production W has no native Assemblies**. Do not represent fake Assembly objects to test this in production. Test the covered case as separate pure-component data only if lawful.
- Enumerate candidate triangles using sorted adjacency set intersection, lexicographically `i<j<k` and event-order first; no scanning combinations over the entire 4096 LANGUAGE space. At most `K_FORM_PER_END=12` *projected* FORM seeds per prospective END, with disjoint seed vertices and no allocation/side effects.

**Critical timing:** compute reciprocal support from the **post-synapse-evidence W*** at the same genuine completed external root END; event qualification comes from its stored PRE-END genuine EVENT snapshot(s). A later graph with additional synapses is NOT proof that an Assembly was FORM-eligible at an earlier END. Freshly formed assemblies cannot inherit earlier event attestations (there are no assemblies or attestation ledger in R01).

## 2. Required data origin and read-only API

Source actual production snapshots through `RootStore`, e.g., in a private inspection wrapper:
- run authentic `RootStore.begin / event / end`, existing production SIC + I2; obtain saved post-close W and all original event witnesses.
- Use the root's immutable event journal and post-evidence W that was *actually available at that close*; verify root COMPLETED, `EVENT` external LEARN, exact root/event order, original commitment time and event-frozen H threshold. Do not issue a fake event, infer witnesses from read-only neural traces, or use a later root's W.
- Reader cannot accept caller-supplied `is_verified`, synthetic link objects or postprocessed `A` as trusted origin. It may expose an immutable diagnostic result, keyed to source W hash / event digest, but MUST NOT return a mutation capability.
- If stored event records lack sufficient verified per-cell final A, F_step, commit timing or theta_emit, return `UNVERIFIED_FORM_EVENT` with the missing field: DO NOT silently assume qualification from source X alone.
- The original graph has no native Assembly records and no production persisted pin/reservation support; R01 must treat this exactly, not fabricate registry/counters/memberships.
- Before and after any inspection, compare exact durable W/H bytes, root status/counters, source graph, accepted credit count, per-key evidence, last journal event and archive digest; inspection is immutable on new and cold-reloaded stores.

Implementation should be the minimum: pure `graph/assembly_support.py` or `research/assembly_inspector.py`, immutable `ReciprocalPairDiagnostic`, `TriangleDiagnostic`, `FormEligibilityDiagnostic` and RootStore read-only verified context. Reuse `graph.synapse.quality` and existing physical graph audit, do not duplicate numeric Q. Avoid adding any permanent public setter or a parallel source of truth.

## 3. Mandatory measured root experiment: candidate `a`

Start with a NEW schema-4 production DB, zero committed cells and zero learned synapses. Use official `RootStore` feature `(("a","1"),)` only:
- Root 1: actual event 0 should commit [8606,9345,11795,12181]; no learned positive link.
- Roots 2,3,4: actual independently completed external roots, each with two ordered `a` feature events. Inspect all LOCAL directed keys after each END (not just example 8606→9345), their origin, q/root credit, S/E/state/Q and all legal structural D.
- At post-root-4 W, inspect the lexicographically first three cells **8606,9345,11795**. Emit the actual six ordered directed LOCAL edges (or explicit missing/invalid reasons), three reciprocal `R^B`, each cell's d/D/Spec with entire actual LANGUAGE reciprocal neighborhood denominator.
- Inspect the real qualifying event(s) in root 4 for all three cells: actual external x support, committed-before-event proof, final A, threshold `theta_emit`, emitter/eligible witnessed origin, event id/order, post-close W evidence compatibility.
- Enumerate all legal size-3 triangles in the actual four-cell W and return the FIRST hypothetically FORM-eligible seed, respecting Core's actual event order and deterministic sorting. Store a diagnostic report only; do not allocate AssemblyID or touch W.
- On a NEW RootStore reopen (same DB), calculate the identical immutable diagnostic. Snapshot verification must prove no data mutation.

**Do not assert up front that four same-feature cells guarantee a reciprocal triangle.** Prior I3 P02 report shows 24 physical links and all LOCAL consolidation, which is a promising preflight; the new experiment must prove exact six keys, R, Spec and event-time eligibility independently. If no legal seed exists return `NO_RECIPROCAL_TRIANGLE` or `NO_QUALIFIED_FORM_EVENT` with the full measured witness/graph details. That is a legitimate scientific constraint rather than permission to force formation.

## 4. Falsification and hard acceptance gates

**R01-T01** one-sided consolidated LOCAL i→j but missing reverse produces R=0; no reciprocal edge.
**R01-T02** both directions but one only CANDIDATE or EPISODIC_INDEXED produces zero reciprocal support; never treat potential future consolidation as current W.
**R01-T03** both consolidated but Q reverse below .10 produces R<.10, edge absent; exact equality .10 qualifies using real binary64 arithmetic and declared comparison precision.
**R01-T04** ASSOCIATIVE contribution cannot bootstrap LOCAL triangle or create structural reciprocity.
**R01-T05** whole-region denominator: additional real external reciprocal neighbor dilutes Spec; compare known three-neighbor values to an actual graph.
**R01-T06** empty/invalid/fixture-only/uncommitted endpoints or self pair fail closed; missing evidence/illegal physical D cannot become an Assembly edge.
**R01-T07** true RootStore cold a birth cannot provide same-event candidate FORM qualification; pre-event commitment strict.
**R01-T08** actual post-root-4 graph extraction prints all six real LOCAL links for selected triangle with real S/E/credits/Q/D, or their exact missing reasons.
**R01-T09** event-time eligibility for root 4 requires qualified direct external witness, pre-event commitment, final A^+ and event-frozen theta_emit; reject predicted-only/future-born/replay/READ_ONLY/ABORT/mismatched identity.
**R01-T10** no event replay/recompute using current or later W to fabricate a previous END-eligible triangle; enforce exact root-close post-evidence snapshot.
**R01-T11** ordered triangle enumeration and bounded K_FORM_PER_END=12, disjoint seeds; no global choose(4096,3) scan, stable across unordered map/iteration.
**R01-T12** empty/truncated event witness yields `UNVERIFIED_FORM_EVENT`, not guessed value.
**R01-T13** read-only inspection before/after on a genuine persisted W keeps all W/H/root/event/budgets/evidence byte identical; separate cold reopen and repeat produces same results.
**R01-T14** an eventual FORM-ready diagnostic is NOT an Assembly birth, never allocates ID, changes Cell.assembly_ids or writes journal/codec; no phantom native Attractor or surface attestation.
**R01-T15** experimental report clearly labels actual real physical trace vs fixture-based arithmetic negatives, with reproduced SIC input, independent root ID, all 6 links, R^B,d,D,Spec,A/theta, and root/event relation; report positive OR measured refusal.
**R01-T16** baseline 704 I0–I3 tests PASS (plus R01), RC4.4 scientific SHA-256 unchanged, Ruff check/format, mypy, verify-specs, pip check, diff check; final-head GitHub CI both Windows+Ubuntu SUCCESS.

### Acceptance gates

**R01-G01:** purely actual audited REAL production W for all reciprocal six directed keys, no fixture links in positive trial.
**R01-G02:** exact physical R^B and structural eligibility/d/D/full-region Spec measured, numeric negative tests.
**R01-G03:** authentic RootStore committed-before-event and event-frozen direct/synaptic emitter witnesses, not later root inference.
**R01-G04:** deterministic event-order triangle ranking, disjoint bounded seeds and no global enumeration.
**R01-G05:** source and output records immutable; zero W/H/root/evidence/status drift across inspection and reload.
**R01-G06:** exact positive or negative empirical report: if no legal triangle, transparent per-edge failure with no forced assembly.
**R01-G07:** preserve 704 regressions, source integrity, lint/type/dependencies and final-head Windows/Ubuntu CI.
**R01-G08:** source-traceable review report and explicit status of D01/D02 unresolved for R02.

**Verdict** `I4-R01 REVIEW READY` only if all R01 gates pass AND true observed first-lab FORM eligibility is actually measured (without publishing an Assembly). If the legitimate real geometry produces no eligible triangle, report `I4-R01 EMPIRICAL_BLOCKED` with physical trace; pure operator tests may still PASS separately. If event/witness data unavailable, report `SPEC_BLOCKED/IMPLEMENTATION_BLOCKED`, not a synthetic positive.

## 5. Execution, report and restrictions

**Step 1:** pure structural support and negative numeric tests. **Step 2:** RootStore read-only event/close provenance binding with strict identity checks. **Step 3:** real cold roots 1–4 as above and derived triangle/eligibility trace. **Step 4:** independent cold store, no-mutation and full suite/CI verification.

Create `docs/implementation/I4-R01-RECIPROCAL-STRUCTURE-VERIFICATION-REPORT.md` with:
- exact changed files, commits, Python/runtime and source hashes, clear synthetic-vs-production evidence categories;
- full cold real root script and six directed links key→(state,S,E_ext,E_int,external_count,Q,D,credits);
- actual triangle pair R^B, total reciprocal neighbor sets, per-cell d/D/Spec and Core thresholds;
- actual event IDs/root IDs, direct SIC X_fixed, final A, theta_emit frozen and committed-before-event witness, proposed FORM seed and all rejected alternatives;
- source W post-evidence checkpoint hashes and read-only before/after bytes, cold reload and replay integrity;
- full R01-T01..T16, G01..G08 dispositions, time/memory/DB-size diagnostics and final-head Windows+Ubuntu CI tied to exact delivered SHA;
- next R02 prerequisites: approval of I4-D01 coexistence, I4-D02 versioned production W migration policy; NO Assembly objects/births in R01.

Preserve all previous behavior and return no mutated W:
`python -m pytest -q --basetemp=.pytest-tmp -rs`;
`python -m ruff check .`;
`python -m ruff format --check .`;
`python -m mypy`;
`python -m dgca_next verify-specs`;
`python -m pip check`;
`git diff --check`, `git status --porcelain`.

**Governance:** feature/i4-native-assemblies-design only, no main merge, no official native Assembly creation, no I4-R02, no science-version migration or automatic recycling, no unapproved context/owner/readout/generation. Stop with exact R01 review bundle and ask independent review.
