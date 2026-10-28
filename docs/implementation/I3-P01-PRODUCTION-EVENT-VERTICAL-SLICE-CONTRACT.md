# DGCA NEXT — I3 P01 Production EVENT Vertical Slice

**Document ID:** I3-P01-PRODUCTION-EVENT-VERTICAL-SLICE-CONTRACT
**Revision:** R01 — 2026-10-28
**Status:** AUTHORIZED EXECUTION INCREMENT — NOT ACCEPTED UNTIL VERIFIED
**Repo/branch:** naoufelbvb2-arch/DGCA-NEXT-V1 / feature/i3-local-learning
**Verified baseline:** 017455554622800a9d9a2556f5ee7588831c81cc (640 PASS; final-head Windows+Ubuntu CI SUCCESS)
**Only authoritative science:** DGCA_CORE_RC4_4.md and DGCA_LLA_RC4_4.md (DESIGN CANDIDATE, NOT FROZEN, NOT EMPIRICALLY VERIFIED)
**Owner approval:** I3-S01/S02 and full I3 scope are already approved. No new scientific decision is requested by this implementation increment.

## 1. Engineering decision: stop rewriting broad I3 scopes, implement one VERTICAL SLICE

This increment MUST demonstrate the exact integrated path:

**Empty durable W/H/R → BEGIN_EXPOSURE → genuinely accepted ordered external EVENT → canonical SIC observation → frozen pre-event W/H/R → actual I2 two-pass → immutable external ingress witness + event trace → approved S01 K_new real sensory birth → L01 24-slot topology/reverse-index → approved S02 sparse H default/adaptation → atomic persisted EVENT checkpoint with next_order=1 → restart → reloaded W/H/R/event witness → ABORT → H_BEGIN exact-byte restoration, with legally retained W-born cells.**

Do **not** implement END, q/E/S evidence publication, learned synapse formation, native Assembly, owner, generation, Replay or automatic production recycling in P01. END must keep rejecting. A reviewer must be able to execute a literal production API call EVENT that no longer raises I3-R02 on valid first-LANGUAGE input, persists actual graph cells and their latent topology, and survives process restart. Pure unit helpers/preflight checks alone do not satisfy this increment.

After P01, I3 remains **PARTIAL**, not I3 REVIEW READY. Subsequent separately contracted P02 will implement witnessed LOCAL/ASSOC proposals and atomic END; P03 persistence/consolidation and cold-start evidence, P04 novelty/recovery closure. Those are a PLAN, not additional scope in this task.

## 2. Existing barriers, located in source (must be fixed without fixture laundering)

- src/dgca_next/persistence/store.py: RootStore.event currently validates raw SIC then unconditionally raises SpecBlocked("I3-R02"); RootStore._validate_store requires W=EMPTY_W and R=R_COLD; schema supports only OPEN/ABORTED with next_order=0.
- src/dgca_next/graph/cell.py: committed=true requires fixture_only=true; production sensory commitment requires a genuinely different audited non-fixture provenance.
- src/dgca_next/graph/network.py _Editor, FixtureBuilder, initialize_cohort and src/dgca_next/graph/policy.py FixtureEventSnapshot are fixture-only. A production implementation must not manufacture fixture witnesses or call FixtureBuilder.
- src/dgca_next/graph/synapse.py: only fixture-only records currently exist; **do not relax production synapse schema as part of P01**. P01 creates no learned synapse. Sketch the future root-authorized mutation boundary without making it public.
- src/dgca_next/dynamics/session.py: read_only_step is READ_ONLY, not a valid external witness engine. Reuse I2 PURE two-pass numerical operators and legitimate snapshots to construct a separate typed LEARN event trace, never relabel read-only provenance.
- src/dgca_next/learning/homeostasis_profile.py: LanguageHomeostasis profile and sparse overrides already exist but are not connected to RootStore. Preserve exact RC4.4 g=1.0, rbar=.05, LANGUAGE regional EMA=.030, theta_active=.20; do not permit caller-supplied production profile tuning.
- src/dgca_next/learning/observation.py: preflight is pure and correct for S01 but is not external witness authority.
- src/dgca_next/persistence/codec.py: currently H-only; implement production W and event R/journal codecs and strict schema/version/hash validation; no unversioned pickle or lossy float json.

## 3. Authoritative production ingress and immutable observation

Only RootStore's controlled OPEN-LEARN path may create a non-fixture **ExternalEventObservation** with (strictly increasing exposure_id, event_order, unique global event identity, actual caller supplied canonical SIC projection digest, X_fixed and salt/config/source digests, EXTERNAL_DIRECT origin, pre-event committed physical IDs and W hash, fixed pre-event H version, real I2 causal lane trace, pre-current-SIC P_T and frozen activity). The event's data come from the actual validated call, not a fixture factory, guessed transcript, expected answer, label, or replay.

The engine cannot verify that caller-supplied feature text describes real-world truth; "external" is an API provenance designation, not human-certified semantic truth. Reject malformed support/feature, wrong root/order, inconsistent optional boundary, unauthorized read-only/replay entry and any mismatch. Never allow an arbitrary user-supplied witness object to mint training authority.

For event 0, BEGIN has already enforced R_cold and no preceding root A/F/μ. Freeze W/H/R before any K_new commitment. Produce a REAL I2 two-pass trace for actually committed pre-event cells, keeping independent observed X on uncommitted receivers as sensory input without implicitly activating or committing them mid-pass. Fully qualified future link proposals and q are out of scope in P01; journal all necessary source/target activities, frozen F_step, pass1 E and direct observation proof for P02.

If I2 lacks a lawful production API for pure LEARN numeric step, create an internal, correctly typed function that uses the existing I2 numeric kernel and legal event-origin controls; avoid copying neural equations into an independent second engine.

## 4. Real sensory commitment on EVENT close

Use S01 deterministic integer-millionth selector from current durable W: rank (-X_fixed,cell_id), max 12 since I5 contextual admissions are OFF. Freeze the *whole* K_new cohort before construction, initialize its L01 24-slot layout with ordinary fixed LOCAL/topographic plus ranked legal empty coactive slots and exact reverse index in one verified graph shadow. Do not call FixtureEventSnapshot, FixtureBuilder, or any fixture-only write API in production. Implement non-fixture cell commitments with immutable REAL admission provenance and a single monotonic **global event identity distinct from per-root event_order**; do not repurpose per-root order=0 as global age/identity. Preserve existing fixture-only tests, audited structural invariants and public read-only snapshots unchanged.

Key experimental examples:
- Empty graph, (("a","1"),) projected physical LANGUAGE receiver IDs [8606,9345,11795,12181]. First accepted production EVENT commits exactly these 4; no learned synapses; stored W survives a new RootStore process.
- Empty graph, features a/ab/c/d all 1 project 16 distinct IDs, accept the known 12 ID-ranked cohort [8286,8465,8606,8649,8694,9227,9345,9902,9912,10128,10273,10513] and report four exact deferred IDs [11524,11641,11795,12181]. After a valid ABORT (permitted births remain), a distinct NEW root seeing the same input may accept 4 remaining, not rebirth the first 12.
- Invalid EVENT leaves durable last checkpoint, W/H/R and next_order unchanged; no partial latent slot/reverse-index edits.
- Single EVENT may carry no accepted newborns: persisted event index and witness still advance exactly once, no phantom births.

NOTE: test the actual legitimate authority path, not a saved fixture graph masquerading as production W.

## 5. Approved H_slow virtual newborn defaults, exact ABORT

Cold production store must initialize only the approved versioned DGCA-H-LANGUAGE-V1 profile. H raw bytes and profile hash are stored with schema identity. Materialize default g=1.0 and rbar=.05 for committed-before-event cells into temporary immutable explicit H snapshot for I2 numeric computation. The durable profile has sparse per-cell adaptation overrides; a newly born cell gets no override from its birth EVENT and is absent from that event's S03 firing denominator.

Execute adaptation of the actual pre-event population via RC4.3 S03 only after numeric two-pass, and persist event-level H_EVENT *provisionally* in the same atomic EVENT transaction as W/R and next_order. If K_r empty, regional rho_bar and theta remain unchanged. Birth does not reset existing adapted shared theta/rho_bar. On ABORT restore EXACT raw H_BEGIN bytes; lawfully committed sensory W cells remain and their missing H overrides are resolved using the frozen approved profile. BEGIN/ABORT must remain idempotent under restart.

Do not lose previous legitimately completed H overrides when later independent roots abort. P01 has no completed roots yet; preserve extension schema/semantics and document the future P02 test obligation.

## 6. Persistence architecture and atomicity

Use existing SQLite local store, with one transaction for each BEGIN/EVENT/ABORT publication. Implement a versioned canonical encoding for *actual* production graph W physical commitments, initialized latent slots, reverse indices, initialization metadata, graph identity and provenance; plus event R state, frozen temporal/frontier traces and immutable typed observation journal records necessary for future evidence and P02. Do not use debug_dump/structural_hash as the only W serialization. Decoding must re-run existing graph invariants; reject unsupported schema/config/RC4.4 hashes/latent policy and corrupted record before exposing state. Float values must retain defined binary64 and SIC fixed-millionth precision.

Test reload from a distinct connection, cold read-only snapshot of newly committed W, same-event retry/out-of-order duplicate and subprocess SIGKILL/os._exit just before/after database commit. On interrupted commit recover exactly pre-event state OR entire post-event state, never partial W with different R/H or an orphan witness. The accepted event order must be durable and not recomputed on restart. Database-level BEGIN IMMEDIATE and interconnection exclusion remain mandatory.

You MAY version the provisional I3-R01 SQLite schema as a deliberate new schema with tests that reject unsupported old files; a compatibility upgrade is not required before public release, but do not silently treat old H-only skeletal stores as new production stores.

## 7. Acceptance tests and exact stop condition

**P01-G01:** Actual non-fixture production EVENT accepted (one user-provided external feature event), next_order advances from 0 to 1 atomically, and typed observation exists.
**P01-G02:** Cold 4-birth and 16→12 birth tests create actual committed cells, 24 slots, exact reverse-index audit; 0 learned synapses/0 root confirmations.
**P01-G03:** Frozen pre-event W/H/R feeding existing I2 two-pass; event trace and provenance are derived from real external input, not fixture/read-only promotion.
**P01-G04:** Newborn Homeostasis virtual defaults, no same-event adaptation, and H_BEGIN raw-byte restoration on ABORT despite persisted W newborns.
**P01-G05:** W/R/H/journal serialization round-trips, reopening OPEN root after EVENT resumes expected order and retains exact snapshot.
**P01-G06:** Process-crash before/after EVENT commit, atomicity/idempotency, corrupt-schema/load rejection; no q/S/E/count/root completion.
**P01-G07:** Preserve all 640 prior I0–I3 regressions, RC4.4 source hashes unchanged, Ruff check+format, mypy, pip check, Ubuntu/Windows CI at final pushed head.
**P01-G08:** Precise report PASS/FAIL/NOT_RUN/SPEC_BLOCKED with actual event/root/physical cell trace, no premature learning claim.

Mandatory new tests use **RootStore production API**; a pure preflight, simulated graph, FixtureBuilder mutation, fabricated EXTERNAL witness or monkeypatch to bypass RootStore.event CANNOT satisfy P01-G01/G02.

Execute exact commands:
python -m pytest -q --basetemp=.pytest-tmp -rs
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m dgca_next verify-specs
python -m pip check
git diff --check
git status --porcelain

GitHub Actions Ubuntu+Windows must succeed on the **last delivery SHA**.

**Deliverable report:** docs/implementation/I3-P01-PRODUCTION-EVENT-VERIFICATION-REPORT.md — provide changed files/commit, root 1 EVENT 0 actual saved W/latent/inverse/H state, raw H_BEGIN and H_ABORT hashes, emitted physical IDs and SIC X_fixed, event trace, high watermark and next order, failure cases, actual crash recovery, command output, final-head CI, all P01 gates, and precise deferred P02 END/evidence work.

**Repository governance:** branch feature/i3-local-learning only; no changes to main, no merge, no RC4.5, no new science values, no Native Assemblies/Owner/Generation. Commit/push only implemented P01. Stop at **I3-P01 REVIEW READY** if all P01 gates pass; else **I3-P01 PARTIAL** with exact blockers. Do not declare full I3 complete and do not begin P02 before review.
