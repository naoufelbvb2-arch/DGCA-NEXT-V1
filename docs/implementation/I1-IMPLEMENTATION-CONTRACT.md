> Historical RC4.1 artifact. L01 used RC4.2; current authorities are `docs/specs/DGCA_CORE_RC4_3.md` and `docs/specs/DGCA_LLA_RC4_3.md`. Historical paths/results remain reproducible at their recorded commits. See `I1-L01-SOURCE-MIGRATION.md` and the approved I2 S01–S03 execution contract.

# DGCA NEXT — I1 Graph Anatomy Implementation Contract

**Document ID:** I1-IMPLEMENTATION-CONTRACT
**Revision:** R01 / engineering execution contract
**Date:** 2026-10-27
**Base:** merged I0 main at `fdcd3ea3c85b9c7484e89d043188a59d49907b71`
**Target branch:** `feature/i1-graph-anatomy`
**Status:** AUTHORIZED FOR I1 IMPLEMENTATION; scientific RC4.1 remains NOT FROZEN / NOT EMPIRICALLY VERIFIED.

## 0. Sources and boundaries

Read these exact sources before code:

- `docs/specs/DGCA_CORE_RC4_1.md`: §1.1–1.4 anatomy; §2.0 only membership bookkeeping bounds; §4 W/R/H boundaries; §7.3 contextual slot reservation requirements; §10.2 capacity/atomic shadow semantics; §12 numerical registry.
- `docs/specs/DGCA_LLA_RC4_1.md`: §4.4 lifetime states; §5 link-admission interface (do not implement it); §6.2 source capacity/pin constraints.
- `docs/specs/SOURCE-MANIFEST.md` and the already accepted I0 contracts/types.
- `docs/implementation/I0-VERIFICATION-REPORT.md` for the existing baseline 163 tests.

**Two and only two scientific normative specs.** This I1 implementation document is non-normative. Scientific ambiguity MUST be reported; do not invent a latent-cell policy, learning law, numeric threshold, or semantic role. Do not edit specifications or their hashes. Do not touch DGCA or DGCA LITE.

The I1 goal is a *real sparse, deterministic, memory-safe physical graph*; NO claimed learning, SIC activation, contextual memory, actual Assembly formation, evidence update, or language generation.

## 1. Package architecture

Preserve existing I0 typed contracts, config and integrity behavior. Extend with a small graph package (do not create placeholders that are never imported):

```text
src/dgca_next/
  contracts.py                      # extend only for agreed physical schema
  config.py                         # preserve pinned baseline
  graph/
    __init__.py
    cell.py                         # persistent cell metadata, lazy storage
    latent.py                       # 24-slot typed neighborhood, reverse index
    synapse.py                      # legal directed keys + record validation
    network.py                      # single sparse graph and accessors
    budget.py                       # unique directed-key reservations / caps
    transaction.py                  # deterministic in-memory shadow / rollback
tests/
  test_graph_addresses.py
  test_graph_cells.py
  test_graph_latent.py
  test_graph_synapses.py
  test_graph_budgets.py
  test_graph_transactions.py
  test_graph_stress.py
docs/implementation/
  I1-IMPLEMENTATION-CONTRACT.md     # this file
  I1-VERIFICATION-REPORT.md         # write only after execution
```

These filenames are an organizational recommendation; limited consolidation is acceptable if responsibility and tests remain clear. Importable modules are preferable to artificial class hierarchies.

## 2. Responsibilities and interfaces

### 2.1 Physical address space and cell metadata

- Reuse I0 `Region`, `CellAddress`, `SynapseScope`, `SynapseKey`; never introduce another cell-ID formula.
- Three physical regions × (32 rows × 16 columns × 8 slots) = **12,288 logical cells**; **4,096 per region**. Every physical address maps bijectively to a fixed ID.
- `Cell` carries only physical identity, commitment flag/committed_event, legal graph structural metadata, and bounded local numerical/homeostatic state interfaces. **No raw text, vocabulary ID, concept label, role name, output class, expected token, training outcome or ground-truth field.**
- The logical uncommitted majority MAY be lazily represented. Iterating physical IDs cannot mutate W or implicitly commit a cell. No eager 12,288×12,288 adjacency matrix.
- `R` activity/temporal scratch must remain separate from persistent W commitment/connectivity; I1 must not replace the I0 immutable W/R/HSlow contracts with mutable public aliases. I1 may define physical schemas but MUST NOT invent activation laws.
- Commitment from a witness during LEARN is **I3**. In I1 provide an isolated fixture-only graph builder for structural tests; fixture-built cells/edges are never presented as learned knowledge.

### 2.2 Microcolumn and bounded physical neighborhoods

- Provide pure geometry: `microcolumn_of(cell_id)`, same microcolumn, orthogonal Manhattan radius 1, and bounded Manhattan radius 2 from a specified anchor; stable ordering and edge clipping.
- Normalize nothing here: I2 owns Microcolumn Normalization/Two-Pass.
- No across-region local-neighborhood admission by accident; physical address/region distinctions are checked exactly.

### 2.3 Latent anatomy and inverse index

- Every logical cell has **24 categorical latent slots**: 6 co-active intra, 6 fixed local, 6 co-active inter (3 per other region), 6 fixed topographic (3 per other region).
- Each slot has typed category, permitted region, empty/occupied state, actual target cell ID if present, stable slot index and protection/recyclability markers. No self-target. Fixed local/topographic slots cannot recycle.
- Maintain exact transactional `reverse_latent_index` such that the forward and reverse views agree after every committed edit. A failed edit MUST restore both. Never expose a mutable alias.
- Structural directed-key eligibility uses **either endpoint**: `D(i,j) = (j in N(i)) OR (i in N(j))`; D is independent of link direction. Absence of this predicate is a hard reject for a proposed physical link.
- Coactive slot recycling is only permissible when there is no legal protected/live synapse (in either direction) and no contextual pin; pinned slots never evict, returning named diagnostic `RECYCLE_BLOCKED_CANDIDATE`.
- Contextual 2/2/2 uses *up to six* z-side co-active intra slots, with uniqueness on physical target IDs, separate role-key claims and no extra latent capacity; exact selecting/learning of P/C/Y is reserved to I5.
- **Policy boundary L01:** RC4.1 §1.3 names inherited highest coactive/intra and deterministic local/inter/topographic initialization and an 'original confirmation window', but does not itself give the full comparator/target-selection procedure. Implement SLOT SCHEMAS, VALIDATION, REVERSE INDEX, EXPLICIT TEST-FIXTURE INJECTION, and reversible primitive operations in I1. Do not silently create a novel random or heuristic initialization/recycling policy. Search both normative specs for an exact rule; if absent, report `UNRESOLVED_LATENT_POLICY` and stop that **policy subgate** only, not unrelated structural tests. A proposal for the missing policy must be separately reviewed before production auto-wiring is enabled.

### 2.4 Directed synapse anatomy

- Canonical structural key is exactly `(source_id, target_id, scope)`; distinct reverse keys are independent; no self-links or duplicate live keys.
- Scopes: LOCAL same region Δ=0; CROSS_TERRITORY distinct regions Δ=0; ASSOCIATIVE any legal source/target regions Δ=1. Reject Δ>1 and all unsupported combinations.
- A *data record* may carry typed state `CANDIDATE|EPISODIC_INDEXED|CONSOLIDATED`, S, E_ext, E_int, external-root count, identity and lifecycle metadata. Validate legal bounds; do **not** transition states via assumed evidence during I1.
- If derived quality `Q` is exposed as a PURE function, use only Core §1.4/LLA §4.1 and fixed config with no additional decay; it does not itself activate a cell or update a synapse.
- Fixture construction may create an explicitly constructed legal CONSOLIDATED link for geometry/lookup tests, with `fixture_only` provenance; it is never a learning result. Production synapse creation is reserved to accepted END_EXPOSURE in I3.
- Persisted accepted roots, q/y reduction, eligibility traces, demotion/pruning and neural signal propagation are OUTSIDE I1.

### 2.5 Budget and reservation invariants

- Total outgoing distinct *live directed keys + unique reserved future keys* ≤ **B_i=64** for each source; cross outgoing keys/claims ≤ **B_i_cross=12**. Count physical directed keys, never role repetitions.
- Episodic outgoing cap **E_cap=4**, Assembly memberships **M_max=12** as structural bounds only; actual replay-episodic policy and Assembly lifecycle are later milestones.
- Reservations are keyed by the unique intended directed synapse; identical live key/reservation is not double charged. Releasing/fulfilling a claim never double-debits or double-frees. Incoming links do not debit target outgoing cap.
- A z-side latent slot can make the physical pair eligible even when the P/C source has no spare latent slots; it NEVER bypasses the **source outgoing** budget.
- Protected valid consolidated links are never silently deleted for capacity. Invalid or saturated requests fail with explicit reason and no partial publication.
- Capacity comparisons involving prospective multiple links must use one deterministic *shadow reservation ledger*; preserve canonical physical-ID/scope ordering for conflict resolution. Do not implement LLA proposal arbitration here.

### 2.6 In-memory atomicity and integrity

- Use side-effect-free validation and one in-memory shadow commit for coherent updates of cell metadata, latent forward/reverse indices, synapses and budget reservations. All-or-nothing on injected failure.
- Idempotent repetition of an already accepted exact mutation is either a strict no-op or an explicit duplicate rejection; choose one **documented administrative API convention** and test it. Conflicting duplicate payloads must fail.
- Stable traversal order must not depend on Python dictionary/hash iteration; iteration and debug dump are deterministic.
- Implement `validate_graph()` as an independent read-only invariant audit: correct IDs/regions, committed/source links, category slot counts, no self/illegal scope, inverse index agreement, active links eligible under D, pinned protection, distinct key counts, reservations and caps.
- Persistence to SQLite, durable root journal, save/load, crash recovery, root `BEGIN/END/ABORT` and W/H rollback are I3+; do not equate in-memory transaction tests with durable crash consistency.

## 3. Exact explicit exclusions

No SIC receiver commitment from a true event, no Two-Pass dynamics, no `A_j^+` calculation, no external positive link witness, no `q/S/E` learning update, no autonomous synapse creation, no Auto Assembly `FORM`, no owner/recruitment, no `G_ctx`, no REPLAY schedule, no READ_ONLY retrieval, no GENERATE, no real learned text, no trained model claims. Leave LLA-T01–T41 and LG-T01–T16 scientifically NOT_RUN except any explicitly mapped pure physical contract subsets, never relabel I1 unit fixtures as empirical success.

## 4. Execution increments

**I1-R01 — Anatomy**: add sparse logical cell metadata, geometry, typed latent slots, physical address/region invariants, minimal exports, tests. Confirm I0 163 regression tests remain green.

**I1-R02 — Graph links and budgets**: add typed directed synapse records, bidirectional D eligibility, inverse index, unique reservations, capacity manager and deterministic ordering. No external q.

**I1-R03 — Atomicity and verification**: shadow transactions, failure injection rollback, protection/recycling validators, 12,288 logical-cell integration/stress cases, full regression, narrow cross-platform CI.

**Do not merge until a final I1 review.** Implementation may be one branch with several commits; the final report must distinguish R01–R03 evidence.

## 5. Explicit I1 tests and expected verdicts

| ID | Check | Acceptance |
|---|---|---|
| I1-T01 | 12,288 unique IDs, three regions and bounds | bijection; zero collisions |
| I1-T02 | lazy/uncommitted cell access | no mutation, no accidental commitment |
| I1-T03 | region/microcolumn geometry at corner, edge, center | stable radius-1/radius-2 neighborhoods |
| I1-T04 | 24 typed latent category positions | 6+6+3+3+3+3 only; category-region invariants |
| I1-T05 | forward/reverse index update and rollback | identical pre/post failure hash |
| I1-T06 | D(i,j) by one-sided, other-sided, both and neither | OR predicate exact |
| I1-T07 | fixed slot recycling attempt | hard reject |
| I1-T08 | protected live-link/candidate slot recycling attempt | reject, no partial change |
| I1-T09 | unprotected slot recycling, if exact policy supplied | deterministic, index-consistent; otherwise POLICY NOT_RUN |
| I1-T10 | legal Δ/scope matrix and reverse direction independence | illegal pairs reject |
| I1-T11 | self-link and duplicate key | reject or documented idempotent exact retry |
| I1-T12 | missing D and uncommitted endpoints | physical link construction fails |
| I1-T13 | source outgoing 64 and 65th request | 64 allowed; 65th rejected atomically |
| I1-T14 | cross outgoing 12 and 13th request | 12 allowed; 13th rejected atomically |
| I1-T15 | multiple reservations same intended key | exactly one capacity claim |
| I1-T16 | reserve→live transfer and rollback | no double debit or hidden release |
| I1-T17 | full source latent slots but z-side D with available outgoing budget | eligible physical link (no semantic recruitment) |
| I1-T18 | overlapping 2/2/2 physical role fixture | one slot per unique physical source, unique keys counted |
| I1-T19 | fixture-only quality Q computation, including E_int>E_ext | exact formula, zero absent link |
| I1-T20 | invalid numeric state / NaN/Inf / negative evidence | rejected without normalizing |
| I1-T21 | independently audited graph after every mutation | no stale indices/counters |
| I1-T22 | injected failure at slot, index, link, budget publication | full in-memory rollback |
| I1-T23 | same graph constructed with reordered fixture insertions | same canonical structural output |
| I1-T24 | full logical network 12,288 + sparse links | no dense 12,288² allocation |
| I1-T25 | I0 full regression and unchanged spec hashes | all prior I0 tests PASS |
| I1-T26 | fixed slot initializer/coactive policy executable check | PASS only with precise source rule; otherwise `UNRESOLVED_LATENT_POLICY`/NOT_RUN |

Tests T13/T14 must create enough genuinely distinct legal target/pair fixtures to reach caps; do not bypass D or region gates to force an artificial passing budget counter. Test T19 remains *fixture arithmetic*, not training.

## 6. Stop/go gate

- **I1-G01** physical space + valid Cell model.
- **I1-G02** latent typed structure + forward/reverse correctness + D.
- **I1-G03** directed Synapse legality and bookkeeping, no semantic state.
- **I1-G04** source/cross/episodic/assembly caps and unique claims (within I1 structural scope).
- **I1-G05** deterministic shadow commits; injected-failure rollback.
- **I1-G06** stress 12,288 logical addresses with sparse memory behavior; timings and memory measured, **no invented performance PASS threshold**.
- **I1-G07** preserved I0 tests, specs, source manifest, reproducibility and CI.
- **I1-G08** clear report: PASS/FAIL/NOT_RUN/POLICY_BLOCKED; no scientific claims.

If latent initiation/recycling policy cannot be inferred exactly from the two specs, **I1 as a whole cannot be declared fully COMPLETE**; report the policy subgate as BLOCKED while delivering the verified structural subset. Do not prolong policy debates before building the independent structural pieces.

## 7. Development rules and evidence report

1. Work only in `feature/i1-graph-anatomy`. No force push, no merge and no modifications to `main`.
2. Check Git starting SHA, record source-spec SHA-256, and run all existing I0 tests first.
3. Implement with the existing Python 3.14-compatible package, no unnecessary third-party runtime deps.
4. Adapt CI to validate I1 feature pushes or PRs without accidentally dropping existing I0 checks.
5. At each R01/R02/R03 checkpoint, run new tests and all I0 regressions.
6. Final commands must include `python -m dgca_next verify-specs`, `python -m pytest -q --basetemp=.pytest-tmp`, `python -m ruff check .`, `python -m ruff format --check .`, `python -m mypy`, `git diff --check`, `git status --porcelain`.
7. Produce `docs/implementation/I1-VERIFICATION-REPORT.md`: starting/final SHA (avoid embedding own final commit SHA inside file), exact changed paths, exact test outputs and counts, metrics, explicit synthetic fixture distinction, limitation list, scientific test NOT_RUN, unresolved policy, and I1-G01–G08 verdicts.
8. Commit/push to feature branch, report `I1 REVIEW READY` **only when gates are all satisfied**, or `I1 PARTIAL / POLICY_BLOCKED` with exact evidence. Stop for independent review; never silently change graph law/constants to make tests green.
