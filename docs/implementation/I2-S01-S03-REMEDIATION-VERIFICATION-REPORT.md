# I2 S01–S03 remediation verification

Date: 2026-10-28 (America/New_York). Target: **I2-R06 REVIEW READY** after
final delivery-head CI. Repository `naoufelbvb2-arch/DGCA-NEXT-V1`; exclusive
branch `feature/i2-neural-dynamics`. The RC4.3 sources are design candidates,
**NOT FROZEN / NOT EMPIRICALLY VERIFIED**. The tests below exercise physical
fixtures and pure numerical calculations, not actual neural learning.

## Authorization and commits

The owner-approved `I2-S01-S03-APPROVED-EXECUTION-CONTRACT.md` authorizes the
three decisions, versioned two-source migration and I2 remediation. The
resolution proposal is non-normative; the two RC4.3 files are current authority.

| Step | SHA |
|---|---|
| Accepted I1 main base | `0b05311fe82dc2e8961bcca226f8d795b3484524` |
| Prior I2 checkpoint (547 passing, three blockers) | `eabc2b79beec8f97e9d3380a3bd4fa58d6c571fe` |
| Approved migration parent and starting remediation branch | `ba36cab417574c7ee416e358f448bec54d0006f2` |
| Atomic two-spec RC4.3 migration | `188b670eff3de010f350ddb1a72180055be6bbcd` |
| R06-B live synchronous links | `e409a95e2bfcf461b0242f6804f1c006c1c61ff7` |
| R06-C weighted fresh cohesion | `7fdbcf1d9f89c805fcb06ff3919c604cc538dbaa` |
| R06-D committed-population firing | `0bb274b322486aea0e4819f19b0351ef269cdc33` |
| R06-E targeted boundary tests and README | `9f541c3502250762ec6e75658f68c034a00fc860` |
| Additional archival/default-parameter integrity tests | `4eabb77cdde2a6fd599c9886706004914ed84286` |
| Frozen-graph cohesion re-audit | `56d092b3422de1f4806cf3fc2694c7f7f223ecbd` |

The report-only delivery commit is identified in the completion message and by
`git log -1 --format=%H -- docs/implementation/I2-S01-S03-REMEDIATION-VERIFICATION-REPORT.md`.
It cannot embed its own hash. No merge to main was performed.

## Scientific migration and exact hashes

Both authorities were renamed together in commit `188b670`, with their revision,
companion, approved S01–S03 text, manifest, configuration origins and integrity
tests in that same commit. Exactly two current scientific files exist. Tests
recover RC4.2 byte-for-byte from immutable parent `ba36cab`; RC4.1 remains pinned
at its earlier archival commits. Tests strip the explicitly authorized additions
and the one accompanying pass-1 clarification and compare **all remaining body
bytes** to RC4.2, then independently compare the RC4.2 laws to RC4.1 as before.
Another test compares the complete Python AST of all configuration defaults
before and after migration: no scientific value changed.

| Source | Raw SHA-256 | Git blob SHA-1 |
|---|---|---|
| Current `DGCA_CORE_RC4_3.md` | `41764eea3ddccdbd692325ecf7f03c243bf259bb46cc2b1820f7648125f3a53a` | `37a226f5d81b3c72685015ae7125f9d5d24af9f4` |
| Current `DGCA_LLA_RC4_3.md` | `4c70fd84a8356e7871e6ac5bd14eeb800bf2347342512c4901e1e2191a89e958` | `4fbaef7f3922d41604bd649b1217fe2741d58b3e` |
| Archived `DGCA_CORE_RC4_2.md` | `570570a2a57c3b859ed3745c8812711cf36de89a47be50bdbf5f415a1b8dbc59` | `5422a212abe21773a48c82b7f2ceaa34a9cd0a63` |
| Archived `DGCA_LLA_RC4_2.md` | `47ad994cbda467ae1ce0ffd6c2868522f5502897f6c4d2d1f3ab68b69ac1df30` | `889025d76d70167de3070ffd8945878d37bf3dde` |

The current configuration fingerprint, including its new RC4.3 source origins,
is `78c0764c0bfde69e6d0d347b24fef73c33670243f15ef69decad5054a810a61f`;
the prior `52567f9f0f269f19be548e8544ba80ad99f76b9687b426a053da74d8692c307b`
is retained as archival provenance. The I2 contract's former consolidated-Q
phrase is explicitly superseded in a dated note; its original wording remains.

## Changed files relative to `ba36cab`

| Path | Change |
|---|---|
| `.gitattributes` | Preserve exact RC4.3 source bytes |
| `README.md` | Current authority, remediation and fixture limitations |
| `docs/specs/DGCA_CORE_RC4_2.md` → `DGCA_CORE_RC4_3.md` | Versioned Core S01–S03 decisions |
| `docs/specs/DGCA_LLA_RC4_2.md` → `DGCA_LLA_RC4_3.md` | Versioned consistency note; evidence laws retained |
| `docs/specs/SOURCE-MANIFEST.md` | Current and archival raw hash/blob pins |
| `docs/implementation/I0-IMPLEMENTATION-CONTRACT.md` | Current-authority notice; historical body retained |
| `docs/implementation/I0-VERIFICATION-REPORT.md` | Current-authority notice; historical evidence retained |
| `docs/implementation/I1-IMPLEMENTATION-CONTRACT.md` | Current-authority notice; historical body retained |
| `docs/implementation/I1-VERIFICATION-REPORT.md` | Current-authority notice; historical evidence retained |
| `docs/implementation/I1-L01-VERIFICATION-REPORT.md` | Historical RC4.2 notice |
| `docs/implementation/I2-IMPLEMENTATION-CONTRACT.md` | Dated, explicit S01 supersession |
| `docs/implementation/I2-VERIFICATION-REPORT.md` | Historical RC4.2 checkpoint notice |
| `docs/implementation/I2-S01-S03-REMEDIATION-VERIFICATION-REPORT.md` | This report |
| `src/dgca_next/config.py` | RC4.3 origin paths, unchanged defaults |
| `src/dgca_next/integrity.py` | Current/archived pins, migration parent and exactly-two check |
| `src/dgca_next/dynamics/drive.py` | Legal live LOCAL/CROSS states use actual Q |
| `src/dgca_next/dynamics/attractor.py` | Bound Assembly fixture, reciprocal weighted cohesion and admission |
| `src/dgca_next/dynamics/session.py` | Compute cohesion from fresh W/activity; remove scalar override |
| `src/dgca_next/dynamics/homeostasis.py` | Audited pre-event committed population, rho and pure H update |
| `src/dgca_next/dynamics/state.py` | Re-audit captured I1 graph and diagnostic identity |
| `tests/fixtures/i0-contract-v1.json` | RC4.3 config digest, retain RC4.2 digest |
| `tests/neural_fixtures.py` | Bind synthetic Assembly identity/generation to captured W |
| `tests/test_dynamics_two_pass.py` | Replace S01 blocker assertion with actual live propagation |
| `tests/test_dynamics_attractor.py` | Replace S02/S03 blocker assertions with actual operations |
| `tests/test_dynamics_sessions.py` | Remove obsolete synthetic cohesion override |
| `tests/test_i2_r06_s01.py` | Live states/scopes, .048, absent/reserved keys and Assembly separation |
| `tests/test_i2_r06_s02.py` | Equal/unequal reciprocal weights, fresh gating, invalid/stale structures |
| `tests/test_i2_r06_s03.py` | Exact frozen population, pre-threshold, newborn, empty region, H immutability |
| `tests/test_spec_integrity.py` | RC4.2 archival bytes, unrelated-law preservation, all defaults and stale authorities |

No I0/I1 regression was removed. Previously passing fail-closed S01–S03 tests
were replaced by real operation tests and invalid-input checks, as authorized.
The existing GitHub Actions workflow already targets this I2 feature branch.

## PASS: executed verification

Local environment: Windows, CPython 3.14.4, pytest 9.0.2, Ruff 0.14.14,
mypy 1.19.1. Commands ran at the repository root.

| Exact command | Result |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp -rs` before remediation | `547 passed in 21.21s` |
| `.\.venv\Scripts\python.exe -m pytest -q tests/test_spec_integrity.py tests/test_config_determinism.py --basetemp=.pytest-tmp` | `66 passed in 2.88s` |
| `.\.venv\Scripts\python.exe -m pytest -q tests/test_i2_r06_s01.py tests/test_i2_r06_s02.py tests/test_i2_r06_s03.py --basetemp=.pytest-targeted -rs` | `24 passed in 0.21s` |
| `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp -rs` before final graph re-audit | `578 passed in 22.70s` |
| `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp -rs` after all implementation changes | **`578 passed in 6.90s`** |
| `.\.venv\Scripts\python.exe -m ruff check .` | `All checks passed!` |
| `.\.venv\Scripts\python.exe -m ruff format --check .` | `59 files already formatted` |
| `.\.venv\Scripts\python.exe -m mypy` | `Success: no issues found in 32 source files` |
| `.\.venv\Scripts\python.exe -m dgca_next verify-specs` | Both exact RC4.3 hashes below; PASS |
| `.\.venv\Scripts\python.exe -m pip check` | `No broken requirements found.` |
| `git diff --check` | Exit 0 |
| `git status --porcelain` after implementation commits | Empty stdout |
| `git diff 188b670eff3de010f350ddb1a72180055be6bbcd HEAD --exit-code -- docs/specs .gitattributes src/dgca_next/config.py tests/fixtures/i0-contract-v1.json` | Exit 0; no later science/config changes |

Exact final local pytest output:

```text
........................................................................ [ 12%]
........................................................................ [ 24%]
........................................................................ [ 37%]
........................................................................ [ 49%]
........................................................................ [ 62%]
........................................................................ [ 74%]
........................................................................ [ 87%]
........................................................................ [ 99%]
..                                                                       [100%]
578 passed in 6.90s
```

Exact integrity output:

```text
PASS docs/specs/DGCA_CORE_RC4_3.md SHA-256=41764eea3ddccdbd692325ecf7f03c243bf259bb46cc2b1820f7648125f3a53a
PASS docs/specs/DGCA_LLA_RC4_3.md SHA-256=4c70fd84a8356e7871e6ac5bd14eeb800bf2347342512c4901e1e2191a89e958
```

Cross-platform implementation run
[40623955692](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/40623955692)
on `9f541c3502250762ec6e75658f68c034a00fc860`: **PASS** Ubuntu and Windows,
all steps successful, including two complete pytest runs. Additional integrity
tests on `4eabb77cdde2a6fd599c9886706004914ed84286` also passed both jobs in
[run 40688866441](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/40688866441).
The final graph-audit fix and this report trigger final-head CI. Its SHA, run
link and both job results are recorded after publication in the completion
message, not guessed here.

## Before/after physical numerical examples

All graph records below are explicitly synthetic I1 fixtures. They do not attest
external roots, learned synapses or naturally formed Assemblies.

**S01:** the previous kernel raised `I2-S01` for an emitting CANDIDATE link.
Now a legal LOCAL candidate with `S=.60`, `E_ext=1`, `E_int=0` has `Q=.06`;
source pass-1 activity `.8` gives the actual contribution **`.048`**. The same
test family covers CANDIDATE, EPISODIC_INDEXED and CONSOLIDATED in both LOCAL
and CROSS scopes. An absent or reservation-only key and a non-emitting source
give zero. Candidate reciprocal links do not satisfy Assembly structural
qualification. ASSOCIATIVE prior-frontier propagation and the no-evidence-factor
test remain intact.

**S02:** the previous admission required a supplied synthetic cohesion scalar
or raised `I2-S02`. For the bound equal-weight reciprocal fixture triangle
`[8606,9345,11795]`, fresh `(1,1,0)` has mean `0.6666666666666666` and
cohesion `0.3333333333333333`; admission returns
`ATTRACTOR_INSUFFICIENT_COHESION`. Fresh `(.5,.5,.5)` has mean and cohesion
`.5` and admits. A second independently specified triangle uses reciprocal
weights `.3,.5,1.0` and fresh `(.8,.4,.2)`; the test compares the exact ordered
binary64 quotient `(.3*.4+.5*.2+1*.2)/(.3+.5+1)` and counts each unordered
pair once. Nonconsolidated or one-sided links are excluded from the qualifying
pair set. No X produces zero fresh/cohesion. Stale or unbound fixture generation
is rejected, and no session API accepts a caller cohesion override. Active
Attractor age/error/decay and next-step-only sigma remain tested.

**S03:** the previous pure helper required a caller-supplied rho or raised
`I2-S03`. For frozen pre-event committed cells `[8192,8193]`, pre-threshold
`.20`, final activity `(1,0)` and prior EMA `.03`, the audited graph-derived
population has active IDs `[8192]`, **rho `.5`**, new EMA `.0535`, and new
threshold `0.20500000000000002`. Dormant committed cells remain in the
denominator; a cell committed after the snapshot is excluded. Residual activity
can count as firing without entering F_step. Empty population leaves that region
unchanged; no asserted scalar or fabricated graph hash is accepted as population
proof. The function returns a new H fixture and never executes or commits LEARN.

The full-suite sparse dynamics measurement is 512 synthetic committed cells,
zero links and four read-only events across the 12,288 logical addresses. This
Windows run recorded `0.2014634000370279` seconds, `784540` retained and `819650`
peak bytes by `tracemalloc`; these are fixture observations, not RSS or a
performance threshold.

## I2 acceptance gates

| Gate | Verdict | Evidence / scope |
|---|---|---|
| I2-G01 | PASS | Exact SIC and FP-ROLE vectors, strict decimal/Unicode and alias/replay regressions |
| I2-G02 | PASS | All legal live-state synchronous scopes use actual Q; prior temporal drive, frozen passes, column normalization and no third pass |
| I2-G03 | PASS | Typed provenance, new-event frontier versus residual, cold/boundary and copied-state forgery regression |
| I2-G04 | PASS fixture scope | Physical gate, depth-2 directed target exception, stale/ambiguous owner diagnostics; no real owner recruitment |
| I2-G05 | PASS pure fixture scope | Reciprocal fresh cohesion and graph-derived committed-population H arithmetic, no real Assembly formation or durable H writes |
| I2-G06 | PASS fixture scope | Cold read-only, PredScore and FULL/CONTROL preserve W, H and caller R; no evidence/commitment |
| I2-G07 | PASS local and implementation CI; final-head CI observed after publication | 578 full tests, strict tooling and integrity; final delivery-head Ubuntu/Windows jobs must succeed |
| I2-G08 | PASS | Exact source pins, results, physical traces, empirical boundaries and deferrals recorded |

## FAIL, SKIPPED, NOT_RUN and remaining limitations

- **FAIL:** zero final local checks. A test assertion was briefly placed in the
  wrong test while editing S02 and was corrected before the final run. No
  scientific file was repinned after the atomic migration commit.
- **SKIPPED:** zero final pytest skips/xfails. All three former blocker guards
  now have executed successful operations as well as invalid-structure tests.
- **SPEC_BLOCKED:** none of the three owner-approved I2 S01–S03 rules remains
  blocked. No additional mandatory scientific ambiguity was discovered for
  this remediation.
- **NOT_RUN:** all 57 named scientific LLA-T01–T41 and LG-T01–T16; genuine
  LEARN event/root execution, external q/E/S updates, checkpoint/ABORT recovery,
  verified novelty, production automatic recycling, I4 Assembly formation, I5
  owner recruitment, generation, GPUs and empirical language capability.
  Production automatic recycling remains disabled. VISION/AUDIO initial
  thresholds remain unspecified and outside the LANGUAGE first lab.

I1 currently stores only fixture membership IDs, not a production Assembly
registry/generation. `AssemblyFixture.bind` therefore captures explicit
synthetic ID/generation and its full frozen graph hash; changed graph identity,
generation, membership or illegal structure fails closed. This conservative
fixture binding is not a persisted I4 Assembly or proof of learned structure.
Similarly, the regional producer verifies the supplied pre-event I1 graph
snapshot and derives its exact committed IDs; I2 has no real root/event
authority to certify when production EVENT began. I3 owns that lifecycle, H
publication and BEGIN/ABORT rollback. Pure helper inputs and fixture outcomes
never become external evidence. No production activation, learning or novelty
claim follows from these tests.

After final-head CI, stop at **I2-R06 REVIEW READY**. Do not merge to main or
begin I3 without independent review.
