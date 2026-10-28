# DGCA NEXT — I3 S01/S02 Scientific Resolution Proposal

**ID:** I3-S01-S02-RESOLUTION-PROPOSAL
**Revision:** PROPOSAL-R01 (2026-10-28)
**Status:** PENDING OWNER APPROVAL — NON-NORMATIVE — NOT IMPLEMENTATION AUTHORIZATION
**Branch:** feature/i3-local-learning
**Reviewed implementation:** 500f5e10c1670ce5a079f531505f68d5a839a5fc
**Current authority:** Only CORE RC4.3 and LLA RC4.3 (DESIGN CANDIDATES, NOT FROZEN, NOT EMPIRICALLY VERIFIED).

The two choices below are NEW first-laboratory scientific policies, not laws already established in RC4.3. This proposal does not implement EVENT/END, authentic learning, graph publication or a cold-start experiment. Current I3 remains PARTIAL / SPEC_BLOCKED.

## 1. Verified state and source gap

CORE §§1.3.1–1.3.4/12 specify K_R=12 and rank LATENT targets AFTER cohort selection, but do not select sensory receivers when more than 12 qualify. I3 production preflight finds 16 distinct equal-support receivers for four features a, ab, c, d and rejects as I3-S01.

CORE §§1.2/5/12 define legal gain range .70..1.40, rho_cell=.05, LANGUAGE regional rho_target=.030 and theta_active initial=.20, and the formulas for later homeostatic adaptation; no initial per-cell gain, per-cell firing EMA or regional firing EMA is specified. I2 uniform_language fixture values are NOT initial production authority. The I3 preflight rejects as I3-S02.

The existing I3 work has 621 PASS and 0 failed/skipped tests, independently confirmed successful final-head Windows/Ubuntu CI, but RootStore.EVENT and END still fail closed intentionally and all scientific learning remains NOT_RUN.

**Additional implementation trap verified in current code:** RootStore.event currently invokes ingress preflight against a freshly created SparseNetwork(), not against a persisted production W snapshot. That is acceptable only as a fail-closed skeleton; a future production EVENT must load and validate the actual durable W before identifying previously committed receivers, allocating K_new, computing same-root eligibility or adapting H. The current store has EMPTY_W markers only, no learned W codec. Repeated observations cannot be adjudicated correctly by removing S01/S02 errors alone.

## 2. S01 — exact sensory cohort arbitration for the first LANGUAGE laboratory

For an authenticated, valid external LEARN EVENT t, compute one canonical SIC-V1 projection before commitment, including exact integer-millionth direct support. Freeze the pre-event committed set. Define

U(t) = { (cell_id, X_fixed[cell_id]) : not committed_before(cell_id,t) AND X_fixed[cell_id]/1_000_000 > eps_p }.

Each physical receiver occurs ONCE, regardless of feature collisions or number of contributing features. Rank by (-X_fixed_integer, physical_cell_id), then take the first min(K_R, |U|). The remaining eligible receivers are DEFERRED, not silently discarded or committed and not stored as a pending autonomous birth queue. Record per-cell SENSORY_BIRTH_CAPACITY_DEFERRED diagnostics; retry occurs only after a new genuine external observation.

**I3 quota interpretation:** contextual candidate admissions are disabled throughout I3. Since Core calls the 8 sensory/4 context allocation nominal and transferable, no contextual reservations exist; the I3 effective sensory capacity is all K_R=12. When the later I5 context engine exists, its genuine concurrent EVENT/END capacity reservations need a separate explicit scoped policy and test, not silent reuse of this I3-only ruling. Never retroactively displace an EVENT-born cell at END.

This selection uses actual merged physical X_fixed, not neural A, predicted activation, feature order, raw text, expected output, semantic class, or a second application of salience. The accepted K_new cohort is initialized simultaneously under the ALREADY APPROVED L01 co-birth and 24-slot policy. Newborn cells never provide same-event q, F_step or retrospective synaptic evidence.

### Fixed numeric example

On empty LANGUAGE graph, features (a,1),(ab,1),(c,1),(d,1) yield sorted global IDs, all with X_fixed=1000000:

8286, 8465, 8606, 8649, 8694, 9227, 9345, 9902, 9912, 10128, 10273, 10513, 11524, 11641, 11795, 12181.

Select first 12 through 10513; defer 11524, 11641, 11795, 12181. If a distinct later legal root repeats observation, the remaining four can then be admitted (up to available 12), but NO evidence may be backdated to their first event.

**Tradeoff:** deterministic physical-ID tie-break can temporarily bias admissions toward low IDs. This is intentionally measurable, not claimed optimal. Count per-cell deferrals, distinct eventual committed receivers and exposure-to-admission in empirical reports; do not invent random tie rotation or label-aware quotas to make the tests pass.

### S01 tests

S01-T01 exact 16-receiver vector, 12 accepted / 4 deferred, atomic one-cohort initialization and zero birth-root q.
S01-T02 reorder input features and repeat NFC/duplicate features: identical X_fixed/ranked physical cohort/digest; same physical receiver counted once.
S01-T03 uneven physical supports prioritize highest merged integer support; ties physical ID; salience applied once; no float tie ambiguity.
S01-T04 cardinalities 0/1/8/12/13/16; no K_R overflow; already committed are excluded; read-only never births.
S01-T05 later genuine root may commit previously deferred cells; no automatic deferred birth or same-root credit.
S01-T06 no contextual owner/candidate fabrication; I5 EVENT/END quota interaction is explicitly deferred.

## 3. S02 — neutral versioned initial H profile and newborn semantics

### Experimental new default profile, LANGUAGE only

- initial or newborn cell gain g0 = 1.0 binary64, neutral neural multiplicative gain.
- initial or newborn cell firing EMA rbar0 = rho_cell = .05, the already specified per-cell target.
- initial LANGUAGE regional firing EMA rhobar0 = rho_target_LANGUAGE = .030, the already specified regional target.
- initial LANGUAGE theta_active = .20, ALREADY fixed in RC4.3.
- initial VISION/AUDIO thresholds and production homeostasis remain UNRESOLVED / UNSUPPORTED in LANGUAGE first lab. No copying LANGUAGE values.

These are new initialization choices; the referenced rho_cell and rho_target values are existing constants but their use as INIT VALUES is proposed, not source-derived. Keep adaptation factors, thresholds, Q, SIC, and evidence mathematics unchanged.

### Event order and crucial ABORT / H_BEGIN identity

At event start freeze K_r(t), pre-event H and theta. New cells are committed only at the event's atomic close and do not participate in event-time regional denominator, per-cell EMA or any same-event learning. A newborn's effective g=1, rbar=.05 and current shared regional theta/rho_bar apply until it was committed-before a later real event; then ordinary adaptation may update its per-cell fields. A birth must NEVER reset the current adapted regional theta/rho_bar to laboratory start values.

CORE §10.1 requires byte/exact H_slow_BEGIN restoration on ABORT while permitting an already lawful sensory birth in W to remain. A naive mandatory durable per-cell H record on sensory birth would violate this requirement on ABORT.

**Required solution:** implement version-pinned immutable H default profile + sparse durable per-cell ADAPTATION OVERRIDES (or a proven byte-equivalent design). Missing per-cell override for a legally committed cell is resolved from the approved immutable profile, with no durable H mutation. Expand full Homeostasis input for I2 numeric evaluation as a PRIVATE frozen temporary snapshot; such expansion does not create external evidence or publish H. A cell which was born during a later-ABORTED root can remain in W and still get exact effective defaults after H_slow is restored byte-for-byte to the BEGIN image. Do not reject legitimate lack of a newborn override as an error; do reject a missing/mismatched profile hash, malformed schema or an unauthorized missing already-adapted record.

An H override is published only on legitimate committed-before-event homeostatic adaptation in a provisional EVENT checkpoint; completed roots retain it, ABORT restores the full original H_BEGIN (including previous legitimate overrides). Subsequent roots may not restore an older H image from an unrelated ABORT. Zero committed LANGUAGE population => no regional EMA/threshold update, though initial regional values remain persisted. READ_ONLY, FULL/CONTROL, REPLAY, GENERATE hold H unchanged.

Stable cold and restore profile values must be explicit in the two scientific sources and code/config manifest; do not use caller-provided H values as a loophole for uncontrolled scientific tuning. Optional alternate H initial profiles require separately versioned comparator experiments, never implicit fallback.

### S02 tests

S02-T01 H0 exact effective profile and deterministic serialized version/hash: gain=1, rbar=.05, language rho_bar=.03, theta=.20.
S02-T02 newborn H without override is properly resolved, not adapted in birth EVENT, but adapts exactly once on next genuine LEARN EVENT.
S02-T03 after EVENT with newborn sensory W and provisional H changes, ABORT leaves lawful born W, restores EXACT H_BEGIN raw bytes, and still resolves newborn defaults.
S02-T04 earlier completed-root adapted overrides survive a later aborted root, including crash/retry and duplicate ABORT.
S02-T05 cold/read-only numerical materialization never mutates persisted W/H; no latent evidence from default expansion.
S02-T06 birth does not reset adapted regional threshold/EMA; zero-committed event skips region update; VISION/AUDIO fail closed.
S02-T07 report measured sensitivity in separately declared comparator H0=0 rates vs the above baseline; no automatic science-version tuning.
S02-T08 corrupted profile/schema/codec or nonfinite overrides rejected on load.

## 4. Scientific version, execution scope, and empirical boundaries

If the project owner APPROVES S01/S02:

1. Version the two scientific authorities **together** RC4.3 → CORE RC4.4 + LLA RC4.4, with hashes and immutable archival RC4.3 history; exactly two CURRENT normative science files. S01 belongs to Core K_R admission and LLA EVENT gating, S02 belongs to Core H initialization/ABORT and LLA EVENT/H boundaries. Preserve unrelated laws and constants byte-for-byte and upgrade config fingerprints/integrity tests atomically.
2. Implement admitted-K_new selector, explicit physical deferral diagnostics and production H profile/newborn virtual defaults with exact H_BEGIN rollback.
3. Continue the STILL MISSING I3 real-path work: production graph/synapse origin (not fixture_only), witnessed EVENT, lawful link proposals and END, root MAX q paired y, actual stored E_ext/S/independent root counts, journal/checkpoint/crash restore, actual R/F_step linkage, learned W codec, trusted event-local novelty, and from-zero real LOCAL+ASSOCIATIVE link experiments. No I4/I5/Generation work.
4. Preserve 621 I0–I3 current tests, add targeted S01/S02 tests, exact scientific source validation, Ruff/format/mypy, Ubuntu/Windows final-head CI.
5. **Do not claim that resolving these policies proves learning.** The first true empirical gate requires that a production root actually witnesses two committed-before-event sources, forms and strengthens legal links from a cold empty target-link graph, preserves them over save/load, and shows read-only causal influence. No fixture mutation may satisfy that gate.
6. No merge to main, no I4, no "I3 REVIEW READY" until independent full I3 acceptance. Remaining work may be PARTIAL even after these policy decisions pass.

**Present verdict:** I3 PARTIAL / SPEC_BLOCKED. This is a proposal, not authorization to modify RC4.3, train, or claim successful learned synapses.
