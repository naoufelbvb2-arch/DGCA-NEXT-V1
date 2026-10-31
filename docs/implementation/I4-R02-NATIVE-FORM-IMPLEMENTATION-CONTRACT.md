# DGCA NEXT — I4-R02 First Native Assembly FORM — Approved Execution Contract

**ID:** I4-R02-NATIVE-FORM-IMPLEMENTATION-CONTRACT
**Revision:** APPROVED-R02 — 2026-10-31
**Status:** **OWNER APPROVED — AUTHORIZED FOR CODEX EXECUTION. I4-D01=A, I4-D02=A AND STAGED FORM-ONLY FIRST-LANGUAGE EXPERIMENT. NOT SCIENTIFICALLY FROZEN AND NOT IMPLEMENTED UNTIL VERIFIED.**
**Repo/branch:** naoufelbvb2-arch/DGCA-NEXT-V1 / feature/i4-native-assemblies-design
**Main baseline:** 88fc596c178c8a89c24b991e280d7a0ca8c07779
**Accepted read-only R01:** b063b0051be452b83f74081572ba3af2d685d7f5 and I4-R01-INDEPENDENT-ACCEPTANCE-REVIEW.md
**Approved engineering decisions:** docs/design/I4-R02-D01-D02-OWNER-DECISION-PROPOSAL.md
**Scientific authority:** CORE RC4.4 §2.0 and §10.2 + LLA RC4.4; unchanged candidate papers, no scientific freeze.

## 0. Mission and hard eligibility

Implement a genuine **production Native Assembly FORM** at a lawful external LEARN root's atomic END, using the six real independently learned, reciprocal, CONSOLIDATED LOCAL synapses observed in R01. The first successful root must produce exactly ONE live size-3 Assembly record with actual unique ID, sorted real members (8606,9345,11795), birth_close_serial at that root's completed close, structural_generation, physical membership back-reference and reverse member index, and verified persistence. No FixtureBuilder, AssemblyFixture, fake reciprocal completion, expected output label, pretrained/hand-constructed W or direct injection of Assembly record.

**Critical:** No R01 `inspect_form_eligibility` read-only diagnostic or caller-submitted triangle may authorize physical FORM. Recompute eligibility inside the trusted *same-root END* shadow AFTER real I3 _settle and use historical event-time original direct witnesses, pre-event commitment, original frozen theta_emit and activity. Same-root newly consolidated link may enable structural FORM, but newborn Assembly cannot claim any event from this root as a *past existing Assembly* or receive retrospective peripheral surface confirmation.

This is a **one-Assembly FORM research vertical slice** and not full Core §2.0 MAINTAIN/GROW/MERGE/SPLIT or Attractor. Full I4 remains PARTIAL. Do not merge main, enable P04/automatic recycling in native mode, change RC4.4 laws, or start I4-R03 until independent review.

## 1. Approved D01/D02 execution boundary

**Owner authorization is recorded (2026-10-31):** I4-D01=A (I3 P04/manual rewiring and I4 native assembly END mutually exclusive, with audited mode/capability distinction) and I4-D02=A (fresh experimental schema-5 only; schema-4/3 DBs fail closed without modification). The staged FORM-only lab containment is approved. Implement these exact policies. The merged I3 schema-4 interface retains its original P04 behavior, preserving all accepted I3 tests and old data byte-for-byte.

**Explicit owner approval has now been recorded in the approved decisions document and this contract.** Codex is authorized to implement R02 within this scope only. Any expansion to full MAINTAIN/GROW/MERGE/SPLIT, schema-4→5 migration, simultaneous P04+native FORM, Attractor, readout or language generation still requires independent later review and authorization.

In fresh schema-5 native laboratory mode, reject P04 requests before they can be staged or before END; not only after evidence publication. Reject a malformed/tampered saved root with competing P04 intent. There is no automatic periodic rewiring. Preserve old schema-4 databases byte-for-byte and reject opening them from schema-5 API with stable error. A later migration/import is separately gated; do not claim compatibility.

## 2. A: structural identity and production codec

Add immutable, trusted, nonsemantic `NativeAssemblyRecord` with fields (assembly_id, LANGUAGE region, sorted unique member_cell_ids, structural_generation, birth_close_serial, last_mutation_close_serial, last_merge_split_close_serial, status LIVE/ARCHIVED). Use exact CORE §2.0 fields/ranges. Assembly IDs must be monotonic never-reused per-region; do not rely on `max(LIVE_ID)+1` after archive. Record `Cell.assembly_ids` membership set (max 12) and a separate sorted member→AssemblyID reverse index, with bidirectional audit and original committed physical Cell/slot/synapse provenance unchanged.

Extend canonical production W graph schema to **schema-5 experimental** and include: Assembly registry, high-watermark, member reverse index, complete original I3 W with LOCAL/ASSOC learned link credits, assignments, recycling journal (empty in enabled native mode), canonical rooted FORM birth provenance and immutable source root/event witness reference, versioned hashes and precise schema rejection. Do not introduce semantic labels, textual tokens, generation words or hidden cell role annotations.

Cold encode/decode and graph transitions MUST reject duplicate/reused IDs, a LIVE Assembly size<3/>16, uncommitted/fixture/bad-region members, candidate/nonconsolidated/one-way LOCAL structural support, violated min(Q_fwd,Q_rev)>=.10, wrong origin/committed-before-event, inconsistent Cell.assembly_ids, wrong reverse membership, bad capacity, tampered birth root/event, wrong structural_generation, missing journal record and mismatched code/config/source hash. Archive preserves ID in registry and never recycles it.

**Full-end validation nuance:** An old valid Assembly can later lose eligible structural links, requiring MAINTAIN/ARCHIVE in later full I4; since that operator is unimplemented during R02, fail-close BEFORE a root can publish any post-close W that would leave existing Assembly invalid. Do not silently drop an Assembly, or claim a full steady-state implementation.

## 3. B: exact pure FORM operator, now with trusted root END

Reuse R01 `assembly_support.py` to compute actual current post-evidence W* reciprocal support and d/D/whole-region Spec. Use original event journal preserved by RootStore to validate external direct OBS_ELIGIBLE committed-before EVENT witnesses and event-frozen A^+>=theta_emit, not copied RootStore inspector output. Derive eligible U_t across actual root events in ascending event_order. Exclude already covered live Assembly members when CoreCoverage>=.70 and members at M_max. Enumerate triangles by reciprocal adjacency intersections, sorted (i<j<k), reject same-root duplicate overlapping FORM vertices, at most 12 proposals per END, requiring d>=2,D>=.70,Spec>=.30 on all 3, theta_A=.10, no wrong or speculative support. One chosen 3-cell triangle gets a trusted shadow Assembly record; unrelated neurons/links remain untouched.

R02's lab-first milestone requires at most the first ONE Assembly birth. If 4 eligible cells yield four candidate triangles, choose exactly the lexicographically first one at first qualified root EVENT, leave remainder as `FORM_VERTEX_ALREADY_ASSIGNED`. The effective cap K_FORM_PER_END=12 remains unchanged; do not replace it by a normative cap 1. The observed four-cell case yields one seed because of disjoint vertices, not because of a fabricated limit.

**Explicit staged-operator policy:** The initial root begins with empty Assembly registry; hence MAINTAIN/GROW/MERGE/SPLIT have no preexisting entities to process and the first triangle creates only one 3-member Assembly on that single END. Subsequent native-mode END capable of changing an existing Assembly state MUST fail closed with a precise `I4_UNIMPLEMENTED_MAINTAIN_GROW` (or earlier stage) until R03/R04 implement Core's full operator pass. BEGIN/read-only inspection and independent cold reload remain available without mutating W. Do not claim operator-complete native END or silently skip required future stages. Existing legacy I3 schema4 RootStore learning continues independently under original mode.

## 4. C: atomic publication and forensic replay

END native mode must execute:
1. Validate still-OPEN external root, genuine ordered EVENTS and original frozen W/H/witnesses.
2. Stage ordinary P02/LLA full-precision q/y settlement and accepted link evidence FIRST in one immutable WpostEvidence shadow, including same-END transition from CANDIDATE to CONSOLIDATED. No external q/S/E/count before END.
3. Run actual FORM eligibility on WpostEvidence using event-time genuine frozen E/X/A/H from that root. No fabricated cross-region links, no retroactive attestation, no readout surface.
4. If a legal seed exists, create first AssemblyID and all member/index/generation/birth records simultaneously, with birth_close_serial exactly the prospectively committed real completed close serial. Validate entire graph. Otherwise complete normal root and return `NO_RECIPROCAL_TRIANGLE`/ `NO_QUALIFIED_FORM_EVENT` without allocating an ID.
5. Commit W/H/closed R/root COMPLETED, accepted link ledger, Assembly journal, registry/high-watermark/index and root-close checksum in ONE existing SQLite transaction.
6. Verify across cold restore by re-deriving each prior physical evidence settlement and each FORM update under the corresponding original event snapshot and pre-close W, not by loading a prebuilt Assembly record as proof. Duplicate END/replay never double-creates Assembly or consumes a new ID. ABORT before END never credits q, creates an Assembly or increments completed-close serial.

Subprocess exit before/after END commit and corrupted schema/journal/membership must fail atomically. Absolute W/H/root and close serial must be reproducible. Preserve I3 P01-P04 learned-link persistence/causal Q effects and no read-only W/H/Assembly mutation.

## 5. D: exact from-zero first native Assembly proof

Create an actual new schema-5 production DB with zero committed cells, zero synapses and zero Assembly records. Use ONLY genuine `RootStore.begin/event/end` and canonical `(("a","1"),)` input:
- Root 1 sensory birth [8606,9345,11795,12181], no synaptic evidence or FORM.
- Roots 2/3 ordered input: all 12 ordered LOCAL keys among those four remain CANDIDATE (E_ext 1, then 2); NO native Assembly; no artificially injected links.
- Root 4, genuine EVENT IDs 5/order0 and 6/order1: six chosen keys CONSOLIDATED S=1/E_ext=3/Q=.3/root counts 3, three R=.3, all three candidate members genuine direct X_fixed=1e6, event5 frozen final A=.7266155086363637 and theta_emit=.253, d=2,D=1,Spec=2/3. END emits **one real LIVE Assembly** with exactly [8606,9345,11795] and audited birth ID/generation/member reverse index. No birth-root surface attestation.
- On cold restart the same Assembly ID/generation and learned synapses persist; the previously independent R01 pure inspection remains possible against original root history but no longer an authorization token.
- A one-way/CANDIDATE-only/ASSOCIATIVE-only link or event lacking real witnessed participation must not FORM; a completed root with no seed creates zero Assembly ID, no counter drift.
- Show no root=4 duplicate END double births, no Assembly from synthetic q/oracle or read-only/generate/replay, and no stale archived ID reuse (component-simulation for archive only until R03).
- Measure runtime/memory/SQLite growth, and distinction between a real native FORM pass and peripheral outbox/Attractor/lexical generation all NOT_RUN.

## 6. Gates and validation

R02-G01 TRUST: original real RootStore external EVENT origin, exact frozen before-commit/frontier and no fixture upgrade.
R02-G02 PHYSICS: six distinct LOCAL CONSOLIDATED directed keys, post-evidence Q reciprocal d/D/Spec and correct event-first seed.
R02-G03 IDENTITY: unique monotonic native AssemblyID and typed LIVE size3 structure in W, durable per-cell membership and inverse map, no semantic role.
R02-G04 ATOMICITY: true END publication of synaptic settlement plus Assembly in same transaction; crash/ABORT/duplicate END zero phantom effects.
R02-G05 PERSISTENCE: canonical schema5 with replay audit/corruption rejection, schema4/3 fail closed without touching files; I3 schema4 interface unchanged.
R02-G06 NEGATIVES: missing reciprocal, candidate/episodic, no direct witnessed emitter, prebirth, unsupported cross/modal, no disjoint capacity, tampered journal all refuse FORM.
R02-G07 REGRESSION: preserve 729 existing I0–I4-R01 tests, unchanged RC4.4 scientific hashes, Ruff/format/mypy/pip/verify-specs, final-head Windows+Ubuntu CI.
R02-G08 REPORT: actual physical/root/Assembly IDs/generation/first-eligible event, W/H hashes, saved graph identities, full output and NOT_RUN operator scopes.

Retain and rerun original 729 regression tests and add clear R02 tests; no hardcoded success assertion outside the test harness, no code-level expected Y labels. Commands:
`python -m pytest -q --basetemp=.pytest-tmp -rs`;
`python -m ruff check .`;
`python -m ruff format --check .`;
`python -m mypy`;
`python -m dgca_next verify-specs`;
`python -m pip check`;
`git diff --check`; `git status --porcelain`.
Final HEAD Windows+Ubuntu CI must PASS, not previous R01 head.

## 7. Deliverable and stop

Produce `docs/implementation/I4-R02-NATIVE-FORM-VERIFICATION-REPORT.md`: exact files/commit SHA, true root/event IDs, physical six links/each Q/E/S/count, original frozen witness and post-evidence proof, AssemblyID/generation/members/inverse index, actual transaction integrity/cold replay, schema version and old-data refusal, tested no-FORM negatives, local commands and head-matched CI, operator scope exclusions and each G01-G08.

`I4-R02 REVIEW READY` only if at least one genuine first Native Assembly has ACTUALLY been atomically FORM-ed from I3 learned links, saved/reloaded and accepted all gates. Otherwise `I4-R02 PARTIAL/SPEC_BLOCKED/EMPIRICAL_BLOCKED` with full physical evidence; zero fabricated native identity. Stop and request independent review, no R03, I5, native Attractor, text readout, generation, automatic recycling, main merge or silent science edits.

**ACTIVATION NOTE (2026-10-31):** AUTHORIZED by explicit owner acceptance of D01=A, D02=A and staged FORM-only first-language containment. Scientific sources unchanged; implementation and R02 final-head verification remain NOT_RUN. Stop for independent review when finished.
