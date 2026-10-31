# DGCA NEXT — I4-R02 Production FORM Integration — Owner Decision Proposal

**ID:** I4-R02-D01-D02-OWNER-DECISION-PROPOSAL
**Date:** 2026-10-31
**Status:** APPROVED BY PROJECT OWNER — I4-D01=A, I4-D02=A, AND STAGED R02 FORM-ONLY CONTAINMENT. AUTHORITATIVE ENGINEERING DECISIONS FOR I4-R02 ONLY; CORE/LLA SCIENTIFIC SOURCES UNCHANGED.
**Base:** main `88fc596c178c8a89c24b991e280d7a0ca8c07779`; R01 delivered `b063b0051be452b83f74081572ba3af2d685d7f5`.
**Audit:** docs/implementation/I4-R01-INDEPENDENT-ACCEPTANCE-REVIEW.md
**Science:** CORE RC4.4 and LLA RC4.4 unchanged DESIGN CANDIDATES.

## Decision I4-D01 — P04 controlled rewiring vs native Assembly END

**Problem.** I3/P04 root END settles synapse evidence and optionally rewires a requested physical latent pair. CORE §10.2 requires future native Assembly MAINTAIN→GROW→FORM→MERGE/SPLIT inside END after evidence and contextual governance. Concurrent rewiring and FORM could change structural support or member protections within the same close. The accepted R01 read-only inspector conservatively refuses a historical END marked P04 RECYCLED.

**Option A — RECOMMENDED laboratory containment:** define two explicitly versioned execution capabilities, never active together on the same root:
- **I3-legacy/production (existing schema-4)**: P04 explicit request/recycling remains available, native Assembly writing unavailable; all existing I3 704+ regression behavior preserved.
- **I4-native experimental (new schema-5)**: root BEGIN/EVENT/END supports true native Assembly operations with normal evidence settlement; attempts to stage P04 controlled rewiring explicitly raise `I4_REWIRING_CONFLICT` **before** publication. A root that somehow contains both intents from tamper/old schema fails closed. An unrequested native END has no rewiring. The flag is versioned/validated, never a mutable user knob bypassing trust.
This is a conservative capability boundary, NOT a new learning law: there is no simultaneous restructuring of assembly membership and physical latent slots until a separately reviewed Core-compatible ordering is approved.

**Option B — deferred:** implement both within one END under a new explicitly approved order with same-root live protection, membership invalidation and no retroactive witnesses; higher complexity and larger forensic surface. Do not choose B implicitly.

**OWNER DECISION — APPROVED:** **I4-D01 = A**, confined to first-language laboratory. Existing I3 schema-4 operation and manually requested P04 remain unchanged; native Assembly-enabled experimental execution must fail closed on any conflicting P04 intent.

## Decision I4-D02 — production schema history/migration policy

**Problem.** I3 schema-4 holds learned W, event journal and P04 records but no native Assembly registry, structural generations, member reverse index or canonical root-close native FORM payload. Simply adding `Cell.assembly_ids` would break existing graph_codec and replay-integrity validation. Schema-3 is already rejected.

**Option A — RECOMMENDED for initial first lab:** introduce explicitly versioned **schema-5, fresh-DB only**, containing full canonical native W/RootStore/Assembly journal. A new R02 lab starts from empty schema-5 W and learns all six LOCAL edges through real I3 external roots, then FORM at a legitimate END. Old schema-4 and schema-3 databases are NEVER modified/dropped/automatically upgraded: R02 loader refuses with `UNSUPPORTED_PRODUCTION_SCHEMA`, documents upgrade not supported yet, and retains reproducibility via the pinned merged I3 source. Before any production/public deployment or reuse of actual old journals, require a separately approved, exact audit-preserving schema-4→5 import/migration contract.
Advantages: clean scientific experiment, minimal risk of corrupting existing evidence; fast research path. Cost: existing schema-4 saved knowledge cannot be used by I4 until migration.

**Option B — more conservative for existing data but larger project:** make migration from real schema-4 journal to schema-5 a hard prerequisite of native FORM. Requires full historical checkpoint and root-chain transform, verified old-source hashes, rollback after crash, old P04 recycling semantics and audit replay. This may delay or confound the first actual Assembly-birth experiment.

**OWNER DECISION — APPROVED:** **I4-D02 = A**, strictly for NEW experimental schema-5 databases. Never convert/drop/modify existing schema-4 or schema-3 database files. Old data migration and public deployment compatibility remain separately gated. Existing I3 schema-4 RootStore behavior remains available in its original explicitly distinguished mode.

## Sequencing scope (already established in R00 review)

**D03 staged implementation:** R02 implements one native **FORM** on an initially empty Assembly registry; R03 subsequently adds MAINTAIN/GROW, R04 adds MERGE/SPLIT. Core §2.0 specifies full operator order. To avoid silently claiming full §2.0 during R02, the constrained first-FORM lab may allow an END while no LIVE/ARCHIVED Assembly exists and a single first Assembly can be legally formed, but **must fail closed on any later END that would require unimplemented MAINTAIN/GROW/MERGE/SPLIT**. Do not claim R02 provides the complete steady-state END runtime. R03/R04 remove these laboratory gates only after independent acceptance.

**D04 dependent Attractor:** retain NOT_RUN until a real pre-existing, cold-restored LIVE Assembly has been proven; no fixture upgrade.

## Exact research starting point

I4-R01 genuine ROOT4 EVENT5/order0 already demonstrates one legal hypothetical triangle `(8606,9345,11795)`, with six directed CONSOLIDATED LOCAL links, all Q=.3, three R=.3, degree=2, density=1, specificity=2/3, direct committed-before-event witnesses, final A=.7266155086363637 and frozen theta_emit=.253. This **does not** authorize reusing a past R01 read-only decision as native FORM authority. R02 must recompute from the actual current root's post-evidence W shadow and original trusted EVENT journal, within atomic END.

**OWNER AUTHORIZATION RECORDED (2026-10-31):** The project owner explicitly approved both D01=A and D02=A and continuation, including the staged R02 FORM-only laboratory containment. The I4-R02 implementation contract may now be marked AUTHORIZED. All additional scientific operators and data migration remain outside this authorization. Core and LLA RC4.4 are unchanged.
