# DGCA NEXT V1

Research implementation of the **Dynamic Graph Cognitive Architecture — DCR**.

## Project status

**I0 — Repository & Contract Foundation. Review candidate.**

The foundation refers to two design-candidate specifications under `docs/specs/`:

- `DGCA_CORE_RC4_1.md` — Core anatomy, dynamics, assemblies, contextual memory and bounded generation.
- `DGCA_LLA_RC4_1.md` — local learning, evidence, consolidation and derived context witnesses.

Both specifications are **RC4.1 / NOT FROZEN / NOT IMPLEMENTED / NOT EMPIRICALLY VERIFIED**. They are design contracts, not evidence of model capabilities. Scientific or numerical changes require explicit documentation and tests; coding agents must not tune thresholds to make tests pass.

## Implementation direction

Python reference implementation, sparse graph, deterministic event ordering, local learning without backpropagation, CPU-first. First experiments validate actual learned synapses, native assemblies, contextual next-event retrieval, hierarchical context, and read-only autoregressive generation. Compositional G3 is a separate unproven research goal.

`DGCA NEXT` is a standalone repository; the original DGCA and DGCA LITE repositories must remain untouched.

## Development policy

- Each implementation milestone uses a feature branch, review, regression suite and recorded evidence.
- Distinguish unit tests using constructed network fixtures from empirical tests learning from real input events.
- Do not report an unexecuted test as passed.
- Maintain independent `W` (learned graph), `R` (working runtime state), and `H_slow` (slow adaptation) boundaries.
- Do not copy text labels or expected answers into the neural learning or selection path.

## I0 installation and validation

Supported reference runtime: **CPython 3.14.x**, CPU only. This single version was
chosen because it is the available local validation runtime; broader Python
compatibility is untested. The package has no runtime dependencies. Development
tools are pinned in `pyproject.toml`.

Run from the repository root on `feature/i0-contract-foundation`:

```powershell
git fetch origin main:refs/remotes/origin/main
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m dgca_next --version
.\.venv\Scripts\python.exe -m dgca_next verify-specs
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy
git diff --check
git status --porcelain
```

On Linux/macOS, substitute `.venv/bin/python` for the Windows interpreter path.
Fetching `main` only updates the remote tracking ref; it does not switch branches
or merge. Tests use that local ref to verify I0-G01 without making network calls.
For a shallow clone, fetch it explicitly before running tests. The dedicated
`.pytest-tmp` directory is disposable: pytest clears it each run. After committing
the implementation, the final status command must produce no output. Validation
must leave scientific files and the manifest unchanged.

The installed console command `dgca-next` also accepts `--version` and
`verify-specs --repo-root PATH`. Integrity checks hash **raw bytes**, compare both
SHA-256 and Git blob IDs, and check the pinned manifest rows. `.gitattributes`
preserves scientific bytes even when `core.autocrlf=true`; editing line endings
is an integrity failure.

## I0 API and limits

`dgca_next.contracts` contains strict frozen physical address, directed key, and
event-provenance schemas. Core §§1.1/3.1 define the complete 12,288-cell address
bijection and region bytes. Invalid types, bounds, self-links, region/scope pairs,
time deltas, modes, and root/session combinations raise `ValueError` without
coercion. Addresses contain no text, labels, or task roles.

`EventProvenance` represents genuine external LEARN input, recalled REPLAY input,
RETRIEVE observations, and GENERATE prompt/selected input. Declaring these modes
does not execute them. `REPLAY_RECALLED` is an administrative name for the recalled
prior-root origin in LLA §4.1. Derived contextual support is a contribution lane,
not a new event origin. This input schema does not certify external evidence,
causality, contiguous event sequences, root independence, prompt ordering, or
whether replay was enabled; those require later runtime/transaction milestones.
Synthetic LEARN inputs are unsupported by this genuine-exposure interface.

`W`, `R`, and `HSlow` are separate immutable opaque snapshot envelopes, with
ownership described in Core §4. They accept only immutable bytes.
`ReadOnlyState` accepts W/HSlow snapshots and exposes no caller R or mutable
persistent reference. These are ownership contracts, not implementations of
graph storage, scratch execution, adaptation, checkpointing, or rollback. Future
runtime payload schemas and their binary field order/version remain to be defined.

`dgca_next.config.load_lab_config()` returns the fixed RC4.1 baseline registry.
Every value has an exact Core/LLA section in `Parameter.origins`. It includes
declared future-engine constants for traceability; it activates no scientific
mechanism. `parameter(name)` raises `UnresolvedParameter` for an unregistered
value. The registry is deliberately not a complete future experiment definition.
In particular, there is no guessed random seed, VISION/AUDIO initial threshold,
tokenizer, or per-owner `tau_ctx_q6` default. The latter must be calibrated at
admission under Core §5.1 and cannot be a universal configuration constant.

```python
from dgca_next.config import load_lab_config
from dgca_next.contracts import CellAddress, Region

config = load_lab_config()
assert config.parameter("B_i").value == 64
print(config.parameter("B_i").origins)
assert CellAddress(Region.LANGUAGE, 3, 3, 6).cell_id == 8606
```

`load_lab_config(Path("lab.toml"))` requires a complete `[lab]` table containing
every registry key with the exact typed baseline value. Missing/unknown keys,
duplicates, nonfinite numbers, contradictory values, and malformed files fail.
It never silently overlays partial values. Alternate scientific configurations
need separate review and versioning; I0 supplies no tuning/ablation interface.
`LabConfig.to_json()` is a deterministic configuration manifest with origins;
`sha256` fingerprints it. It is not a neural checkpoint. The address binary
fixture declares an administrative tag/version and fixed field order, following
Core §3.1's record envelope; it does not assert a future W/R/H wire format.

All I0 tests are **contract tests**. Neural learning, Assembly formation, probes,
retrieval execution, hierarchy, generation, SIC projection, surface attestation,
and scientific success remain unimplemented. LLA-T01–T41, LG-T01–T16, and the Core
scientific validation program are **NOT_RUN**. The first scientific gate remains
I3/I4. Neither these tests nor a CI success freezes or empirically validates RC4.1.

The GitHub Actions workflow runs these checks on CPython 3.14 on Ubuntu and
Windows. See `docs/implementation/I0-VERIFICATION-REPORT.md` for the executed
commands, results, gate coverage, limitations, and unresolved decisions.
