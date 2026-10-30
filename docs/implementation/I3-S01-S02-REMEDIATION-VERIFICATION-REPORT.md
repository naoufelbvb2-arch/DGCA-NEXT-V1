# I3 S01/S02 remediation verification — I3 PARTIAL

## Result and exact remaining blocker

The owner-approved scientific migration to RC4.4 is complete, but **I3
production learning is not complete**. The present `RootStore` deliberately
rejects a valid `EVENT` with `I3-R02: EVENT production graph authority is not
implemented`; `END` also fails closed. It has no durable production graph W,
validated external witness, genuine EVENT/END journal, proposal publication,
real evidence updates, or event-bound novelty producer. Therefore the required
from-zero production learning and read-only causal experiment is **NOT_RUN**.
There is no empirical result that the model cannot learn. These are unfinished
engineering obligations, not a claim of a new scientific ambiguity.

I3-S01 and I3-S02 are **owner-resolved** and incorporated into the two
RC4.4 scientific sources. The currently implemented selector and homeostasis
profile are pure components, not production admission, durable adaptation, or
root authorization. They are not yet connected to the SQLite root skeleton.
In particular, exact H_BEGIN restoration *after an actual newborn EVENT*,
the distinction between missing defaults and missing previously adapted
overrides on a durable graph, and prevention of alternate production H profiles
have not been verified in an end-to-end production path. Existing BEGIN/ABORT
tests exercise only the old explicit-H / empty-W skeleton.

## Source migration, commits and changed files

Branch `feature/i3-local-learning`; owner-approved remediation parent
`c0c860a1a00b24c5e796a512c5b77beb022a079a`. Atomic source migration commit
`17893cdf8f84bb4f60dc00ce98fc4e97ad1750d1`. Subsequent partial policy commit
`68c6240b28c1d39f48c82b6cc2c1f878da87ca53`. The report is committed separately;
its own commit SHA and final-head CI are obtained from Git and the workflow
run, avoiding a self-referential hash.

Changed paths from that parent:

- `README.md`;
- `docs/specs/DGCA_CORE_RC4_3.md` → `docs/specs/DGCA_CORE_RC4_4.md`;
- `docs/specs/DGCA_LLA_RC4_3.md` → `docs/specs/DGCA_LLA_RC4_4.md`;
- `docs/specs/SOURCE-MANIFEST.md`;
- `src/dgca_next/config.py`, `src/dgca_next/dynamics/state.py`,
  `src/dgca_next/integrity.py`;
- `src/dgca_next/learning/homeostasis_profile.py`,
  `src/dgca_next/learning/observation.py`, `src/dgca_next/persistence/store.py`;
- `tests/experiments/test_i3_cold_learning.py`,
  `tests/fixtures/i0-contract-v1.json`, `tests/test_i3_r01_root_store.py`,
  `tests/test_i3_r02_ingress_preflight.py`, `tests/test_i3_rc44_policy.py`,
  `tests/test_spec_integrity.py`;
- `docs/implementation/I3-S01-S02-REMEDIATION-VERIFICATION-REPORT.md`.

The only current scientific authorities are:

| Source | SHA-256 | Git blob SHA-1 |
| --- | --- | --- |
| CORE RC4.4 | `3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c` | `1207be632b6f8aa5839a30c0570ce844724faf0f` |
| LLA RC4.4 | `ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0` | `7c81d4dd6ea98650856cb87cf02ddce3bce5048d` |

RC4.3 Core SHA-256 `41764eea3ddccdbd692325ecf7f03c243bf259bb46cc2b1820f7648125f3a53a`,
blob `37a226f5d81b3c72685015ae7125f9d5d24af9f4`; RC4.3 LLA SHA-256
`4c70fd84a8356e7871e6ac5bd14eeb800bf2347342512c4901e1e2191a89e958`,
blob `4fbaef7f3922d41604bd649b1217fe2741d58b3e`. Their exact bytes remain
available at `c0c860a1a00b24c5e796a512c5b77beb022a079a`. Tests compare the
independent scientific body before and after the approved inserted paragraphs.
New config fingerprint:
`088363eb89484c9605fa52e7c06743e5a1867be22bf3d87692492221fd317e27`.
All prior configured values remain unchanged; the new profile values are
separately recorded with RC4.4 source origins.

## Implemented and tested subsets

- Pure ingress preflight ranks unique eligible receivers by descending exact
  SIC millionths then physical ID, accepts at most 12 and exposes per-cell
  `SENSORY_BIRTH_CAPACITY_DEFERRED` diagnostics. It validates an audited
  snapshot but neither creates witnesses nor commits cells. Unit tests cover
  permutations, Unicode normalization, merged supports, salience, committed
  exclusion, strict epsilon and 0/1/8/12/13/16 candidates.
- The sparse LANGUAGE H numeric profile has virtual gain `1.0`, cell EMA
  `.05`, initial regional EMA `.030` and initial threshold `.20`. Its
  `DGCA-H-LANGUAGE-V1` profile hash is
  `67a2196c02d2235f2d40ca6fe1e9d50bd0397b15b1d09d92692720c2260851e6`.
  Canonical initial profile record hex is
  `444743412d48340167a2196c02d2235f2d40ca6fe1e9d50bd0397b15b1d09d92692720c2260851e6480100000022000000000000000000000001023fc999999999999a00000001023f9eb851eb851eb8`.
  Tests check round-trip bytes, sparse overrides, no region reset on virtual
  birth, missing pair, tampered hash, unsupported region, and pure numeric
  adaptation over an audited synthetic pre-event population. These tests do
  not confer production event provenance or persist an override.
- The old store now validates SIC features without creating a fresh empty
  graph as a purported durable W. It remains fail-closed on EVENT/END. It
  retains the previously tested BEGIN/ABORT SQLite skeleton and explicitly
  caller-supplied H for that legacy path; that H is not authorized production
  initialization. Automatic production recycling remains disabled.

## Traces and experimental limitations

In a pure cold diagnostic, features `(a,1),(ab,1),(c,1),(d,1)` produce 16
unique receivers, each `X_fixed=1000000`. The selected IDs are `8286, 8465,
8606, 8649, 8694, 9227, 9345, 9902, 9912, 10128, 10273, 10513`; deferred IDs
are `11524, 11641, 11795, 12181`. No physical cohort is committed by this
diagnostic. In a synthetic guard test, two test roots are opened and aborted;
their attempted events both return `I3-R02` before publication. The test
high-water mark is 2, accepted events and completed external roots are 0,
initial and final W are the empty marker, and learned links are 0. These test
roots are not genuine completed external exposures.

Genuine learned link IDs, actual event-time and close-time D, q/y/E/S/count,
independent completed root IDs, neural Q/ablation effect, saved and restored
learned W, EVENT/END crash witnesses, 100-close novelty age audit, AB/DB
diagnostic, experiment resource measurements and H_BEGIN after a real birth
are all **NOT_RUN**. Existing q/y examples and root simulations in the earlier
report are synthetic arithmetic, not evidence of actual learning. The required
H0=0 rate comparator is also **NOT_RUN**; the profile has not been varied to
force a result.

## Local verification

Windows, Python 3.14, source state at implementation commit `68c6240`:

| Exact command | Result |
| --- | --- |
| `.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp -rs` | **PASS:** `640 passed in 8.83s`; no skips. The 621 prior tests remain, with outdated I3-S01/S02 error assertions updated to test the approved behavior. |
| `.venv\Scripts\python.exe -m ruff check .` | **PASS:** `All checks passed!` |
| `.venv\Scripts\python.exe -m ruff format --check .` | **PASS:** `71 files already formatted` |
| `.venv\Scripts\python.exe -m mypy` | **PASS:** `Success: no issues found in 39 source files` |
| `.venv\Scripts\python.exe -m dgca_next verify-specs` | **PASS:** the two RC4.4 SHA-256 values above. |
| `.venv\Scripts\python.exe -m pip check` | **PASS:** `No broken requirements found.` |
| `git diff --check` | **PASS:** no output. |

**FAIL:** none in the final local checks. **SKIPPED:** none reported by
pytest. **SPEC_BLOCKED:** no additional unresolved scientific rule established
in the implemented subsets; unimplemented production paths have not been
fully evaluated for further ambiguities. **EMPIRICAL_BLOCKED:** not claimed;
the real experiment has not run. **NOT_RUN:** actual production acceptance and
empirical cases described above.

Implementation-head cross-platform CI:
[run 40701171064](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/40701171064)
completed **PASS** on Ubuntu and Windows for commit `68c6240b28c1d39f48c82b6cc2c1f878da87ca53`.
The report commit triggers a separate final-head run, whose actual SHA and
result are available in the [branch workflow history](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/workflows/validate.yml?query=branch%3Afeature%2Fi3-local-learning).
Do not infer final-head status from an earlier run.

## Checkpoints and acceptance gates

| Checkpoint | Verdict | Evidence / gap |
| --- | --- | --- |
| A | **PASS** | Atomic RC4.4 migration, pinned hashes, independent-law and regression checks. |
| B | **NOT_RUN** | Pure selector/profile subsets pass; real production admission, EVENT adaptation and H_BEGIN identity across newborn/ABORT are absent. |
| C | **NOT_RUN** | No genuine witnessed EVENT, proposals, END, evidence or production graph authority. |
| D | **NOT_RUN** | No production W/R/journal codec or EVENT/END crash recovery. Legacy BEGIN/ABORT skeleton tests pass only for empty W. |
| E | **NOT_RUN** | No genuine external-root learning, learned-link persistence or causal inference. |
| F | **NOT_RUN** | Local checks pass; final-head Ubuntu/Windows CI must be observed after report publication. |

| Gate | Verdict | Evidence / gap |
| --- | --- | --- |
| I3-G01 | **NOT_RUN** | No accepted production EVENT or validated external root witness. |
| I3-G02 | **NOT_RUN** | Pure deterministic sensory ranking passes; no actual production birth or latent initialization. |
| I3-G03 | **NOT_RUN** | No witnessed proposals, D_event/D_close or atomic END arbitration. |
| I3-G04 | **NOT_RUN** | Synthetic root-max/evidence arithmetic only; no actual independent completed-root evidence. |
| I3-G05 | **NOT_RUN** | Legacy empty-W BEGIN/ABORT tests pass; production EVENT/END and W persistence/recovery are absent. |
| I3-G06 | **NOT_RUN** | No genuine event-local novelty authority or 100-close audit; automatic recycling remains off. |
| I3-G07 | **NOT_RUN** | Cold-start production experiment, learned links, repetition, persistence and causal effect unavailable. |
| I3-G08 | **NOT_RUN** | 640 local tests, static checks and integrity pass; exact final-head CI must be observed after publication. |

Complete scientific LLA-T and LG-T scenarios needing genuine I3/Assembly/owner
or later generation remain **NOT_RUN**, notwithstanding physical fixture
sub-operator tests. No I4 work or main merge was performed.

Final status: **I3 PARTIAL**.
