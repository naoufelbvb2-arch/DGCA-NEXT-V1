# DGCA NEXT — I4-R00 Independent Readiness Review and Scoped Decision Record

**ID:** I4-R00-READINESS-REVIEW-AND-DECISIONS
**Date:** 2026-10-30
**Status:** READINESS REVIEW COMPLETE; R01 PURE DIAGNOSTICS AUTHORIZED; D01/D02 REMAIN NON-NORMATIVE PENDING R02 APPROVAL
**Working branch:** feature/i4-native-assemblies-design
**Accepted base:** main `88fc596c178c8a89c24b991e280d7a0ca8c07779` (merged PR #4)
**Scientific authority:** Only CORE RC4.4 / LLA RC4.4; both DESIGN CANDIDATES, NOT FROZEN / NOT SCIENTIFICALLY VERIFIED.
**Purpose:** Advance engineering examination without silently deciding Assembly/recycling ordering, legacy journal migration, contextual pin semantics or new scientific values.

## A. Evidence read directly from the merged implementation

- `src/dgca_next/graph/network.py` maintains real production Cell/Synapse/24-slot physical W but no native Assembly registry/high-watermark/reverse member map. `Cell.assembly_ids` is only an administrative frozenset; `graph_codec.py` rejects a production W with nonempty cell assembly_ids. There is no legitimate native Assembly publication path.
- `src/dgca_next/dynamics/attractor.py` contains `AssemblyFixture` and fixture-bound cohesion/Attractor calculations. Those are valuable for isolated numerical checks but are NOT native Assembly provenance.
- `RootStore` I3 END atomically settles learned evidence and optional P04 manually requested physical rewiring, but has no persisted MAINTAIN/GROW/FORM/MERGE/SPLIT stage. No recipient can infer such functionality from a fixture test.
- CORE §2.0 sets a native FORM gate requiring REAL, LIVE, **reciprocal CONSOLIDATED LOCAL** links; in first LANGUAGE lab a three-cell candidate needs SIX directed keys, three unordered reciprocal pairs with `R^B=min(Q_ij,Q_ji)>=.10`, genuine event-time participating emitters and full-population specificity `Spec>=.30`.
- The previously accepted P02 real `a` experiment commits exactly four physical cells [8606,9345,11795,12181]. Root 2 produces 24 accepted LOCAL+ASSOCIATIVE keys from only those committed cells; after roots 2–4 the regression asserts **ALL** learned LOCAL edges in that production run are CONSOLIDATED. This is a **promising candidate triangle feasibility signal**, not a direct test of every reciprocal key, whole-region Spec or native FORM.
- At fixed LOCAL evidence `S=1,E_ext=3` a directed Q=.3; a three-cell reciprocal pair with both keys so qualified has R=.3>.10. **This is a conditional numerical implication, not a claim the full actual triangle was inspected.** R01 must extract exact keys and event witnesses from the production RootStore graph, rather than extrapolate from one displayed example key.
- I3 reports 704 local tests PASS and approved previous CI; none of the native Assembly named LG-T01/LG-T02/LG-T03/LG-T16 end-to-end scenarios are completed.

## B. Decision inventory — no scientific law modification

**D01: same-root END controlled P04 recycling versus native Assembly updates.** Future production root order must satisfy CORE §10.2 (evidence → contextual operations when available → Assembly). The current P04 optional controlled rewiring occurs immediately after evidence, so allowing both on one END would create an unresolved concurrency/order question. **Recommended conservative containment for R02:** an explicit versioned **I4 Assembly-enabled experimental mode** does not permit staging P04 controlled rewiring requests; reject incompatible request BEFORE END, while ordinary no-request END runs Assembly operators. Preserve the previous separate I3 experimental mode where P04 is supported and I4 Assembly updates are disabled. No reroute, no hidden skip of mandated Assembly when enabled, and no retroactive coverage. This is an IMPLEMENTATION SAFETY PROPOSAL, not yet an approved change to Core law or P04 API. R01 read-only inspector has no conflict and requires no decision.

**D02: schema/production database compatibility.** R01 writes ZERO production state and uses existing schema-4 RootStore, so no version change required. For R02, a native Assembly registry needs a new versioned W+root history representation, plausibly schema-5. **Recommend an explicit audited schema-4 → schema-5 migration or verified import path**, including intact learned credits, W wiring, old history, rollback and nonmutating failure; schema-3 remains separately unsupported. If migration is not demonstrated, require an explicit owner decision to allow lab-only fresh schema-5 databases with schema-4 fail-closed rejection. Do not take that fallback automatically; no irreversible destructive replacement.

**D03: stage the operators rather than claim the full Core §2.0 suite at FORM.** **Adopt for task sequencing**: R01 read-only reciprocal physics/qualified witness; R02 native FORM; R03 MAINTAIN/GROW; R04 MERGE/SPLIT. Full I4 cannot be CLOSED until Core §2.0 scope is implemented and tested, with exact deferred status on any missing operator. This changes no RC4.4 equation.

**D04: Attractor is a dependent, later subgate.** **Adopt for sequencing**: R05 only after live native Assembly identity+generation are proven in production. Before then I2's `AssemblyFixture` cannot count as native Attractor. Native Attractor may be separated into cognition later only by a new scoped owner decision; do not silently upgrade fixture transitions.

**R01 authorization boundary:** implementing pure read-only reciprocal and event-qualified FORM-eligibility inspectors plus instrumentation is permissible with D01/D02 unresolved, because it does NOT write Assembly identities, change END, alter W/H/R or imply any new law. R02 MUST NOT start before a targeted approval of D01/D02 and its production schema and transaction design.

## C. Engineering proof obligations to collect with R01

1. The actual saved post-root-4 production W has or lacks all six directed CONSOLIDATED LOCAL records for candidate triangle (8606,9345,11795); list each key, state, S/E/count/Q and structural D, not just one example.
2. Enumerate qualified triangles from the *actual* committed graph, not a fixture; use finite physical reciprocal adjacency and exact `R^B`, `d,D,Spec`, including all external reciprocal neighbors in the specificity denominator.
3. Recover the event-frozen source/frontier and final A for the same genuine accepted root/event, and prove each triangle member committed BEFORE that EVENT, with actual external witnessed legal participation and `A^+>=theta_emit`. DO NOT apply post-close H thresholds or post-close inferred emitter tags as if they were event-time observations.
4. Compute the deterministic lexical-first FORM seed and `K_FORM_PER_END=12` bounded projected eligible sets as **read-only hypothetical decisions**. An eligible decision is NOT an Assembly birth, does not allocate AssemblyID or modify cells.
5. Independently demonstrate REAL negative outcomes: only one directional LOCAL edge; reciprocal CANDIDATE/EPISODIC; low Q; loss of event witness; no committed-before-event source; Spec diluted by additional real reciprocal neighbors; no triangle. Negative tests may use isolated constructed W for pure numeric operators, but label them COMPONENT, never production native FORM.
6. Instrument empty-graph and 4-cell positive curriculum cost. If exact six-link triangle cannot form due to physical geometry, record source/target D, K_R, PASS1/F_step, q/y, root counts and reason. Do not fake reciprocal links or lower thresholds.

## D. Readiness outcome

**I4-R00 ACCEPTED for READINESS/SCOPED R01 EXPERIMENT DESIGN; not native Assembly implementation acceptance.** R01 read-only inspection may proceed under existing CORE/LLA RC4.4 without D01/D02 changes. Native FORM, versioned Assembly storage and same-END ordering remain pending R02 authorization. I3 production source remains untouched; all accepted I3 regression and evidence laws remain mandatory.

**Next artifact:** I4-R01 pure reciprocal-structure/FORM-readiness implementation contract, with FULL/COMPONENT/NOT_RUN accounting and hard NO_RECIPROCAL_TRIANGLE refusal.
