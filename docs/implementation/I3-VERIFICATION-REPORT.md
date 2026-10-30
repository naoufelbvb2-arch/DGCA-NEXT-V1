# I3 verification report — PARTIAL / SPEC_BLOCKED

## Scope and result

The I3 production learning contract is **not implemented**. No external EVENT
has been accepted, no real root has completed, and no learned LOCAL or
ASSOCIATIVE synapse has been created. The cold-start learning experiment,
save/load of learned synapses, and subsequent causal-effect comparison are
**NOT_RUN / SPEC_BLOCKED**. The absence of results is not an empirical finding
that the scientific model cannot learn.

Two decisions require scientific clarification, detailed with reproducible
counterexamples in [I3-R00-PRODUCTION-PREFLIGHT.md](I3-R00-PRODUCTION-PREFLIGHT.md):

1. **I3-S01:** the 12-cell birth limit is specified, but the selection of an
   admitted sensory cohort when more than 12 direct receivers qualify is not.
   The latent-target ranking applies after cohort admission. `project` of
   features `a`, `ab`, `c`, and `d`, each with support `1`, yields 16 distinct
   equally supported receivers on an empty graph.
2. **I3-S02:** the specifications provide the gain bounds and adaptation
   equations, but do not specify the initial newborn gain and firing EMA or the
   initial regional firing EMA. An explicit caller-provided complete H image
   permits preflight of known IDs, but does not itself define a general newborn
   rule. An approved initialization profile and newborn rule are needed.

These decisions are not the only remaining work: production graph authority,
validated EVENT witnesses, durable EVENT/END publication, actual evidence and
novelty, and the empirical trial are also unimplemented. Even with an explicit
H image and a non-oversubscribed cohort, `RootStore.event` fails closed with
`I3-R02`; `end` fails closed with `I3-R03`. No fixture can authorize a
production synapse. Automatic production recycling remains disabled.

## Repository and changes

- Branch: `feature/i3-local-learning`; baseline I3 contract commit:
  `aacd16f5c014699ec828e2988ccdea9bb59bc800`; accepted I2 main base:
  `f63935c143b3fa1ef016078a58309f648a51bd22`.
- Implementation commits: `91413277fe48c84152c9f30da7abc10c7dde9841`,
  `8b5e25f163f1a51c10958a123c0219db3d4b9801`,
  `ef37750105bf3ca9c49a5f48c36becb5d74cfdb8`,
  `426f8f6b184139854e71ea2eb7dbe00baba085de`, and
  `5cc9ada6a9638f9637156832e1b029c2334b4fd9`. This report is committed
  separately; its commit and final-head CI must be read from Git history and
  the branch's final workflow run, avoiding a self-referential commit hash.
- Changed paths relative to the I3 contract baseline:
  `.github/workflows/validate.yml`, `README.md`,
  `docs/implementation/I3-R00-PRODUCTION-PREFLIGHT.md`,
  `docs/implementation/I3-VERIFICATION-REPORT.md`,
  `src/dgca_next/learning/__init__.py`,
  `src/dgca_next/learning/evidence.py`,
  `src/dgca_next/learning/observation.py`,
  `src/dgca_next/persistence/__init__.py`,
  `src/dgca_next/persistence/codec.py`,
  `src/dgca_next/persistence/store.py`,
  `tests/experiments/test_i3_cold_learning.py`,
  `tests/test_i3_r01_root_store.py`,
  `tests/test_i3_r02_ingress_preflight.py`, and
  `tests/test_i3_r03_r04_evidence_arithmetic.py`.
- Core RC4.3 SHA-256:
  `41764eea3ddccdbd692325ecf7f03c243bf259bb46cc2b1820f7648125f3a53a`.
  LLA RC4.3 SHA-256:
  `4c70fd84a8356e7871e6ac5bd14eeb800bf2347342512c4901e1e2191a89e958`.
  Both specifications and the I0 configuration contract remain unchanged.

## Implemented subsets and numerical traces

The SQLite skeleton persists an explicitly supplied H image, an empty W marker
and cold R marker, tracks one OPEN root and a non-reusable high watermark,
and atomically restores H_BEGIN on ABORT. Its versioned H codec checks ordering,
finite binary64 values, and record schema. Tests include separate-connection
locking and subprocess termination immediately before and after BEGIN and ABORT
commits. This is **not** a complete graph codec or proof of EVENT/END crash
recovery. The code revision is caller-declared metadata, not authenticated Git
or real-world provenance. The standalone I2 read-only API is not centrally
integrated with the root guard.

Synthetic arithmetic tests exercise local and one-step associative q, root MAX
with paired y, bounded ledgers, and consolidation math. For example, local
`0.8 * 0.6 = 0.48`; associative
`0.8 * 0.6 * 0.7408182206817179 = 0.35559274592722456` in binary64, and
`0.5 * 0.5 * 0.7408182206817179 = 0.18520455517042947`. Seventeen hypothetical
fixture inputs illustrate accumulation but are **not external roots**, genuine
evidence, actual learning, or a claim of novelty detection.

The synthetic ingress guard test starts with zero cells and zero synapses.
Single-feature `a` maps to physical IDs `8606`, `9345`, `11795`, `12181`
with `X_fixed=1000000`; missing H causes I3-S02 before publication. The
four-feature example maps to IDs `8286`, `8465`, `8606`, `8649`, `8694`,
`9227`, `9345`, `9902`, `9912`, `10128`, `10273`, `10513`, `11524`, `11641`,
`11795`, `12181`, all `1000000`; it causes I3-S01 before publication. Both
test roots are aborted, leaving test high watermark 2, accepted events 0,
completed external roots 0, and learned links 0. These are synthetic attempts,
not real external observations. Actual root journals, root q/y, E/S/count,
learned link IDs, H_EVENT traces, 100-close age audit, neural before/after,
AB/DB comparison, learned-network resource measurements, and persistence of
learned W are **NOT_RUN** because there are no accepted production events.

## Validation

Executed locally on Windows, Python 3.14, implementation head
`5cc9ada6a9638f9637156832e1b029c2334b4fd9`:

| Command | Result |
| --- | --- |
| `.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp -rs` | **PASS:** `621 passed in 7.99s`; includes the 578 existing tests; no skips reported. |
| `.venv\Scripts\python.exe -m ruff check .` | **PASS:** `All checks passed!` |
| `.venv\Scripts\python.exe -m ruff format --check .` | **PASS:** `69 files already formatted` |
| `.venv\Scripts\python.exe -m mypy` | **PASS:** `Success: no issues found in 38 source files` |
| `.venv\Scripts\python.exe -m dgca_next verify-specs` | **PASS:** both RC4.3 hashes shown above. |
| `.venv\Scripts\python.exe -m pip check` | **PASS:** `No broken requirements found.` |
| `git diff --check` | **PASS:** no output. |
| `git diff aacd16f --exit-code -- docs/specs src/dgca_next/config.py tests/fixtures/i0-contract-v1.json` | **PASS:** exit 0; no tracked changes to those paths. |

**FAIL:** no outstanding failures in the completed local checks. **SKIPPED:**
none reported by pytest. **NOT_RUN:** production tests and experiments listed
above. The baseline run before I3 changes was `578 passed in 7.16s`.

On implementation head `5cc9ada6a9638f9637156832e1b029c2334b4fd9`,
[GitHub Actions run 40694447151](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/40694447151)
completed **PASS** on both `ubuntu-latest` and `windows-latest`, including the
workflow's two pytest executions, integrity, Ruff, format, mypy, and cleanliness
steps. The report commit triggers a separate final-head run; its conclusion is
recorded by [branch workflow runs](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/workflows/validate.yml?query=branch%3Afeature%2Fi3-local-learning).
The exact final-head conclusion must be checked after publication.

## Acceptance gates

| Gate | Verdict | Evidence or limitation |
| --- | --- | --- |
| I3-G01 | **SPEC_BLOCKED** | BEGIN/ABORT and high watermark subset pass; no trusted accepted EVENT, event provenance, or completed roots. |
| I3-G02 | **SPEC_BLOCKED** | I3-S01 and I3-S02; no production admissions or latent wiring. |
| I3-G03 | **NOT_RUN** | No real witnesses, proposals, D_event/D_close, END arbitration or production publication. |
| I3-G04 | **NOT_RUN** | Pure fixture arithmetic passes; real root MAX, evidence, and consolidation do not exist. |
| I3-G05 | **NOT_RUN** | BEGIN/ABORT crash subset passes; EVENT/END atomicity, learned W save/load and end-to-end recovery are absent. |
| I3-G06 | **NOT_RUN** | No genuine event-local novelty producer or 100 completed-root audit; automatic production recycling remains off. |
| I3-G07 | **SPEC_BLOCKED** | Actual cold-start training, repeated real roots, persistence and causal effect are not run; zero learned links is not an empirical failure. |
| I3-G08 | **NOT_RUN** | Local checks and both implementation-head CI jobs pass; exact final-head Ubuntu/Windows CI must be checked after report publication. |

Full I3-T01 through T28 integration cases requiring real EVENT, END, genuine
roots or learned W are **NOT_RUN**. T01/T02/T08/T09/T12/T14/T15/T21/T26/T27/T28
have only the specific independent or synthetic subsets described above, not
full production acceptance. The target named LLA integration scenarios and
the remaining complete LLA-T01–T41 and LG-T01–LG-T16 scientific scenarios are
**NOT_RUN**; existing physical sub-operator tests do not prove them. Native
Assembly formation, contextual owners, generation, and I4 remain out of scope.

Final status: **I3 PARTIAL / SPEC_BLOCKED**.
