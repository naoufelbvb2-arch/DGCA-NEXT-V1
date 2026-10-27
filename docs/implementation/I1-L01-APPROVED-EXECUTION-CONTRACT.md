# DGCA NEXT — I1-L01 Approved Remediation Execution Contract

**Revision:** I1-L01-EXEC-R01
**Status:** AUTHORIZED FOR CODEX IMPLEMENTATION ON I1 BRANCH (I1 REMAINS POLICY_BLOCKED UNTIL VERIFIED)
**Owner approval:** 2026-10-27
**Base verified source:** `1de0de43cfc634fb5e00ed175c121d749b779c41` (314 PASS, 2 POLICY_BLOCKED skips)
**Working branch:** `feature/i1-graph-anatomy`
**Source decision:** `docs/implementation/I1-L01-LATENT-POLICY-RESOLUTION-PROPOSAL.md` (now approved for controlled incorporation).
**Normative target:** exactly two integrated Core/LLA documents, revision **RC4.2**, no third normative rulebook.

## 0. Mission and stop conditions

Implement **the approved L01 latent initialization and recycling safety policy** within the existing I1 Graph Anatomy subsystem; do not start I2. Verify correct physical topology, reverse indexing, permissions, deterministic co-birth ranking, and safety of dynamic slot replacement. Do not claim genuine novelty detection, sensory learning, reinforcement or actual Assembly formation.

**Never change scientific constants to pass a test.** When a necessary value/rule cannot be taken from the approved proposal, historical original and existing two documents, stop only that subgate and report `POLICY_BLOCKED`. Do not invent new heuristics or globally scan external words.

## 1. Required scientific-document migration (first, on the same feature branch)

- Convert *the existing* `docs/specs/DGCA_CORE_RC4_1.md` and `docs/specs/DGCA_LLA_RC4_1.md` into the approved **RC4.2** contents, retaining exactly TWO normative science files. Preferred repository filenames remain unchanged initially to avoid stale paths in I0 tests, but the **internal revision and status must explicitly become RC4.2**. Better, if changing filenames, make the entire path/hash/code/README/test migration one atomic, audited commit with exactly two authoritative files and archival versions accessible in Git history. Never leave a half-migrated branch presented as complete.
- The **content of RC4.1 must remain recoverable byte-for-byte from the parent Git commit**, and the change diff must be section-limited and explain what was superseded. Do not rewrite independent RC4.1 laws.
- Core §1.3 owns the executable slot selection, fixed LOCAL/topographic mapping, co-birth event timing, duplicate handling, reverse index, age, bilateral recycling, protection and error states.
- LLA §5 and event-root execution own the **external observation/provenance gate** for dynamic coactive candidates and local novelty, including the proposed residual measure. No new external evidence, q, S or E is created by wiring or recycling.
- Use the approved proposal's byte-exact topographic hash domain and salt; calculate *golden vectors* from the specification and hard-code expected outputs in tests (not code-dependent computed expectations). Coactive rank from Q6 external support/final real pass observations as specified; never use evaluator labels, semantic words or predicted-only activity as a real co-birth witness.
- Recycling confirmation **W_conf=100 completed genuine external root closes**, not 100 steps, not age of synapse, and not 100 aborted/open/scratch sessions.
- Approved experimental novelty formula in event-local form:
  `nu(u,t)=max(0, X_ext(u,t)-min(X_ext(u,t),P^T_u(t))) / max(X_ext(u,t), 1e-6)`
  for directly observed valid external receiver u; otherwise 0. The predictive drive is a frozen **pre-current-SIC** genuine runtime quantity, not a label or reconstructed target oracle. `theta_R=0.30`. This law is experimental, may frequently equal 1 with absent predictions and is not proven beneficial.
- In I1, define the typed verified-witness *interface* and pure guard/transaction only. Actual production automatic recycling MUST remain disabled until I2/I3 can supply genuine, validated, event/root-bound external witness; reject caller-asserted arbitrary floats as proof.
- Check compatibility of "fixed LOCAL/TOPOGRAPHIC always assigned" with lazy sparse address space and newly born contextual z at END; if a legal birth cannot be handled without invented sensory witness, document precise unresolved case instead of filling slots retroactively.
- Update `docs/specs/SOURCE-MANIFEST.md`, `src/dgca_next/integrity.py`, pinned I0/graph test fixtures and relevant README version references **coherently**. The I0 spec integrity CLI must PASS on both new bytes, and an old RC4.1 checkout must remain reproducible via its commit. Update `docs/implementation/I1-VERIFICATION-REPORT.md` or add a small I1-L01 re-verification report; never claim old 314 PASS applies to new files without rerunning.
- Record a single reviewed science-version transition (`RC4.1 → RC4.2`) in the Git history. Do not modify other repositories, do not merge.

## 2. Graph implementation requirements

- Maintain existing 24 typed slots `6 coactive intra + 6 local + (3+3) coactive inter + (3+3) topographic` and unchanged directed `D(i,j) = [j∈N(i) OR i∈N(j)]`.
- Co-birth group `K_new` is evaluated against one frozen canonical event snapshot. No intra-cohort iteration advantage, no same-root retroactive synaptic learning. With an absent real I2 event driver, test the deterministic selection as **pure explicit-input policy functions**, not synthetic "LEARN" achievements.
- Fixed LOCAL six targets: round-robin across own and clipped orthogonal microcolumns; physical IDs tie-break; different source/target regions forbidden; no self-target, no within-owner duplicate.
- Fixed TOPOGRAPHIC six targets: exact domain-separated SHA-256/u64BE/mod-4096 candidate and deterministic circular probe (three per other region); no Python `hash`, no reused SIC salt.
- Coactive six-intra and three-per-other-region: rank `(-Q6(support),cell_id)` on permitted *verified physical receiver/frontier candidates*; exclude owner, previously selected targets, forbidden provenance, and leave unused slots EMPTY rather than inventing random replacements. Respect pre-existing pinned contextual z slots and per-category target-region constraints.
- Dynamic slot recycling: only after at least 100 completed external closes, verified bounded novelty threshold, zero live edges/reservations/pins in **both** directions, and legal replacement for all affected occupied dynamic slots. No deleting protected knowledge; fixed slots never rotate. Perform bilateral reverse-index/wiring-log updates atomically with failure-injection rollback. No partial replacement or capacity double-charge.
- New transient witness/proof types used for I1 tests must be marked **fixture-only** and never accepted by production auto-recycling.
- Provide diagnostic statuses `UNVERIFIED_NOVELTY`, `CONFIRMATION_WINDOW_NOT_ELAPSED`, `RECYCLE_BLOCKED_CANDIDATE`, `RECYCLE_BLOCKED_LIVE_OR_PROTECTED`, `RECYCLE_BLOCKED_FIXED`, `NO_RECYCLING_REPLACEMENT` as applicable; preserve existing I1 APIs unless a scientific change requires a versioned adaptation.
- Reuse the existing immutable snapshots/in-memory shadow transaction model, physical-cell identities, outgoing caps and reverse index. No neural activation or experience evidence changes in I1.

## 3. Mandatory verification

Run **all 314 previously passing tests** plus the two previously skipped tests, replacing policy skips with real, narrowly scoped production-policy **physical** checks when feasible. Require:
- 12,288 physical identities / 24 slots / fixed and coactive quotas unchanged.
- L01-T01–T11 from approved policy, including deterministic co-birth, LOCAL border/center coverage, hash golden vectors on Windows/Ubuntu, ties/empty categories, no retroactive evidence, 100 close boundary, protected bilateral recycling, atomic replacement and no eligible replacement, null labels, reproducibility.
- Independently validate updated RAW SHA-256 and Git blob identities of BOTH specs; old RC4.1 hashes are archival, not active I0 test expectations after migration.
- Full regression: `python -m pytest -q --basetemp=.pytest-tmp -rs`, `python -m ruff check .`, `python -m ruff format --check .`, `python -m mypy`, `python -m dgca_next verify-specs`, `git diff --check`, `git status --porcelain`.
- CI matrix Ubuntu/Windows success **on final branch head**; clean Git status after committed validation.
- Report PASS/FAIL/SKIPPED/NOT_RUN separately. `314` is historic baseline, not a promised new test total.
- Scientific LLA-T01–T41 and LG-T01–T16 continue **NOT_RUN**; real residual-novelty LEARN integration remains **NOT_RUN/DEFERRED** until I2/I3.

## 4. Review disposition and implementation order

**Phase A:** Version the two scientific specifications together, inspect the diff and pinned hashes.

**Phase B:** Add pure fixed/coactive initializer selectors and golden test vectors; implement verified immutable event-cohort inputs; no access to raw word labels.

**Phase C:** Implement bilateral recycling age/protection checks, pure novelty interface and fixture-only replacement/rollback. Keep production auto-trigger OFF.

**Phase D:** Full I0/I1 regression + cross-platform CI + documented independent gate outcomes. Commit/push and stop at `I1-L01 REVIEW READY` if all mandatory *physical* policy tests pass; otherwise `I1-L01 POLICY_BLOCKED` with smallest counterexample.

### Explicit deferral decision

The owner has authorized **I1's structural completion even when the first REAL externally verified novelty trigger has not executed**, because obtaining `X_ext` and frozen pre-input `P^T` is properly an I2/I3 responsibility. This is **not** a permission to bypass fixture policy tests, invent evidence or mark production recycling active. State final I1 gates with the true deferral and require a later integration gate before experimental claims.

**Main stays unchanged until independent review.** Do not start I2 or unfreeze RC4.2 scientifically.
