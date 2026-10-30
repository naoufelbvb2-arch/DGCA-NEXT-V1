# I3-P03 verified novelty and recycling feasibility verification

Scope: the `feature/i3-local-learning` branch, based on accepted P02
`80ae771283bb9397660b740338e169bf6cbe8c32` and the P03 contract at
`bba5670`. Implementation and acceptance tests are in commit
`8f962b265941789ed24a4b9a32d4d5fc47f6b5ab`; this report is the subsequent
documentation commit. The current branch head and its workflow run provide the
delivery-commit identity and final-head CI results.

## Changed files

- `src/dgca_next/learning/novelty.py`: immutable journal-bound novelty and
  read-only bilateral recycling diagnostics.
- `src/dgca_next/persistence/production_store.py`: validated production APIs,
  consistent reads, and an externally invalidated journal-validation cache.
- `tests/test_i3_p03_novelty.py`: numeric, provenance, real temporal prediction,
  protection, recovery, and tampering tests.
- `tests/test_i3_p03_guard_fixtures.py`: isolated bilateral physical-guard
  mechanics, expressly not production evidence.
- `tests/experiments/i3_p03_age_trace.py`: instrumented actual-root experiment.
- `tests/experiments/test_i3_p03_real_age.py`: automated actual-root acceptance.
- `docs/implementation/I3-P03-VERIFIED-NOVELTY-VERIFICATION-REPORT.md`: this report.

## Scientific sources

Both RC4.4 sources remain unchanged and passed `python -m dgca_next verify-specs`:

| Source | SHA-256 |
| --- | --- |
| CORE RC4.4 | `3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c` |
| LLA RC4.4 | `ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0` |

## Genuine event provenance and numerical trace

Novelty is derived from a validated RootStore journal event, direct SIC support,
the receiver's pre-event commitment, and the pre-event graph and homeostasis.
The verifier reconstructs the preceding event's F_step, computes the frozen
temporal lane, and verifies both activation passes and frontiers against the
persisted event. It returns provisional records while OPEN; ABORTED events cannot
authorize a completed witness. The records carry root/event identity, event and
pre-W digests, config/spec hashes and completed-close attribution. SQLite hashes
are integrity checks, not authentication against an attacker able to rewrite
the database and its checksums.

In a real production sequence, exposure 1 committed the `a` receivers; exposure
2 learned through external events; exposure 3 event order 1, global event 4,
observed receiver 8606 with `X_fixed=1000000`. The historical frozen temporal
prediction was `P_T=0.11297496516614403`; the local residual was
`0.887025034833856` and Q6 was `887025`. This uses the event's pre-END W, not
subsequent W or a synchronous response. The cold first event has `P_T=0`.
Prediction-only activity with no direct receiver cannot issue a witness. Auxiliary
numeric tests check `.6/.5 -> 1/6` and `.6/.1 -> 5/6`; these values do not
constitute production authority.

## Actual completed-root and physical trace

The production-only harness creates and ends every root with `RootStore`; it
does not insert graphs, fake serials, or use `FixtureBuilder`. Exposure 1 with
`a=1` committed receiver IDs 8606, 9345, 11795 and 12181. An intervening root
with two genuine events was aborted, and a read-only episode was executed;
neither advanced the completed-close serial beyond 1. Exposures 3–99 used
genuine `a=0.000001` input; exposures 100 and 101 used `a=0.2, ab=1`.
The small support is external input, not a changed scientific threshold.

| Exposure / global event | Completed serial | Pair and physical occurrences | Result |
| --- | ---: | --- | --- |
| 100 / 100 | 99 | 8606 slot 0 → 9345 and 9345 slot 0 → 8606; assigned serials 0/0; ages 99/99 | `CONFIRMATION_WINDOW_NOT_ELAPSED` |
| 101 / 101 | 100 | same pair; assigned serials 0/0; ages 100/100 | `ALLOWED`; proposed replacements `(8606, 0, 8694)` and `(9345, 0, 8694)` |

For exposure 101, receiver 8606 had `X_fixed=200000`, frozen `P_T=0`,
`nu=1`, and `nu_q6=1000000`. The result is a feasibility diagnosis only;
no replacement was applied. Exposure 102 while OPEN gives
`UNVERIFIED_NOVELTY`; after completion its lack of legal current-event
replacements gives `NO_RECYCLING_REPLACEMENT`. Exposure 103 creates real LOCAL
connections through ordinary learning, and inspection refuses the old pair with
`RECYCLE_BLOCKED_LIVE_OR_PROTECTED`, even though its age exceeds 100. Existing
links were not removed or changed to produce that refusal.

The saved serial-100 state was closed and reopened; its completed witness,
decision, W and H were identical. Before/after inspection checks include
W/H, root state, synapses/evidence and graph structural hash. At serial 100 W
was 17,479 bytes, with 12 genuine learned links; at serial 98 W was 6,014 bytes.
The serial-100 W SHA-256 was
`6c4da41ce728e8718a0d91393fad0d77dbf8ca5de3c0935bcf4d75c624c252f8`, and H
SHA-256 was `147fe74532e10dfcdd91b8ce2467e12d20b2038044972e4a917db81aa52d92eb`.
The isolated test database uses the explicit test revision identifier `a` repeated
40 times; it is not a claim that this is the source commit.

The instrumented command passed in 112.39428369991947 seconds, with peak
`tracemalloc` Python allocation 4,994,306 bytes. The SQLite file was 2,899,968
bytes at serial 100 and 3,076,096 bytes after the two subsequent completed
roots. The final serial was 102. The protected pair's two ages were 102 and its
live LOCAL keys were `8606→9345` and `9345→8606`. The timing was measured while
the final local regression suite also ran; it is not a benchmark.

## Checks and acceptance gates

Commands below use the workspace's `.venv/Scripts/python.exe` on Windows:

| Command | Result |
| --- | --- |
| `python -m pytest -q --basetemp=.pytest-tmp -rs` | PASS: 693 passed in 59.82s |
| `python -m ruff check .` | PASS: All checks passed! |
| `python -m ruff format --check .` | PASS: 88 files already formatted |
| `python -m mypy` | PASS: no issues in 47 source files |
| `python -m dgca_next verify-specs` | PASS: both hashes above |
| `python -m pip check` | PASS: No broken requirements found. |
| `git diff --check` | PASS |
| `python tests/experiments/i3_p03_age_trace.py` | PASS: genuine-root trace, 112.39428369991947s, peak Python allocation 4,994,306 bytes. |

Implementation CI is [run 41095405079](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/41095405079),
for `8f962b265941789ed24a4b9a32d4d5fc47f6b5ab`: Ubuntu and Windows both PASS.
The documentation commit
triggers a separate final-head Ubuntu/Windows matrix; its actual status must be
read from the [branch workflow runs](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/workflows/validate.yml?query=branch%3Afeature%2Fi3-local-learning).

| Gate | Verdict and evidence |
| --- | --- |
| G01 | PASS: real event-bound direct support, historical pre-SIC prediction and exact residual. |
| G02 | PASS: provisional, completed, aborted, newborn and absent-direct separation; callers cannot submit scalar authority. |
| G03 | PASS: 100 actual completed external roots and the 99/100 bilateral boundary, with abort and read-only counterexamples. |
| G04 | PASS for implemented guards: actual production fixed and live links; isolated physical fixtures exercise pinned, protected, reserved, one-sided and unequal-age bilateral paths. Current P02 production codec cannot encode pin/protected fixture state; no actual production pin/protection record is claimed. |
| G05 | PASS: actual ranked bilateral candidates and an actual no-candidate refusal, with no slot mutations. |
| G06 | PASS: read-only state equality, cold reopening, and external journal-tampering rejection. |
| G07 | Local checks PASS; final-head Ubuntu/Windows CI must complete successfully before the gate is PASS. |
| G08 | PASS for the evidence recorded here, subject to final-head CI. |

## Limitations and NOT_RUN

Actual physical rewiring, automatic recycling and its ablation, full I3 novelty
benefit, contextual owners, Assemblies, Replay, multimodal behavior and language
generation are NOT_RUN and outside this slice. A high residual does not establish
semantic novelty, learning benefit, retention improvement or active recycling.
The current production codec does not persist recycling assignments or logs;
P04 would need a separately reviewed atomic mutation and fresh guard checks.
Full I3 remains partial. No new scientific parameter or scientific decision was
introduced.
