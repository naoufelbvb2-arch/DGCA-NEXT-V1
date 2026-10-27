# I1-L01 remediation verification

Date: 2026-10-27 (America/New_York). Target: **I1-L01 REVIEW READY** after the
physical-policy and final-head CI gates below. RC4.2 remains **NOT FROZEN / NOT
EMPIRICALLY VERIFIED**. No merge or I2 work is authorized by this report.

Repository: `naoufelbvb2-arch/DGCA-NEXT-V1`.
Implementation/delivery branch: `feature/i1-graph-anatomy` exclusively.

## Authorization, source transition and commits

The owner-approved proposal and execution contract authorize the coordinated
science migration, the physical mechanism, and explicit deferral of a real
novelty producer to I2/I3. They do not authorize synthetic learning claims.

| Reference | SHA |
|---|---|
| Starting approved-contract branch | `673451ca905911931c60e3bece47e37e0e3d1e7a` |
| Unchanged main / historical accepted I0 | `fdcd3ea3c85b9c7484e89d043188a59d49907b71` |
| Atomic two-spec RC4.2 migration | `511fe3e6f67cbf63004398bf2ac4f3b5ff2d2a7e` |
| Tested L01 implementation | `60be997c3eb5f39c6eb833f65bfaab0824be86c6` |

The report-only delivery commit is identified in the completion message and by
`git log -1 --format=%H -- docs/implementation/I1-L01-VERIFICATION-REPORT.md`.
It is not embedded in itself. Final-head CI is checked after this report is pushed.

The dedicated migration commit renames both sources together, updates their
revisions/status/companions, inserts the approved policy in Core §1.3 and LLA §5.1
with its §7.1 lifecycle clarification, and updates manifest/code/config/test/docs
references together. Its parent retains the exact original RC4.1 bytes. Tests
also verify those original hashes/blobs at the immutable accepted I0 commit,
without assuming RC4.1 paths remain present on a future `main`.

There are exactly two current scientific authorities, both RC4.2. The integrity
CLI rejects a stale third science file as well as source/manifest/hash corruption.
Independent regression assertions compare Core §1.4 onward and unaffected LLA
body bytes to RC4.1, proving unrelated scientific laws were preserved. Historical
reports/contracts retain their old results with a current-baseline notice; they
were not relabeled as executed RC4.2 evidence.

| Current source | Raw SHA-256 | Git blob SHA-1 |
|---|---|---|
| `DGCA_CORE_RC4_2.md` | `570570a2a57c3b859ed3745c8812711cf36de89a47be50bdbf5f415a1b8dbc59` | `5422a212abe21773a48c82b7f2ceaa34a9cd0a63` |
| `DGCA_LLA_RC4_2.md` | `47ad994cbda467ae1ce0ffd6c2868522f5502897f6c4d2d1f3ab68b69ac1df30` | `889025d76d70167de3070ffd8945878d37bf3dde` |

The old RC4.1 SHA-256 values remain archival and unchanged: Core
`f9d57129b773a93cf8603cdf2df0f6530364200ddea7ce7a070101491800a92d`,
LLA `67d98d3e34aa0edeac2c77b955c0a0e489d3b6aac89f86959a8b626c4b4d2b69`.
The RC4.2 configuration manifest digest is
`52567f9f0f269f19be548e8544ba80ad99f76b9687b426a053da74d8692c307b`;
the prior config digest remains in the fixture as historical provenance.

## Exact changed-file inventory

| Path | Change |
|---|---|
| `.gitattributes` | Preserve raw current RC4.2 bytes |
| `README.md` | Current authority paths, physical-policy APIs, commands and deferrals |
| `docs/specs/DGCA_CORE_RC4_1.md` → `docs/specs/DGCA_CORE_RC4_2.md` | Versioned Core migration with executable L01 selection/age/bilateral guards |
| `docs/specs/DGCA_LLA_RC4_1.md` → `docs/specs/DGCA_LLA_RC4_2.md` | Versioned provenance/residual novelty/lifecycle integration |
| `docs/specs/SOURCE-MANIFEST.md` | Current raw SHA/blob pins and archival commit/hash provenance |
| `docs/implementation/I0-IMPLEMENTATION-CONTRACT.md` | Historical-baseline notice; original body retained |
| `docs/implementation/I0-VERIFICATION-REPORT.md` | Historical-baseline notice; original evidence retained |
| `docs/implementation/I1-IMPLEMENTATION-CONTRACT.md` | Historical-baseline notice; original body retained |
| `docs/implementation/I1-VERIFICATION-REPORT.md` | Historical notice and current remediation-report link |
| `docs/implementation/I1-L01-SOURCE-MIGRATION.md` | Dedicated transition scope/provenance record |
| `docs/implementation/I1-L01-VERIFICATION-REPORT.md` | This execution evidence |
| `src/dgca_next/config.py` | RC4.2 source origins; approved policy tag/salt and production-OFF setting |
| `src/dgca_next/integrity.py` | Active/archival pins; immutable historical commits; exactly-two-authority checks |
| `src/dgca_next/graph/__init__.py` | Export physical policy and fixture interfaces |
| `src/dgca_next/graph/latent.py` | Immutable assignment clock/event/version metadata |
| `src/dgca_next/graph/policy.py` | Pure Q6/LOCAL/topographic/coactive selectors and immutable fixture cohorts |
| `src/dgca_next/graph/recycling.py` | Future verified-witness interface, synthetic residual arithmetic, bilateral plans and clock-credit law |
| `src/dgca_next/graph/network.py` | Atomic cohort/context initialization, later fills, guarded fixture replacement, production rejection and idempotence |
| `src/dgca_next/graph/audit.py` | Fixed-policy/version, assignment-age, inverse-index and recycling-log audits |
| `tests/fixtures/i0-contract-v1.json` | Updated config fingerprint; retained archival fingerprint |
| `tests/test_spec_integrity.py` | Current/archival/migration-parent raw hashes and independent-law preservation |
| `tests/test_graph_latent.py` | Replace two policy skips with actual physical/production-guard tests; adapt resolved-policy diagnostics |
| `tests/test_latent_policy.py` | Co-birth, golden selectors, ranks, pins, provenance, replay/order and feasibility measurements |
| `tests/test_latent_recycling.py` | Age/novelty/bilateral guards, actual replacements, protected states and fault rollback |

The existing Ubuntu/Windows workflow already targets this feature branch and
runs the complete suite twice plus integrity, Ruff, formatting, mypy and clean
status. No workflow or dependency change was required. I0 physical contracts,
version identifier, runtime ownership envelopes and neural exclusions remain.

## PASS — executed local verification

Runtime: Windows, CPython 3.14.4, pytest 9.0.2, Ruff 0.14.14, mypy 1.19.1.
All commands ran from the repository root using the existing I0 environment.

| Exact command | Executed result |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp -rs` before changes | Historical baseline: `314 passed, 2 skipped in 13.25s` |
| `.\.venv\Scripts\python.exe -m pytest -q tests/test_spec_integrity.py tests/test_config_determinism.py --basetemp=.pytest-tmp` after final migration hash pinning | `53 passed in 1.12s` |
| `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp -rs` on committed implementation | **`421 passed in 11.15s`** |
| `.\.venv\Scripts\python.exe -m ruff check .` | `All checks passed!` |
| `.\.venv\Scripts\python.exe -m ruff format --check .` | `30 files already formatted` |
| `.\.venv\Scripts\python.exe -m mypy` | `Success: no issues found in 16 source files` |
| `.\.venv\Scripts\python.exe -m dgca_next verify-specs` | Both exact raw hashes below; PASS |
| `.\.venv\Scripts\python.exe -m pip check` | `No broken requirements found.` |
| `git diff --check` | Exit 0 |
| `git status --porcelain` after committed validation | Empty stdout |
| `git diff 511fe3e6f67cbf63004398bf2ac4f3b5ff2d2a7e --exit-code -- docs/specs .gitattributes src/dgca_next/config.py tests/fixtures/i0-contract-v1.json` | Exit 0; scientific bytes and migrated configuration unchanged during implementation |
| `Get-Content .pytest_cache/i1-stress-metrics.json` | Measured sparse fixture artifact below |
| `Get-Content .pytest_cache/i1-l01-feasibility.json` | Measured published-footprint fixture eligibility below |

Exact committed-implementation pytest output:

```text
........................................................................ [ 17%]
........................................................................ [ 34%]
........................................................................ [ 51%]
........................................................................ [ 68%]
........................................................................ [ 85%]
.............................................................            [100%]
421 passed in 11.15s
```

Exact integrity output:

```text
PASS docs/specs/DGCA_CORE_RC4_2.md SHA-256=570570a2a57c3b859ed3745c8812711cf36de89a47be50bdbf5f415a1b8dbc59
PASS docs/specs/DGCA_LLA_RC4_2.md SHA-256=47ad994cbda467ae1ce0ffd6c2868522f5502897f6c4d2d1f3ab68b69ac1df30
```

All 314 previously passing I0/I1 regressions remain in the executed suite, with
the authorized version/provenance adaptations. The two former policy skips now
execute checks; additional tests execute successful fixture replacement as well
as production rejection. The final count is a newly executed 421, not reuse of
the historical 314 result. No missing policy was hidden by skip/xfail/warning
suppression.

## Cross-platform CI

Implementation run: [I0 and I1 validation, 40588125928](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/40588125928)
at `60be997c3eb5f39c6eb833f65bfaab0824be86c6`.
Both `contracts (ubuntu-latest)` and `contracts (windows-latest)` completed
successfully. Their installation, version, integrity, two full pytest runs, Ruff,
formatting, mypy and final clean-status steps all concluded `success`.
The report-only delivery head's CI is necessarily observed after this report is
committed/pushed; the completion message identifies that final SHA and run. Both
jobs must pass on that head before handoff.

## L01 and I1 gate dispositions

| L01 gate | Verdict | Evidence and limits |
|---|---|---|
| L01-T01 | PASS physical | Simultaneous three-receiver cohort, no iteration advantage, latent D graph only; zero learned links |
| L01-T02 | PASS | Exact LOCAL corner/edge/center round-robin vectors, clipping, self/duplicate exclusion |
| L01-T03 | PASS | Standalone-spec SHA-256 golden vectors, including owner 1309 collision/probe; no Python hash or SIC salt reuse |
| L01-T04 | PASS | Exact rational Q6, ties/physical IDs, reordered births, empty categories and later empty-slot fills |
| L01-T05 | PASS physical subset | Initialization adds no evidence/synapses; retroactive birth-event fixture link rejected; permitted birth retained after trigger rejection; clock-credit rule excludes incomplete/internal/read-only cases |
| L01-T06 | PASS guards | 99/100 boundary; both assignment ages; canonical event-bound residual threshold; no caller scalar authority; production always OFF |
| L01-T07 | PASS | Both directions/all live states, LOCAL/ASSOCIATIVE/CROSS scope, reservations, pins, fixed/protected copies and interrupted two-sided mutation |
| L01-T08 | PASS | Actual one-/two-sided fixture replacement, refreshed metadata and reverse references, ordered logs, idempotent retry, whole-operation failure without replacement |
| L01-T09 | PASS measurement | Four published SIC physical-footprint cohorts examined for structural three-way eligibility; no encoder/learning execution |
| L01-T10 | PASS | Snapshot/dump reproducibility, required versions, frozen physical schemas, no semantic fields, independent corruption audits |
| L01-T11 | PASS local and implementation CI | Entire I0/I1 regression suite; Ubuntu/Windows results and final-head validation as recorded above/in completion message |

I1-G01–G08: physical address/Cell model, complete approved latent policy,
synapse legality, budgets/reservations, atomicity, sparse verification,
regressions/integrity/implementation CI and candid reporting are satisfied.
Final report-only head verification is a handoff condition as described above.
I1-G02's former missing-policy blocker is resolved. The owner
explicitly authorized physical completion with real novelty integration deferred.

## Measurements — synthetic fixtures only

The existing full-network fixture still verifies all 12,288 stored physical cell
records with 768 occupied slots, 576 live fixture synapses and 192 reserved keys.
There are 768 stored 24-position neighborhoods, not dense N×N connectivity.
Its unchanged canonical structural hash is
`160a96789166570bd8337c04f55044687c2dae8df62f690832d0164afb0f58b9`.

Measured on the final committed local run: construction including its publication
audit **1.2305536000058055 s**, independent audit **0.800667799951043 s**,
Python-traced retained memory **6,410,737 bytes**, peak **13,851,557 bytes**.
These are `tracemalloc` fixture measurements, not process RSS or a performance
promise. No new time/memory acceptance threshold was invented.

The L01 feasibility fixture uses Core §3.1's four published receiver-ID vectors.
Each cohort has four distinct receivers, with **four structurally eligible
three-cell subsets**. **4/4 cohorts (100%)** have at least one eligible triangle.
This is a tiny explicitly constructed footprint measurement, not learned links,
reciprocal consolidation, real SIC execution, vocabulary coverage, Assembly birth
or empirical language fitness. The percentage is recorded, not tuned or used as
a required success threshold. Every such graph has zero synapses.

## FAIL, SKIPPED and NOT_RUN

**FAIL: 0 final local test/check failures.** During development, Ruff found import
and wrapping issues and mypy found temporary annotation/narrowing issues; they
were corrected, and the final checks above passed unchanged strict settings.
The first migration commit attempt caught Markdown trailing whitespace; only
changed header lines were trimmed and both hashes repinned before the single
migration commit. An approval-service usage-limit interruption delayed that
commit; after the user asked to continue, the retry executed successfully. No
rejected action was bypassed and no permission blocker remains.

**SKIPPED: 0.** The two historical policy skips are replaced by executed tests.
There are no xfails or conditional policy passes in the final local suite.

**NOT_RUN / DEFERRED:** genuine external LEARN novelty verification and production
automatic recycling integration/ablation; real X_ext and pre-input P_T creation;
sensory admission and root execution; ABORT/END durability, journals, save/load
and recovery; I2 activation/normalization; I3 learning/evidence laws; contextual
owner recruitment; actual Assembly formation, hierarchy, retrieval and generation.
All **57 scientific tests LLA-T01–T41 and LG-T01–T16 remain NOT_RUN**. Other Python
minor versions, GPUs, scale/performance experiments and empirical utility are
not claimed.

## Remaining limitations and exact safety boundary

`VerifiedLocalNovelty` is a future producer authority interface. The only concrete
I1 novelty input is `FixtureLocalNovelty`, which is explicitly synthetic, immutable
and bound to the exact fixture snapshot. Its pure residual arithmetic does not
obtain predictions or certify observations. `SparseNetwork.recycle_slot()`
rejects it and protocol-shaped caller claims; `automatic_recycling_enabled` is
read-only false. No code path turns a caller-provided scalar into production proof.

The completed-close serial is an externally provided fixture quantity; the pure
credit rule does not execute or deduplicate roots. The real I2/I3 executor must
validate observation/provenance/commitment, freeze predictions before current SIC,
advance only genuine completed-root closes, and certify novelty. OPEN/ABORT
semantics are specified in RC4.2 but not falsely represented as an implemented
I1 root executor. The pending-birth marker and physical initialization persist
without evidence credit in fixtures; lifecycle publication/recovery remains later.

Contextual END birth accepts explicit protected physical pins first and initializes
fixed topology without a fake sensory score for z. It is a physical fixture API,
not I5 role selection, OwnerID admission or neural contextual activation.
Legacy isolated graph fixtures may remain explicitly uninitialized; missing
assignment age never defaults to zero and cannot authorize recycling. Initialized
policy metadata requires an explicit supported version; actual checkpoint loading
is still outside I1. Diagnostics/digests are not a persistence implementation.

No new scientific parameter was guessed: counts/budgets/W_conf/theta_R/eps_p are
existing constants; the new topographic bytes and production-OFF boundary are
exactly owner-approved. The residual law is approved experimental science and may
frequently produce 1 with absent predictions; utility remains untested.

Stop after final-head verification at **I1-L01 REVIEW READY**. Main remains
unchanged and I2 has not been started.
