# I3-P02 learning and atomic END verification

## Result and scope

The cold-start production experiment created and reinforced both LOCAL and
one-step ASSOCIATIVE synapses through real `RootStore` external-feature events
and atomic completed roots. The learned W survived reopening and produced
measurable synchronous and temporal neural drive in a read-only comparison.
The accepted root IDs in this experiment are `1`, `2`, `3`, and `4`; root `5`
was aborted. Root 1 committed the physical receivers without creating a link.
Roots 2–4 provided independent positive evidence, with at most one credit per
key/root. Root 5 did not add evidence.

This demonstrates the narrow P02 mechanism for one repeated physical SIC
input. It does not establish contextual learning, generalization, language
generation, real-world truth of the input, or completion of full I3. An
`EXTERNAL_DIRECT` witness records a valid API submission; private Python
capabilities and checksums are not authentication against a process that can
rewrite the entire database and code.

## Commits, paths, and scientific sources

Branch `feature/i3-local-learning`; contract parent
`00657320c9451e22a3be0148bb99409a58df15c7`.

- `87698d6918828356fea6759c54e7d9f3831ae730` — production evidence schema and
  full-precision root maximum.
- `745120aeb0aa1f62f91d5520886d956eb3721f62` — witnessed EVENT proposal staging.
- `8b2aa65bff05fc1c012ba1bbb4937050da2020e9` — atomic END, versioned binary
  checkpoints, production experiment, and recovery tests.
- `b5380b4b4141905d111a75f62565244dddab0d71` — production/fixture separation,
  shared evidence arithmetic, and completed-event confirmation clock.
- This report and the trace-output enhancement are committed separately; use
  Git history for that commit's SHA rather than a self-referential value here.

Changed paths relative to the P02 contract parent:

- `README.md`;
- `src/dgca_next/graph/audit.py`, `network.py`, `production.py`, `synapse.py`;
- `src/dgca_next/learning/evidence.py`, `production_event.py`, `proposals.py`,
  `settlement.py`;
- `src/dgca_next/persistence/binary_records.py`, `graph_codec.py`,
  `production_store.py`, `store.py`;
- `tests/experiments/i3_p02_cold_trace.py`,
  `tests/test_i3_p01_production_event.py`, `tests/test_i3_p02_binary_records.py`,
  `tests/test_i3_p02_learning.py`, `tests/test_i3_p02_proposals.py`,
  `tests/test_i3_r03_r04_evidence_arithmetic.py`;
- `docs/implementation/I3-P02-LEARNING-END-VERIFICATION-REPORT.md`.

The RC4.4 sources are unchanged. Core SHA-256:
`3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c`;
LLA SHA-256:
`ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0`.
Configuration SHA-256:
`088363eb89484c9605fa52e7c06743e5a1867be22bf3d87692492221fd317e27`.

P02 database schema is version 3. W, EVENT, proposal and close records use
tag/version `(0x57,2)`, `(0x45,2)`, `(0x50,2)`, `(0x43,2)` respectively,
with a u32 big-endian payload length, fixed-width integer fields and finite
big-endian binary64 values. The approved H profile remains version-pinned.
The sampled post-root-3 W SHA-256 is
`cc97d34f2ef7d7cfaf94305669d571d75407e21e0eac10ccf4771debeb05556d`;
H SHA-256 is
`5daa60a3aaccc3ee116f5455c66d014afaee89b56aec87a4497c1b3ab7334aed`.
An older version-2 P01 production database is explicitly rejected; the old
explicit-H fixture skeleton remains separate and cannot publish production
events or evidence.

## Reproducible external-root trace

Run `.venv\Scripts\python.exe tests/experiments/i3_p02_cold_trace.py` on
Windows, or `python tests/experiments/i3_p02_cold_trace.py` in an installed
Python 3.14 environment. The script starts an empty production database,
submits only ordinary feature tuples, inspects actual saved physical state, and
uses no fixture graph, injected synapse, expected-answer label, or privileged
learning key. Its test code revision is the explicitly declared value `a` × 40;
that is metadata, not an assertion that Git has that SHA.

1. Root 1 / global EVENT 0 observes `a` with support `1`, committing IDs
   `8606`, `9345`, `11795`, and `12181`. The birth event has no eligible
   proposal. END completes the root with **zero learned synapses**.
2. Root 2 has global events 1 and 2, both observing `a`. For the example keys
   below, source and target direct `X_fixed` are both `1000000`; the source
   is in the actual Pass-1 emitter frontier and, for ASSOCIATIVE, the previous
   actual F_step. The source/target observation digest is
   `87265149bf7ca770278f06eab98b2f3ee85ced8d1bbea0d2b954648bb6d86b3e`.
   There are 36 staged proposals and END selects 24 link/root winners. Both
   selected examples have actual `D_event=1` and `D_close=1`.
3. Root 3 has global events 3 and 4 and adds one independent credit to each
   repeated eligible key. A restart returns identical W, H, synapse records,
   journals and completed-root count 3. Root 4 repeats the genuine observations
   and crosses the LOCAL mass threshold. Root 5 submits `ab`, lawfully births
   `8694`, `10273`, `10513`, `11641`, then ABORTs without changing any link.

| Key and root | Source event → target event | Source A → target A | q / paired y | E_ext / S / root count / Q | State |
| --- | --- | --- | --- | --- | --- |
| LOCAL `8606→9345`, 2 | 2 → 2 | `1.0 → 1.0` | `1.0 / 1.0` | `1.0 / 1.0 / 1 / 0.1` | CANDIDATE |
| ASSOC `8606→9345`, 2 | 1 → 2 | `0.7272727272727273 → 1.0` | `0.5387768877685221 / 1.0` | `0.5387768877685221 / 1.0 / 1 / 0.05387768877685221` | CANDIDATE |
| LOCAL `8606→9345`, 3 | 4 → 4 | `1.0 → 1.0` | `1.0 / 1.0` | `2.0 / 1.0 / 2 / 0.2` | CANDIDATE |
| ASSOC `8606→9345`, 3 | 3 → 4 | `0.7270689090909092 → 1.0` | `0.538625895545725 / 1.0` | `1.077402783314247 / 1.0 / 2 / 0.1077402783314247` | CANDIDATE |
| LOCAL `8606→9345`, 4 | 6 → 6 | `1.0 → 1.0` | `1.0 / 1.0` | `3.0 / 1.0 / 3 / 0.3` | CONSOLIDATED |
| ASSOC `8606→9345`, 4 | 5 → 6 | `0.7266155086363637 → 1.0` | `0.5382900082277323 / 1.0` | `1.6156927915419792 / 1.0 / 3 / 0.16156927915419791` | CANDIDATE |

Within root 2, repeated LOCAL proposals reduce to the largest **full binary64**
q and retain its paired y; only one root confirmation is published. No staged
proposal has live Q or E/S/count before END. The ASSOCIATIVE source activity
is the frozen previous-event final value, with no intervening boundary.

For read-only comparison, both runs use the same four committed physical
cells, topology, H snapshot, and two `a` feature events. The comparator W is
the saved genuine production graph immediately after root 1, before any links;
it is not a hand-edited graph. At root 3's learned W, the synchronous `P_S`
at each of the four IDs is `0.3756819435817961` versus zero in the comparator;
the next-event temporal `P_T` is `0.2169510788785245` versus zero. The store
W, H, and root status are unchanged by the read-only runs.

The raw H_BEGIN and H_ABORT bytes for root 5 are identical:

```text
444743412d48340167a2196c02d2235f2d40ca6fe1e9d50bd0397b15b1d09d92692720c2260851e6480100000082000000040000219e3feff0f3ea3f39d7000024813feff0f3ea3f39d700002e133feff0f3ea3f39d700002f953feff0f3ea3f39d7000000040000219e3fd34e7115ecd14e000024813fd34e7115ecd14e00002e133fd34e7115ecd14e00002f953fd34e7115ecd14e00000001023fcd70a3d70a3d7200000001023fd25d911bc6affd
```

Both have SHA-256
`6b79ad7e629e8954e99131212265a37e99265206a24c3a932d83c191d3712208`.
The root-5 birth survives ABORT, prior completed H and all learned links remain,
and its aborted proposals contribute no external count.

## Verification and recovery

The existing 664 P01 and earlier tests remain. Local Windows / Python 3.14:

| Exact command | Result |
| --- | --- |
| `.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp -rs` | **PASS:** `682 passed in 79.25s`; no skips. |
| `.venv\Scripts\python.exe -m pytest -q tests/test_i3_p02_learning.py tests/test_i3_p02_proposals.py tests/test_i3_p02_binary_records.py --basetemp=.pytest-tmp -rs` | **PASS:** `18 passed in 39.67s`. |
| `.venv\Scripts\python.exe tests/experiments/i3_p02_cold_trace.py` | **PASS:** actual production trace above, exit 0. |
| `.venv\Scripts\python.exe -m ruff check .` | **PASS:** `All checks passed!` |
| `.venv\Scripts\python.exe -m ruff format --check .` | **PASS:** `83 files already formatted`. |
| `.venv\Scripts\python.exe -m mypy` | **PASS:** `Success: no issues found in 46 source files`. |
| `.venv\Scripts\python.exe -m dgca_next verify-specs` | **PASS:** both source hashes above. |
| `.venv\Scripts\python.exe -m pip check` | **PASS:** `No broken requirements found.` |
| `git diff --check` | **PASS:** no output. |
| `git diff --exit-code 0065732 -- docs/specs` | **PASS:** exit 0; no scientific source changes. |
| `git status --porcelain` at implementation commit | **PASS:** no tracked or untracked changes. |

The production tests use subprocess `os._exit(71)` before and after END commit
and before and after an EVENT commit with already learned links. Reopen yields
the whole pre- or post-state; duplicate END returns the existing result without
double credit. Existing production BEGIN/EVENT/ABORT crash tests also run in the
full suite. The synthetic isolated stale-latent shadow checks refusal without
publishing evidence; the synthetic sub-millionth q near-tie checks the exact
production comparator without authorizing a link. Bounded E/S arithmetic is
shared with fixture-level saturation tests; those numeric fixtures are not
counted as external learning evidence.

**FAIL:** none in the final local checks. **SKIPPED:** none reported.
**SPEC_BLOCKED:** none identified for the implemented P02 scope.
**EMPIRICAL_BLOCKED:** none for the two requested link types in this narrow
experiment. **NOT_RUN:** full I3, P03 novelty/recycling, contextual owners,
Assemblies, Replay, language generation, and the 57 complete named LLA/LG
scientific scenarios; component tests do not establish those scenarios.

Implementation-head CI: [run 40815855022](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/40815855022)
completed **PASS on Ubuntu and Windows** for
`b5380b4b4141905d111a75f62565244dddab0d71`.
The report commit triggers a distinct final-head run; its actual SHA and
conclusion must be checked in [branch workflow history](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/workflows/validate.yml?query=branch%3Afeature%2Fi3-local-learning).

## P02 acceptance matrix

| Gate | Verdict at report creation | Evidence or scope |
| --- | --- | --- |
| Checkpoint A / T01–T02 | **PASS** | Versioned production W, credits and indices round-trip; fixture writer and unverified credit construction are rejected. |
| Checkpoint B / T03–T04, T08–T09 | **PASS** | Real external direct observations, frozen Pass-1 and prior F_step; birth, empty input, boundary, OPEN and ABORT do not create external credit. |
| Checkpoint C / T05–T07, T10–T13 | **PASS** | D_event/D_close, isolated stale refusal, full-q paired maximum, existing golden arithmetic, bounded shared update, real consolidation, atomic END, idempotence, H rollback. |
| Checkpoint D / T14–T17 | **PASS** | Actual LOCAL and ASSOC from zero links; independent reinforcement, later births, reboot, read-only P_S/P_T comparison and subprocess failure injection. |
| T18 / T20 | **PASS** for scope | No owners, native Assemblies, Replay, generation or automatic recycling; remaining full scientific gates are NOT_RUN. |
| T19 | **NOT_RUN** at report creation | Local regressions, source integrity, lint/type and dependency checks pass; final-head Ubuntu/Windows CI awaits the report commit. |

The ordinary candidate deadline uses the count of external events in completed
roots at END; aborted events do not advance it. Confirmation remains eligible
through the stored deadline and is refused after it. This implementation does
not automatically prune the retained expired candidate. P02 checkpoints retain
before/after sparse W snapshots per EVENT for audit; storage and validation
cost therefore grow with event history and have not been optimized for large
networks. VISION/AUDIO production initialization, context-dependent owners,
novelty authority, and automatic recycling remain outside this increment.

P02 is **I3-P02 REVIEW READY** only if both final-head CI jobs pass. Full I3
remains partial and P03 must not begin without independent review.
