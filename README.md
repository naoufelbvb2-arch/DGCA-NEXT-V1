# DGCA NEXT V1

Research implementation of the **Dynamic Graph Cognitive Architecture — DCR**.

## Project status

**I0 accepted. I1 — Graph Anatomy: verified structural subset; latent policy blocked.**

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

## I1 physical graph

`dgca_next.graph` adds a sparse physical graph over the existing I0 IDs. Reading
or iterating the 12,288 logical cells never stores or commits missing cells. Cell
metadata, synapse records, latent slots and public index views are immutable.
Activity and adaptation remain outside the graph, under the unchanged I0 R and
HSlow boundaries. No LLA, activation, learning or generation is implemented.

Only the explicitly named **FixtureBuilder** can construct synthetic committed
cells and links in I1. Records require `fixture_only=True`. A fixture's root count
is asserted test data, not proof of independent observations or accepted evidence.
There is no production synapse-admission interface.

```python
from dgca_next.contracts import CellAddress, SynapseKey, SynapseScope
from dgca_next.graph import FixtureBuilder, SparseNetwork, Synapse, SynapseState

graph = SparseNetwork()
builder = FixtureBuilder(graph)
source, target = CellAddress.from_cell_id(8192), CellAddress.from_cell_id(8193)
key = SynapseKey(source, target, SynapseScope.LOCAL)
with builder.transaction() as tx:
    tx.commit_cells([source.cell_id, target.cell_id], committed_event=0)
    tx.inject_slot(target.cell_id, 0, source.cell_id)  # Explicit fixture target.
    tx.reserve(key, source.cell_id)
    tx.add_synapse(Synapse(key, 0, SynapseState.CANDIDATE,
                           0.6, 1.0, 0.0, 1, 2, fixture_only=True))
assert graph.structurally_eligible(source.cell_id, target.cell_id)
assert graph.outgoing_usage(source.cell_id).total == 1
assert graph.reserved_keys() == ()  # Claim transferred to live key.
graph.validate_graph()
```

Geometry functions return inclusive, clipped Manhattan balls of radius 0, 1 or 2,
in row/column order within one region. They never select latent targets. Slot
indexing is an administrative schema: 0–5 coactive intra, 6–11 fixed local,
12–17 coactive inter, 18–23 fixed topographic. Cross groups allocate three slots
to each other region in region-byte order. Empty positions stay empty until an
explicit fixture target is injected. The fixture API rejects redundant targets
within one owner's slots rather than choosing or normalizing the caller's input.
This conservative construction convention does not resolve production selection
or overlap handling under the missing inherited policy.

Structural eligibility is exactly the either-endpoint OR predicate. The reverse
index records every occupied `(owner_id, slot_index)` reference. Distinct live
keys plus reserved future keys share a 64-outgoing cap per source; cross-region
endpoints (including ASSOCIATIVE keys) share its 12-cross cap. Incoming keys do
not debit target outgoing capacity. Repeated claimants and multiple claims for
the same intended key consume one key. Releasing one claimant preserves the
others; fulfillment transfers the entire key to live storage. Slot pins are
explicit physical claimant IDs, separate from synapse reservations; fulfillment
does not silently remove a pin.

Episodic fixtures obey four outgoing links per source and the existing network
`floor(.10 * committedCells)` cap. Membership IDs exercise the 12-membership bound
only; they create no Assemblies. Consolidated and explicitly protected synapses
cannot be deleted by the fixture API. Slot removal respects fixed categories,
live links in both directions, protection and candidate pins. A separate
`remove_fixture_slot` primitive supports explicit safe synthetic teardown; it is
not a production recycling policy. Pending fixture reservations must first be
released before tearing down their backing pair.

Exact repeated fixture mutations are strict no-ops; conflicting duplicate cells,
occupied slots and link payloads fail. `transaction()` creates one single-use
shadow, commits automatically on successful context exit, and discards all
staged changes on error. An operation error invalidates that transaction, even
if the caller catches it. Manual `commit()`/`rollback()` are available outside
the context-manager form. Stale shadows cannot overwrite later changes. Batches
that exceed capacity fail in full; I1 does not rank or partially admit proposals.
This is a single-thread in-memory contract, not durable crash recovery.

`validate_graph()` independently reconstructs inverse indices, directed-key
counts, endpoint eligibility, slot shapes and caps. Publication also compares
the before-image to prevent loss of protected slots, pins, links or commitment.
`MutationStage`/`InjectedFailure` exercise faults after shadow cell, slot, reverse
index, link, reservation and budget writes, and immediately before publication.
No fallible work follows the single published-state assignment. `debug_dump()`
and `structural_hash` provide sorted diagnostics, including all bookkeeping and
fixture wiring-log deltas; they are not persistence or save/load formats.

**UNRESOLVED_LATENT_POLICY:** Core §1.3 names inherited highest-coactivity,
local/inter/topographic target policies and an original confirmation window,
without providing their complete executable procedure in either normative spec.
`initialize_latent_neighborhoods()` and unprotected `recycle_slot()` therefore
raise `UnresolvedLatentPolicy`. Protected recycling attempts return their more
specific rejection diagnostics. Production auto-wiring, cross-category overlap
selection and confirmation-window recycling need a separately reviewed rule.
I1 cannot be declared fully complete while this policy boundary remains open.

The same installation and validation commands above run all I0 and I1 checks.
Use `python -m pytest -q --basetemp=.pytest-tmp -rs` to display the two explicitly
**POLICY_BLOCKED** skips (I1-T09 and I1-T26 production-policy execution). Tests of
their fail-closed API behavior run separately and do not count as executing the
missing policies. The full-network test writes measurements to the ignored
`.pytest_cache/i1-stress-metrics.json`; it has no invented time or memory pass
threshold. All constructed graphs and quality calculations remain synthetic
contract fixtures. LLA-T01–T41 and LG-T01–T16 remain scientifically **NOT_RUN**.

The workflow retains I0 validation and also runs I1 feature pushes and main PRs
on Ubuntu/Windows. Executed increment/gate evidence and policy limitations are
recorded in `docs/implementation/I1-VERIFICATION-REPORT.md`. Stop at
**I1 PARTIAL / POLICY_BLOCKED**; I2 requires separate review authorization.
