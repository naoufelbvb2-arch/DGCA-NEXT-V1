# DGCA NEXT — I1 L01 Latent Wiring Policy: Targeted Resolution Proposal

**ID:** I1-L01-POLICY-RESOLUTION
**Revision:** PROPOSAL-R01 (2026-10-27)
**Status:** **FOR SCIENTIFIC APPROVAL — NOT NORMATIVE — NOT IMPLEMENTATION AUTHORIZATION**
**Source implementation:** `feature/i1-graph-anatomy` at `1de0de43cfc634fb5e00ed175c121d749b779c41`.
**Affected source sections:** CORE RC4.1 §1.3, §7.3, §10.1–10.2; LLA RC4.1 §5, §6.2.
**Compatibility:** Preserve 24 slot quotas, D(i,j) OR eligibility, local Δ0 vs associative Δ1, 64-outgoing budget, two-root evidence, genuine observation provenance, and immutability of successful knowledge.

This is a deliberately limited scientific decision candidate for I1-T09 and I1-T26. It is NOT a replacement for the two RC4.1 normative documents. If approved, integrate the normative language **inside those two documents**, update the source manifest/integrity hashes and existing I0/I1 regression fixtures in the **same explicitly versioned scientific baseline transition**, then implement and test. Never edit pinned RC4.1 files in place without versioning/migration.

## 1. What history specifies, versus what it does not

The historical `DGCA-V2-CORE-LLA-SPEC v2.0.0` (in the original archival `LLA-&-L2.txt`):
- Defines **6 co-active intra**, **6 fixed local**, **3+3 co-active inter**, **3+3 fixed topographic** slots.
- For co-active candidates specifies the *most active* cells in `L_t ∪ K_new`, respectively within the same region and each other region.
- For local slots names own and four orthogonally neighboring microcolumns.
- For topographic slots names a deterministic `hash(id, other_region, salt_T)` mapping.
- States bilateral recycling after `W_conf`, with neither direction supporting live link, and local novelty `nu_r ≥ theta_R`.
- Defines `W_conf=100`, `theta_R=.30` elsewhere.

**Still missing:** exactly how target ranking/ties work; cold batch commitment order; fixed local neighbor spread; topographic hash byte preimage and salt; candidate duplication across slot classes; slot age clock/boundary behavior; exact source of novelty `nu_r`; deterministic two-sided replacement and evidence-free recovery. These are NEW lab decisions if approved, not historical facts.

## 2. Proposed deterministic, physically local initialization

### 2.1 Timing, source, and no retroactivity

Only initialize latent slots for physically newly committed cells. Use the same canonical external EVENT witness/snapshot from which the sensory admission was accepted, with a **frozen event-time activity vector**. A full same-event birth cohort `K_new` is evaluated simultaneously, sorted by physical cell ID; never let iteration order determine availability. `L_t` consists exclusively of cells already committed before that EVENT and present in its lawful active frontier; `K_new` consists of the cells accepted for commitment in that EVENT. Each potential target is a physical cell ID, not a word/feature label.

For ranking only: a prior committed frontier cell gets `score=Q6(A_i^+(t))`; a same-event newly committed receiver gets `score=Q6(X_ext[i])` from directly observed SIC, never bootstrap/prediction. The score creates **latent topology only**; it does not create a learned synapse, q, S, E or an external evidence root. Co-birth peers can see one another in `K_new` only after the entire cohort passes admission rules. No retrospective learning involving newly born cells in that root.

Build each cell's 24-slot candidate layout from a single immutable event snapshot, then publish accepted slot/reverse-index changes atomically with lawful sensory commitment. `ABORT` preserves only the explicitly allowed sensory commitments and their incident original physical slot initialization; it credits **no** staged synaptic evidence/novelty certificate. No other root may interleave.

### 2.2 Fixed LOCAL six slots

Construct the ordered set of microcolumns `[owner_own_mc] + [valid Manhattan-1 orthogonal neighbor microcolumns sorted by (row,col)]`. Cycle through these microcolumns round-robin, selecting each column's lowest not-yet-selected physical cell ID different from the owner, until six distinct targets are chosen. Skip exhausted columns; at borders cycle among remaining valid columns. This deliberately covers adjacent columns rather than always taking six members of the owner's own column. Only same-region targets are legal. LOCAL slots are permanently fixed, even if their target remains uncommitted.

### 2.3 Fixed TOPOGRAPHIC 3+3 slots

Freeze a dedicated **new** domain-separated 16-byte topographic salt `salt_T=ASCII("DGCA-LATENT-TOP1")` and version tag `ASCII("DGCA-LATENT-TOPO-V1")`. These are proposal choices, not SIC salts.

For a source ID `u`, other-region byte `r`, slot ordinal `k ∈ {0,1,2}`, define:

`payload = tag || 0x00 || salt_T || u32BE(u) || u8(r) || u8(k)`

`base = u64BE(SHA256(payload)[0:8]) mod 4096`.

Choose the target by deterministic circular linear probing `(base + probe) mod 4096` over the requested region, skipping a physical ID already selected for **any** slot owned by u. The first remaining target wins; at most 4096 probes, otherwise explicit error. Process target regions in Region enum order and ordinals ascending. Never call Python's random hash. Topographic slots remain fixed.

### 2.4 Dynamic COACTIVE slots (6 intra + 3 per other region)

After choosing all fixed local/topographic targets, enumerate from the immutable `L_t ∪ K_new` snapshot for each target region, exclude `u` itself and any target already selected by `u` in any category. Sort candidates by `(-score_q6,cell_id)`; select top 6 for same region and top 3 for each other region. No padding with unobserved/uncommitted random neighbors. If fewer eligible coactive candidates exist, leave remaining slots **EMPTY**; later lawful filling during another *genuine witnessed event* uses the same ranking and atomic checks, and is not counted as recycling or evidence. In LANGUAGE-only laboratory the other-region coactive slots can therefore stay empty.

A contextual z recruited at END uses the existing §7.3 **protected six-slot exception first**. Ordinary initialization must not override/evict its 2/2/2 pins; fixed six LOCAL and six TOPOGRAPHIC still use this proposal's physical policy. No extra slots or outgoing-key budget are introduced.

### 2.5 Physical invariants

- One owner's occupied slots contain distinct target IDs; the reverse index is exact. Cross-owner reciprocity is **not required**: latent `D_ij` is OR.
- Fixed slots never recycle, even if no links ever form.
- Co-active target selection is physical and deterministic, **not a link creation or guarantee of a reciprocal consolidated triangle**.
- No target may be chosen based on `raw_surface`, an expected outcome, category labels, or test oracle.
- Runtime must reject unversioned/mismatched topographic policies at checkpoint load; save/load semantics are otherwise reserved for later milestones.

## 3. Proposed recycling lifetime and evidence gates

### 3.1 Time and protection

For each occupied dynamic slot `(u,slot,v)` store `assigned_at_completed_close_serial` and last wiring event metadata. An initial assignment during OPEN records the then-current completed-close count and a pending birth marker; ABORT retains the permitted physical birth without aging/novelty credit. Eligibility requires at least **100 completed external root-closes** since assignment (`completed_external_closes - assigned_at_completed_close_serial >= W_conf=100`). ABORT, READ_ONLY, REPLAY, internal GENERATE do not age this count.

For **both** directed pairs `(u→v)` and `(v→u)`, there must be no live `CANDIDATE`, `EPISODIC_INDEXED`, or `CONSOLIDATED` key of any scope and no reserved intended key or candidate pin. If either side is fixed/protected/pinned, block the bilateral operation. Cross the full shadow budget/reverse-index/audit before publishing. No protected link or knowledge is deleted.

### 3.2 Novelty: a genuinely missing contract

The old text invokes `nu_r>=theta_R=.30` but does **not** define `nu_r` numerically; DCR's branch novelty `nu_ctx=c*dP*dY` is a different measure and cannot be substituted silently.

**Proposed I1/I2 interface boundary:** I1 implements pure recycling feasibility and deterministic shadow mutation **only** when passed a typed `VerifiedLocalNovelty` witness created and validated by a future real LEARN event executor. I1 itself cannot create that proof or infer novelty from fixture labels. While its numeric producer is absent, **production automatic recycling stays disabled**, even if the slot is 100 closes old. Synthetic witnesses are allowed solely in clearly designated physical fixture tests.

**Suggested new measurable I2/I3 rule for approval**, not yet authorized:
For a directly observed receiver u at a real LEARN event t, with predicted pre-observation one-step temporal drive `P^T_u(t)` frozen before direct SIC input, define

`nu(u,t) = max(0, X_ext(u,t) - min(X_ext(u,t), P^T_u(t))) / max(X_ext(u,t), 1e-6)`,

and `nu(u,t)=0` when there is no genuine external direct observation at u. Accept a recyclable pair's trigger iff one endpoint has a verified value `>=theta_R=.30`. This is a **new candidate scientific novelty definition**, and must be tested for degenerate always-novel behaviour. Do not enable merely because the scalar was supplied by a caller.

### 3.3 Bilateral replacement

Once a valid verified novelty trigger, confirmation age, protection, real coactive replacement candidate(s), and shadow capacity checks coexist: stage the two-sided removal of dynamic u↔v slot occurrences (when present), but only if **both** copies, if present, are recyclable and unprotected. Replace only the vacated dynamic slot(s) using the same current-event ranked `L_t ∪ K_new` candidate pool and each source slot's region/category rule, excluding the just-evicted old target for that operation. Do not change any fixed slot. If either side has no legal replacement, fail the whole bilateral transaction unchanged with `NO_RECYCLING_REPLACEMENT`, rather than silently deleting. Write ordered `WIRING(...,RECYCLED)` entries only after successful atomic publication. No partial reverse-index mutation or evidence credit.

## 4. Acceptance and scientific risk checks

- **L01-T01**: cold same-event cohort of 3 directly observed new physical receivers produces a deterministic 3-way coactive *eligibility* graph where valid, but **no learned links**; any structurally unfit cohort is reported, not artificially rewired.
- **L01-T02**: local border/corner/center fixed round-robin targets; neighboring microcolumns are reached and stable.
- **L01-T03**: topographic target vectors byte-exact on Windows/Linux, 3 distinct targets per other region, no SIC salt reuse.
- **L01-T04**: rank ties/order and empty dynamic slots; identical results under reordered birth inputs/sets.
- **L01-T05**: no retroactive same-root link/evidence, including ABORT-permitted sensory commitment.
- **L01-T06**: BEFORE 100 closes recycling impossible, after 100 closes *still impossible without real verified novelty*.
- **L01-T07**: bilateral protection tests include reverse links, candidate/episodic live states, reservations, pins, fixed slots and torn transaction injection.
- **L01-T08**: true physical replacement rebuilds reverse indexes and wiring log; no replacement ⇒ no-op/fail.
- **L01-T09**: examine first-lab SIC coactivation fitness: % birth cohorts with enough legal 3-way reciprocal LOCAL eligibility (not CONSOLIDATED links). This is a measured feasibility metric, not a tuning target or automatic success claim.
- **L01-T10**: hashes/digests/replay of slot population deterministic; no forbidden semantic labels.
- **L01-T11**: original 314 PASS and CI on Ubuntu/Windows remain; scientific LLA/LG tests still NOT_RUN.

## 5. Approval and implementation order

**Do not merge I1 yet and do not claim full I1-G02 PASS.** Current status remains `I1 PARTIAL / POLICY_BLOCKED` (314 PASS, 2 pytest skips). This document is an evidence-backed **proposal**, not a command to Codex.

If approved:
1. Integrate the exact chosen policy, including an explicit decision on the local novelty function, into the two scientific specs as **new versioned RC4.2** (not an in-place silent change to RC4.1). Update source manifests/integrity and typed fixture hashes atomically in a dedicated spec-migration commit. Preserve RC4.1 in git history, and do not label RC4.2 scientifically validated.
2. In the same I1 branch, implement deterministic initialization and the guarded recycling mechanism. Where no genuine novelty producer exists before I2/I3, classify **production trigger integration as NOT_RUN / DEFERRED**, never counterfeit real external evidence. Replace skipped T26 with actual pure physical initialization tests. Replace skipped T09 with tested pure recycling guard and synthetic trigger cases, clearly distinguishing the later real LEARN integration test.
3. Re-run all I0/I1 regressions, run cross-platform CI, independently review diff and updated spec hashes. Merge I1 only after explicit decision about deferral of real novelty triggering to I2/I3; any true neural learning/Assembly result remains unclaimed.

**Critical distinction:** missing *policy definition* is a real contract blocker; missing *I3 runtime wiring of a future verified novelty producer* need not keep I1 physical anatomy blocked if the correct guarded mechanism is already verified and its production trigger is explicitly out-of-scope. Do not relax protection, evidence or binary64 laws to make an initialization test pass.
