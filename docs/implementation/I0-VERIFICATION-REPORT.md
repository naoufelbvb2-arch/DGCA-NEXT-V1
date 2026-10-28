> Historical RC4.1 artifact. L01 used RC4.2; current authorities are `docs/specs/DGCA_CORE_RC4_3.md` and `docs/specs/DGCA_LLA_RC4_3.md`. Historical paths/results remain reproducible at their recorded commits. See `I1-L01-SOURCE-MIGRATION.md` and the approved I2 S01–S03 execution contract.

# I0 verification report

Date: 2026-10-27 (America/New_York). Status: **I0 REVIEW READY**.

Repository: `naoufelbvb2-arch/DGCA-NEXT-V1`.
Working/delivery branch: `feature/i0-contract-foundation` only.
No merge into main, force push, scientific edit, or other-repository change.

- Starting SHA: `b86be656f4022c14df2ede7b3ed1d907dfce5541`.
- Tested implementation SHA: `f1775883ff0315e104966a85b08bde55a084f1ae`.
- Default-branch source SHA inspected: `75f363c8ea61e2ff3d4543ae829de6e30c964e32`.
- Delivery adds this report to the tested implementation. The final delivery SHA
  is given in the accompanying completion message and is reproducible with
  `git log -1 --format=%H -- docs/implementation/I0-VERIFICATION-REPORT.md`.
  This avoids embedding a commit's own hash inside that commit.

## Changed files

| File | Change |
|---|---|
| `.gitattributes` | Preserve exact scientific bytes; LF source files |
| `.gitignore` | Ignore local environments, caches, build and test artifacts |
| `.github/workflows/validate.yml` | Narrow read-only validation on Ubuntu/Windows, Python 3.14 |
| `pyproject.toml` | src packaging, no runtime dependencies, pinned dev tools, validation settings |
| `README.md` | Installation, exact commands, APIs, scope and unresolved values |
| `src/dgca_next/__init__.py` | Final typed version identifier, no engine API |
| `src/dgca_next/__main__.py` | Version and raw-byte spec verification CLI |
| `src/dgca_next/contracts.py` | Physical schemas, provenance validation and separate ownership envelopes |
| `src/dgca_next/config.py` | One immutable fixed baseline reader with exact section origins |
| `src/dgca_next/integrity.py` | Pinned SHA-256/blob identity and manifest checks |
| `src/dgca_next/py.typed` | Publish typing metadata |
| `tests/test_package_import.py` | Installed import from outside repository and version consistency |
| `tests/test_contract_schemas.py` | Exhaustive address identity, strict rejection, scopes, provenance, ownership |
| `tests/test_config_determinism.py` | Full/invalid TOML, origins, immutability, process-independent fingerprint |
| `tests/test_spec_integrity.py` | Local/default-branch bytes, tampering/missing inputs, CLI failure paths |
| `tests/fixtures/i0-contract-v1.json` | Address record and fixed config digest fixture |
| `docs/implementation/I0-VERIFICATION-REPORT.md` | This verification evidence |

The two scientific specs, `SOURCE-MANIFEST.md`, and
`I0-IMPLEMENTATION-CONTRACT.md` are unchanged from the starting SHA.
Windows initially checked out CRLF bytes under `core.autocrlf=true`; the exact
existing Git blob bytes were restored before validation. No scientific content
or manifest hash was changed. Tests reject CRLF corruption rather than normalize
it during integrity checking.

## Executed validation: PASS

Local runtime: Windows, CPython 3.14.4, fresh `.venv`, pytest 9.0.2,
ruff 0.14.14, mypy 1.19.1. All commands ran from the repository root.
The clean installation used network access for development tools. Tests make no
network calls. The main fetch only updated `refs/remotes/origin/main`.

| Exact command | Result / exact summary output |
|---|---|
| `python -m venv .venv` | PASS; exit 0, no output |
| `.\.venv\Scripts\python.exe -m pip install -e '.[dev]'` | PASS; exit 0, installed dgca-next 0.1.0 and pinned tools |
| `git fetch origin main:refs/remotes/origin/main` | PASS; `* [new branch] main -> origin/main` |
| `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp` | PASS; `163 passed in 1.13s` on committed implementation |
| `.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp` (repeat) | PASS; `163 passed in 1.31s` on committed implementation |
| `.\.venv\Scripts\python.exe -m ruff check .` | PASS; `All checks passed!` |
| `.\.venv\Scripts\python.exe -m ruff format --check .` | PASS; `9 files already formatted` |
| `.\.venv\Scripts\python.exe -m mypy` | PASS; `Success: no issues found in 5 source files` |
| `.\.venv\Scripts\python.exe -m pip check` | PASS; `No broken requirements found.` |
| `.\.venv\Scripts\python.exe -m dgca_next --version` | PASS; `dgca-next 0.1.0` |
| `.\.venv\Scripts\dgca-next.exe --version` | PASS; `dgca-next 0.1.0` |
| `.\.venv\Scripts\python.exe -m dgca_next verify-specs` | PASS; exact hashes below |
| `.\.venv\Scripts\dgca-next.exe verify-specs` | PASS; identical output |
| `git diff --check` | PASS; exit 0 |
| `git diff b86be656f4022c14df2ede7b3ed1d907dfce5541 HEAD --exit-code -- docs/specs docs/implementation/I0-IMPLEMENTATION-CONTRACT.md` | PASS; exit 0, no output |
| `git status --porcelain` after committed implementation tests | PASS; empty stdout, no generated tracked/untracked artifacts |

Exact committed-implementation pytest output, first run:

```text
........................................................................ [ 44%]
........................................................................ [ 88%]
...................                                                      [100%]
163 passed in 1.13s
```

Exact repeat output:

```text
........................................................................ [ 44%]
........................................................................ [ 88%]
...................                                                      [100%]
163 passed in 1.31s
```

Exact integrity output (module and installed console script):

```text
PASS docs/specs/DGCA_CORE_RC4_1.md SHA-256=f9d57129b773a93cf8603cdf2df0f6530364200ddea7ce7a070101491800a92d
PASS docs/specs/DGCA_LLA_RC4_1.md SHA-256=67d98d3e34aa0edeac2c77b955c0a0e489d3b6aac89f86959a8b626c4b4d2b69
```

PASS totals: **163/163 tests per run; 326 passing test executions over the two
recorded committed-implementation runs; 0 skipped tests**. All configured local
lint, formatting and type checks passed. The staged implementation also passed
`git diff --cached --check` and had no staged scientific-file differences.

## FAIL and corrected development attempts

Final applicable checks: **0 FAIL, 0 test errors**.

- Initial sandboxed Git clone and pip install could not reach the network.
  Both succeeded with approved network execution; no unapproved source was used.
- Initial `.\.venv\Scripts\python.exe -m pytest -q` ended with
  `127 passed, 36 errors in 8.75s`. All 36 errors were fixture setup failures:
  Windows denied access to the shared system `pytest-of-Laptop` directory.
  The documented workspace-local `--basetemp=.pytest-tmp` resolves this without
  skipping tests or suppressing warnings. The complete suite then passed.
- Initial lint reported two fixable import findings and formatting reported one
  file needing formatting. Imports/formatting were corrected and all final
  configured checks passed. Warnings remain errors in pytest.
- Sandboxed Git occasionally printed a permission warning for the user's global
  ignore file; repository status stdout was empty on the committed check, and
  the same Git checks with normal approved execution did not have that warning.

## NOT_RUN

- **57 named scientific tests**: LLA-T01–LLA-T41 and LG-T01–LG-T16.
- Core §13 scientific/transaction/dynamics program and empirical Gates A–E
  (beyond the narrow I0 schema/integrity portions), including SIC projection,
  save/load, crash recovery, probes, contextual predictions, native Assembly
  emergence, hierarchy, surface attestation, G1/G2 and G3 experiments.
- Remote GitHub Actions matrix execution was not part of the local evidence
  above. The workflow is supplied for the pushed branch; remote results, if
  available, are reported separately in the completion message. Ubuntu was not
  locally executed. No remote or cross-platform PASS is inferred from Windows.
- Other Python minor versions, GPUs, performance/scaling and empirical quality.

No scientific tests were represented by dummy tests or fake learning outputs.
These NOT_RUN items are outside I0, and are not conditional local test passes.

## Acceptance gates

| Gate | Disposition | Evidence / boundary |
|---|---|---|
| I0-G01 | PASS | Both files on inspected main ref match source hashes; local raw hashes and manifest match; committed test run leaves clean status |
| I0-G02 | PASS | Fresh venv install; isolated subprocess import outside repository; CLI and README |
| I0-G03 | PASS | All 12,288 addresses round-trip through IDs and binary records; region aliases/bounds rejected |
| I0-G04 | PASS | Full mode/origin matrix plus invalid enums, types and root/session combinations; shape validation only |
| I0-G05 | PASS | Every registry literal has a source section; complete fixed TOML only; missing/unknown/contradictory values fail; same config hash in fresh process |
| I0-G06 | PASS | Separate frozen W/R/HSlow types; immutable byte snapshots only; ReadOnlyState has no writable persistent state or caller R |
| I0-G07 | PASS | Two repeat complete runs, strict warning policy, lint/format/type checks clean, exact outputs above |
| I0-G08 | PASS | No engine methods/CLI; scientific tests explicitly NOT_RUN; first scientific gate remains I3/I4 |

## Blockers, unresolved decisions and limitations

**I0 blockers: none.** No discrepancy requiring a new scientific decision was
needed to implement the mandatory I0 schemas and checks. RC4.1 remains
**NOT FROZEN / NOT IMPLEMENTED / NOT EMPIRICALLY VERIFIED** as a scientific model.
This foundation makes no empirical claim and does not authorize I1 or merging.

Future decisions deliberately left unresolved:

- Core §11 requires a recorded experiment seed but supplies no global default.
  `random_seed` raises `UnresolvedParameter`; select/version it before experiments.
- No VISION/AUDIO initial adaptive threshold was inferred from the LANGUAGE-only
  first-lab default. Both initial-threshold requests remain unresolved in I0.
- Core §3.1 leaves raw-surface feature extraction outside scope. No tokenizer or
  semantic representation was invented.
- `tau_ctx_q6` is an admission-calibrated immutable per-owner statistic (Core
  §5.1), not an absent global tuning value to fill. Requesting a global default
  fails explicitly.
- Exact future runtime W/R/H payload schemas, journaling and transaction
  implementation remain for later milestones. I0 envelopes do not deserialize
  arbitrary bytes into a claimed valid neural state.
- Root lifecycle, strict monotonic IDs across events, derived parent proofs,
  replay scheduling and generation prompt ordering require future stateful
  validation. I0 validates typed single-event input shapes only. It does not
  impose a starting exposure ID, enable replay or implement synthetic LEARN.
- Address record tags/version, Python package version, JSON manifest format,
  supported Python minor version and `REPLAY_RECALLED` spelling are documented
  administrative choices, not new numerical scientific parameters.

Stop point: **I0 REVIEW READY**. User review controls merge and the next milestone.
