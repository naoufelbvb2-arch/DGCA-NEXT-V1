# DGCA NEXT — I4-R03 Native Assembly MAINTAIN and GROW — Implementation Contract

**ID:** I4-R03-NATIVE-MAINTAIN-GROW-IMPLEMENTATION-CONTRACT
**Revision:** APPROVED-ENGINEERING-R01 — 2026-10-31
**Status:** AUTHORIZED FOR IMPLEMENTATION WITH STRICT STAGED LAB GATES; NOT YET IMPLEMENTED/VERIFIED
**Repo/branch:** naoufelbvb2-arch/DGCA-NEXT-V1 / feature/i4-native-assemblies-design
**Accepted I4-R02 code baseline:** c66eb570b03e7653d9fa1f16c1805d52ad5f9072
**Independent acceptance:** docs/implementation/I4-R02-INDEPENDENT-ACCEPTANCE-REVIEW.md
**Owner-approved staged I4 policy:** docs/design/I4-R02-D01-D02-OWNER-DECISION-PROPOSAL.md (D01=A, D02=A, D03 staged operators, D04 deferred native Attractor)
**Normative scientific authority:** EXACTLY docs/specs/DGCA_CORE_RC4_4.md and docs/specs/DGCA_LLA_RC4_4.md; DESIGN CANDIDATES, NOT FROZEN/NOT EMPIRICALLY VERIFIED.

## 0. Mission: first lifecycle of an ALREADY LEARNED native Assembly

R02 ACTUALLY publishes a native Assembly 0 GEN1 with members [8606,9345,11795] on genuine root-4 END. It then intentionally refuses a later native END with `I4_UNIMPLEMENTED_MAINTAIN_GROW`. R03 must remove that blanket refusal ONLY when the exact Core §2.0 **MAINTAIN then GROW** stages, real root close, persistence, mutation journal and later-operator safety conditions can all be discharged. It is NOT permission to skip FORM/MERGE/SPLIT under a generic no-op.

Primary positive experiment: NEW schema-5 RootStore DB, actual independent roots1–4 generate first real Assembly0 GEN1. On the next genuinely completed external root 5, use actual learned reciprocal physical fourth cell **12181** (not selected as original seed) and Core's GROW test. When its actual d/D/Spec and existing-member keep conditions pass, **GROW** Assembly 0 from 3 to 4 real members; increment structural_generation to 2 and last_mutation_close_serial to 5; persist original birth record unchanged, append a truly rooted mutation record, update per-cell assembly_ids/inverse for 12181, cold reopen and show identity/generation/learned Q preserved.

The experimental target is a falsifiable prediction, not a hardcoded add instruction. If genuine Core scores or candidate ranking do not permit the fourth member, report actual rejection and EMPIRICAL_BLOCKED; never insert a membership, fake an event, patch Q, retune thresholds or change input weights.

**Additional MAINTAIN requirement:** perform an authentic continued native root with a stable member set and zero structural changes. Implement exact lawful removals and archival for degraded cases; isolated component simulations may establish removal math, but only genuine production END (with real learned W and source trust) can establish production removal/archival. If no genuine degradation can be obtained without violating first-lab laws, report that subscenario NOT_RUN/EMPIRICAL_LIMITED, not a fabricated production archive.

**Excluded:** R04 actual MERGE/SPLIT, automatic recycling, schema-4→5 import, contextual owner/pins, readout/outbox, native Attractor, language generation, cross-region Assemblies and any new law. Full I4 remains PARTIAL.

## 1. Core §2.0 algorithms: deterministic, one pass per END

All operators run on a shadow after ordinary root link evidence has settled. Use inherited existing formula `R^B_{ij}=min(Q^LOCAL_{ij},Q^LOCAL_{ji})` only for two legitimate directed LIVE CONSOLIDATED LANGUAGE LOCAL links and `R^B>=theta_A=.10`, same real physical D and provenance checks. Whole-region specificity denominator includes EVERY legitimate reciprocal neighbor of that cell, not merely A.

**MAINTAIN**, for each LIVE Assembly ID ascending:
- Evaluate `d(x,A)>=2`, `D(x,A)>=rho_keep=.35`, `Spec(x,A)>=sigma_keep=.20` on current shadow live reciprocal graph; among failing members, remove the **LOWEST physical cell_id**, recompute all predicates, iterate until no violations OR |A|<3. Do not choose the worst score, last failed member or all failing cells at once.
- If |A|<3, ARCHIVE that Assembly and remove its LIVE membership references; DO NOT delete/modify underlying synapses or recycle its AssemblyID. Preserve immutable original birth and all structural edit history. Every actual change of membership increments structural_generation exactly once. Do not increment on a no-change close; archive transition must have an auditable generation/status disposition consistent with the Core. If the code exposes a genuine representation ambiguity for archived <3-member records, report SPEC_BLOCKED with exact Core text instead of silently preserving fake LIVE memberships.
- A member removed from a valid LIVE Assembly must be deleted from BOTH Cell.assembly_ids and independent member→AssemblyID inverse; the record's current member list reflects exact live structural membership. Archived memberships are historical journal data, never a currently live owner/pin.

**GROW**, each still LIVE Assembly ID ascending, while size<16:
- Enumerate candidate committed LANGUAGE cells from the finite reciprocal neighbors of CURRENT members, not all 4096 logical region cells and not the lexical input label. Exclude current members, blocked/unsupported/fixture cells, M_max=12 cells.
- Rank candidates by `(-sum_{j in A} R^B_{xj}, physical cell_id)`, with deterministic stable floating-point ordering consistent with Core. Inspect each candidate **once** in the ranked pass. On prospective A∪{x}, require `d(x,A)>=2`, `D(x,A)>=rho_G=.50`, `Spec(x,A)>=sigma_G=.30`; ALL existing members must satisfy MAINTAIN keep conditions on the prospective set; cap K_max=16. After adding one candidate, update W shadow, member index and structural_generation; no re-sort/revisit of already inspected candidate beyond what the normative algorithm allows. Never add links, root evidence or semantic role labels.
- Cell 12181 in the real four-cell fully reciprocal LANGUAGE W is a measurable candidate: it has 3 reciprocal neighbors of R=.3, rank from actual W; its prospective size-4 d=3, D=1, and Spec=1 if these are its only 3 reciprocal neighbors. Existing members' full-neighbor Spec should then be 1. Verify these values from graph at root5 and apply only if Core qualification really holds.

**FORM after MAINTAIN/GROW:** Core still specifies FORM after GROW at every END. R03 retains genuine R02 FORM from empty registry, with only its approved one-seed lab boundary and authentic root/event selection. On an already-live registry, compute whether any NEW independent seeds remain after current active Assembly coverage/CoreCoverage rules; if any would need formation beyond R03's approved lab scope, **FAIL CLOSED before publishing** rather than silently ignoring the required FORM stage. No post-GROW FORM duplicates may be created from covered members. At root5 with the four-cell cohort already covered by Assembly0, this is expected to create no new Assembly; verify actual original event-time coverage and projected U_t. Do not change the normative K_FORM_PER_END=12 limit.

**MERGE/SPLIT deferred:** Before publishing any END in R03 with multiple LIVE Assemblies or any size>=6 Assembly, run a **pure eligibility guard** against Core's inherited MERGE/SPLIT conditions, OR fail closed for all potentially affected configurations until R04. In every case, no transition that would legally require MERGE/SPLIT may publish an unprocessed close; report `I4_UNIMPLEMENTED_MERGE_SPLIT` with full pre-close OPEN W/H/root state preserved. A single LIVE Assembly size3 or size4 cannot MERGE (no second live) and cannot SPLIT (size<6), so the genuine root5 GROW scenario is safe. Do not claim full R04 implementation or create a bogus operator result.

## 2. R02 code constraints that MUST be corrected safely

1. `graph/native_assembly.py::validate_native_state` currently enforces `origin.members==record.member_cell_ids`, generation exactly 1 and last mutation at birth; R03 must distinguish immutable FORM birth `NativeFormRecord.members` from CURRENT membership and structural generation. Replace birth=current equality with an authenticated sequence of mutation transitions that replays from birth and validates every intermediate member set/generation/status.
2. `learning/native_form.py::_form_at_end` throws for ANY existing Assembly. Replace with a properly named native END operator pipeline, preserving the accepted first-FORM branch and adding real MAINTAIN/GROW, conditional deferred FORM/MERGE/SPLIT handling. No auto-apply of a stale R01 inspector diagnostic.
3. Existing `graph.validate_graph()`, ordinary I3 synapse `_settle`, and native codec audit may reject a temporary state where new ordinary evidence makes a member's specificity/structure below the MAINTAIN keep threshold. Build an **internally authorized, narrowly bounded physical-only pre/post-evidence shadow** or an equivalent carefully audited validation boundary that allows Core MAINTAIN to repair the graph within the SAME SQLite transaction, while requiring the published W to satisfy ALL final structural, inverse, root and codec invariants. Do not relax persisted final-state validation, do not rewrite W prehistory and do not let fixtures bypass trust.
4. Add a versioned canonical **NativeStructuralMutationRecord** carrying real identity, root/event authority, completed-close serial, operator stage MAINTAIN_REMOVE/GROW_ADD/ARCHIVE, before/after sorted members, generation, status, actual evaluated witness graph hash, relevant d/D/Spec, membership inverse delta and deterministic ordering. Keep immutable original `native_form_log` and old validated root/evidence. Journal may represent a whole ordered same-root mutation sequence but must preserve exact per-change provenance and generation increments. Never derive current members solely from a highest ID or ignore archived entries.
5. Choose either a backward-compatible, fully audited versioned W5 record extension with an explicit canonical schema evolution policy, or an expressly versioned schema-6 fresh lab with schema5 unavailable. **Preference:** preserve compatibility with the accepted schema-5 W if feasible; do not silently change canonical W bytes for already saved data or reject them without an explicit compatibility review. If unavoidable new schema migration or production record policy requires approval beyond accepted D02, stop `SPEC_BLOCKED` with exact reason rather than inventing data policy.
6. Ensure any new native structural mutation participates in completed-root replay verification, not just encode/decode and hash checks: recompute ordinary settled links and THEN all mandatory, ranked Assembly transitions from ORIGINAL root history. Validate final W, metadata high watermarks and complete mutation ledger. Re-running END, cold reopen or process-kill cannot double-grow, double-increment generation, lose members, or mis-credit roots.
7. Old `I3_SCHEMA4` mode and schema5 native mode separation remain unchanged. P04 remains rejected in native mode; no automatic recycling. Schema3/4 input to native mode remains fail-closed without modification.

## 3. Mandatory genuine production and negative experiments

**POSITIVE P1 — continuation + GROW:** From blank native DB use roots1–4 with `(("a","1"),)` to publish Assembly0 GEN1. Root5 BEGIN/EVENT/END truly completes without the old blanket `I4_UNIMPLEMENTED_MAINTAIN_GROW`, and GROW adds physical 12181 if exact measured candidate/keep guards hold. Assembly ID remains 0, generation becomes 2, last mutation close serial 5, four sorted members [8606,9345,11795,12181], one accepted rooted mutation and no extra FORM or new ID. Root5 ordinary q/E/S credit may update links in normal I3 way; do not claim Q remains numerically unchanged unless root5 lacks eligible proposals. Existing physical link keys remain lawful and learned, never replaced or injected. A sixth real completed root with no structural changes must preserve generation=2 and mutation ledger exactly; E/S may evolve only if actual new learning event is submitted.

**POSITIVE P2 — persistence:** Separate interpreter cold open retrieves exact Assembly0 GEN2 with current four-member Cell.assembly_ids/inverse, immutable initial FORM log GEN1 and rooted GROW log; complete historical replay audit reproduces W and H. A read-only episode cannot change generation/members/root credits, even when the existing Assembly is externally stimulated.

**NEGATIVE N1 — false recruitment:** no growth from one-way LOCAL, ASSOCIATIVE-only, CANDIDATE-only or missing physical latent D; no adding uncommitted, unsupported region, self, duplicate or membership-capacity-exhausted cell; full-neighbor specificity denominator must include real outside neighbors. Unit/component graphs are allowed to falsify arithmetic but NOT prove actual production growth.

**NEGATIVE N2 — MAINTAIN deterministic cleanup:** pure component scenarios show lowest-ID failing removal, iterative recomputation and archive when <3. Production MAINTAIN structural edits require actual lawfully changed post-evidence W and valid root event; do not fake consolidation loss by direct graph mutation and call it a production pass. A genuine stable root demonstrates MAINTAIN with no mutation. If an adverse genuine scenario is not reachable, label production removal/archive `NOT_RUN` and preserve it as a later explicit empirical gate.

**NEGATIVE N3 — deferred scopes:** if multiple new FORM seeds, any legally required MERGE/SPLIT, unsupported P04 request, unsupported contextual pins/reservation or ambiguous archive history appear, fail closed with exact named diagnostic and unchanged OPEN root/W/H. Never skip scientific operator or mark later subscopes PASS.

**NEGATIVE N4 — forensic:** birth journal unchanged; tampered GROW member, mutation ordering, generation skip, root serial, before/after W, reverse index, authorizing event and archival ID reuse must fail under canonical cold historical replay even if individual checksums are repaired.

**NEGATIVE N5 — crash and rollback:** inject real subprocess exit before/after END and ABORT; allow only complete OPEN or COMPLETE state, root close serial once, generation exactly once, no invented extra AssemblyID. Duplicate END idempotent. Old schema3/4 readonly unchanged, original I3 default mode regressions unchanged.

## 4. Test matrix, acceptance and governance

**R03-T01:** actual R02 Assembly0 GEN1 retained and independently audited after Root4, no changed values in accepted baseline.
**R03-T02:** actual Root5 witness and shadow E/S are authentic; real candidate 12181 evaluated by Core rank/d/D/Spec and existing keep conditions.
**R03-T03:** actual 3→4 GROW produces ID0 GEN2, last_mutation_close_serial5, unchanged birth log, exactly one rooted structural edit, no linked edge injection.
**R03-T04:** complete canonical W/member/inverse/mutation log and same-height root replay + separate cold process recovery.
**R03-T05:** sixth legal root no structural change gives stable generation and mutation log, no passive learning or ID drift.
**R03-T06:** exact MAINTAIN removal order and iterative recompute; legitimate ARCHIVE and no ID reuse tested at operator/codec level; label any missing production removal experiment.
**R03-T07:** GROW candidate ranking, membership cap12, max size16, prospective existing-member keep tests, no full 4096-cell scan or iterative convergence.
**R03-T08:** FORM chronology/disjoint/qualified event coverage after MAINTAIN+GROW; no R01 stale permission, no post-birth retroactive attestation.
**R03-T09:** deferred MERGE/SPLIT/extra FORM fails closed if required; no silent no-op, and original one-live size4 safe end works.
**R03-T10:** RootStore read-only/ABORT/duplicate END/exception/process-crash consistency for multi-episode native identity.
**R03-T11:** corrupt or forged birth/grow/archive/root/generation/member inverse/latest event rejected after repaired simple checksum.
**R03-T12:** old schema policy and original I3 P04 execution remain unchanged; P04 forbidden in native mode.
**R03-T13:** no actual Native Attractor/readout/owners/generation/automatic recycling, no native I4 final close.
**R03-T14:** preserve all **753** existing I0–I4-R02 regressions, unchanged RC4.4 hashes, Ruff check, formatting, mypy, verify-specs, pip check, clean git diff and exact final-head Ubuntu+Windows CI PASS.
**R03-T15:** report full actual physical/q/E/S/assembly/root/close serial trace, frozen event witness and post-evidence membership calculations, H/W digests, save/restart/crash evidence and operator coverage limits.

**R03-G01:** real root5 continuation after R02 birth under same source, no fixture paths.
**R03-G02:** exact MAINTAIN then GROW mathematical ordering with immutable birth versus mutable member registry, proper rooted generation ledger.
**R03-G03:** true physical source→fourth-member GROW, valid d/D/Spec and unchanged AssemblyID/synaptic provenance.
**R03-G04:** W/H/identity/index structural mutations committed and cold replay-authenticated atomically; crash/ABORT/double-END safe.
**R03-G05:** read-only/no-change stability plus explicit refusal of deferred operations and correct negative arithmetic.
**R03-G06:** old-schema/mode protection, no bypass of Core/LLA, no false native Attractor or readout.
**R03-G07:** all 753 regressions plus new tests, scientific hashes and final-head cross-platform CI.
**R03-G08:** transparent report with actual physical state and MAINTAIN removal empirical caveat, exact operator NOT_RUN scopes.

**Verdict:** `I4-R03 REVIEW READY` only with a real production 3→4 GROW, safe subsequent completed root, lawful MAINTAIN implementation and all scoped gates, no fake mutation. If positive GROW impossible, emit `EMPIRICAL_BLOCKED`; if Core/codec/deferred policy cannot safely be reconciled, `SPEC_BLOCKED`; otherwise `PARTIAL` with precise test evidence. Any production MAINTAIN removal/archive NOT_RUN must be explicitly separated from component tests; R03 can pass as a scoped MAINTAIN/GROW engineering slice only with a truthful qualification, NOT as full proven lifecycle science.

## 5. Deliverable and hard stop

Implement only on `feature/i4-native-assemblies-design`; keep main unchanged, no merge, no R04 or I5 code. Write `docs/implementation/I4-R03-NATIVE-MAINTAIN-GROW-VERIFICATION-REPORT.md`, list exact commits/files, traced actual root5/6 physical support and per-member d/D/Spec, before/after Assembly ID/generation/members/inverse, sorted mutation journal, W/H/SQL hashes, process-kill and tamper controls, test results and final-head CI, per-test/gate status and deferred MAINTAIN-ARCHIVE/MERGE-SPLIT. Preserve first accepted R02 trace and spec integrity.

Verification commands: `python -m pytest -q --basetemp=.pytest-tmp -rs`, `python -m ruff check .`, `python -m ruff format --check .`, `python -m mypy`, `python -m dgca_next verify-specs`, `python -m pip check`, `git diff --check`, `git status --porcelain`.

Stop with `I4-R03 REVIEW READY` only when real run/tests genuinely pass. Otherwise report exact `I4-R03 PARTIAL / SPEC_BLOCKED / EMPIRICAL_BLOCKED`. **No scientific FROZEN, no complete native END claims, no semantic/generation claims.**
