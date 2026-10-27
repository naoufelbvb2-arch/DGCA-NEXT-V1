> Historical RC4.1 artifact. Current authorities are `docs/specs/DGCA_CORE_RC4_2.md` and `docs/specs/DGCA_LLA_RC4_2.md` under the approved L01 execution contract. Historical paths/results below remain reproducible at their recorded commits; they are not current RC4.2 validation claims. See `I1-L01-SOURCE-MIGRATION.md`.

# DGCA NEXT — I0 Implementation Contract

**Revision:** I0-D01 (implementation planning, non-normative)
**Target branch:** `feature/i0-contract-foundation`
**Normative sources:** `docs/specs/DGCA_CORE_RC4_1.md` and `docs/specs/DGCA_LLA_RC4_1.md`
**Objective:** establish a deterministic, testable Python implementation foundation, **without pretending that any neural learning or language generation has been implemented**.

## A. Scope

1. Establish Python `src/` packaging using `pyproject.toml`, `pytest`, and a basic lint/type-check command. Choose one documented supported Python version (Python 3.11+ is the starting preference); no GPU, web service, UI, vector database, or training dependency.
2. Create the package `src/dgca_next/` with a minimal importable API and an immutable version identifier; no dummy learning outputs.
3. Define **minimal typed contract objects only**: canonical cell address (region, microcolumn row, column, slot), directed synapse scope, event/provenance mode, and `W` / `R` / `H_slow` ownership boundaries. Do not implement learning laws or assign semantics to cell IDs.
4. Introduce one canonical lab configuration reader whose defaults must be copied strictly from the two specifications. Every default must cite its exact Core/LLA section. When a value is absent, report it as unresolved rather than guessing.
5. Build reproducible contract tests, integrity verification, and simple deterministic serialization fixtures. Do not build a neural simulator during I0.
6. Create small CLI commands for `--version` and `verify-specs` only if they can be tested without implementing the engine.
7. Add a narrowly-scoped GitHub Actions validation workflow if repository permissions allow, else document why not.

## B. Hard boundaries

- Core contains **dumb cells**. No word IDs, raw surfaces, semantic labels, or expected next-token answers may enter neural schemas.
- `W` holds learned persistent graph data, `R` holds ephemeral working state, `H_slow` holds long-lived slow adaptation. I0 may define *ownership contracts*, not invent exact future runtime implementations.
- No backpropagation, dense embeddings, pretrained language model, or hidden oracle.
- Preserve all RC4.1 scientific text and the SHA-256 values in `docs/specs/SOURCE-MANIFEST.md`. Treat unapproved edits as hard test failures.
- No modification of DGCA or DGCA LITE repositories.
- Do not call unexecuted tests PASS. Report PASS, FAIL and NOT_RUN distinctly.
- A test using artificially seeded legal links is a **contract test**, not empirical proof that LLA forms those links.
- Scientific experiments, assemblies, learning, probes, retrieval, hierarchy, generation, and surface attestation are out of scope for I0.

## C. Target repository files (create only when useful)

```text
pyproject.toml
src/dgca_next/__init__.py
src/dgca_next/contracts.py
src/dgca_next/config.py
tests/test_package_import.py
tests/test_spec_integrity.py
tests/test_contract_schemas.py
tests/test_config_determinism.py
docs/specs/SOURCE-MANIFEST.md         # already committed to I0 branch
docs/implementation/I0-IMPLEMENTATION-CONTRACT.md  # this document
.github/workflows/validate.yml        # optional, if available
.gitignore
```

Keep implementation narrowly scoped; no 40 empty module files.

## D. I0 acceptance gates

**I0-G01:** Both specs exist on the repository's default branch; SHA-256 exactly matches the source manifest, and git status is clean after the test run.

**I0-G02:** Python package installs/imports in a clean virtual environment and validation commands are documented in README.

**I0-G03:** Addressing contracts enforce LANGUAGE/VISION/AUDIO regions; 32×16 microcolumns and 8 slots per microcolumn; deterministic identity and no accidental cross-region aliasing (Core §1.1).

**I0-G04:** Contracts reject invalid event modes and invalid provenance combinations rather than silently normalizing them.

**I0-G05:** Configuration is deterministic, with explicit origin tracking to source sections; invalid, absent or contradictory values are errors, not fallback guesses.

**I0-G06:** W/R/H_slow types are independently owned, and read-only operation interfaces do not expose mutable persistent state as a writable reference.

**I0-G07:** Repeatable test results; formatting/lint clean; all tests actually run locally, with exact command/output included.

**I0-G08:** No neural learning, Assembly birth, contextual prediction or generation result is claimed; the first scientific gate remains I3/I4.

## E. Execution and reporting

1. Work only on `feature/i0-contract-foundation`; never force-push or merge to main on your own.
2. Inspect the two RC4.1 specifications and manifest before changing code. Do not rewrite scientific rules or parameters.
3. Implement and test I0 scope; use minimal types and simple pure operations.
4. Run tests, lint, and any type check configured; record exact PASS/FAIL/NOT_RUN totals.
5. Produce an I0 completion report: changed files, branch, starting/final SHAs, exact test commands, skipped checks, limitations, and any spec ambiguity requiring a separate design decision.
6. Commit and push implementation; stop at **I0 REVIEW READY**. The user decides merge and start of I1.

**Exit policy:** No conditional PASS by suppressing warnings or inventing missing Core dynamics. If spec ambiguities block a mandatory I0 gate, report **BLOCKED** with the smallest reproducer.
