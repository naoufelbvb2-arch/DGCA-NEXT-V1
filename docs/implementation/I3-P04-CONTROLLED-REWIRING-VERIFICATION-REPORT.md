# I3-P04 controlled atomic rewiring verification

Branch `feature/i3-local-learning`; accepted P03 delivery
`bc2e195946b98a14fc138498761f0e435ea33375`, P04 contract base
`78b242b8a3586a6ba5b8f0790aef1741bcf3c189`.

Implementation commit `7712593416ce8710918027b8f287c8e9ae1abd47` and additional
ABORT crash tests commit `a175f27ca670ccb3fa546af63afdac18776565e5` and
initial report commit `215413338d22ae7eff4f6fb5c08067be1de70135` precede
this report's status update. The branch head identifies the delivery;
the [branch workflow](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/workflows/validate.yml?query=branch%3Afeature%2Fi3-local-learning)
shows the final-head Ubuntu and Windows results.

## Changed files

- `src/dgca_next/graph/audit.py`, `network.py`, and `recycling.py`: graph audit
  and distinct production recycling record support.
- `src/dgca_next/learning/novelty.py` and `production_rewiring.py`: event-bound
  staged END verification, ranked bilateral replacement and physical shadow.
- `src/dgca_next/persistence/graph_codec.py` and `production_store.py`: versioned
  W encoding, restricted durable root request, atomic END and replay audit.
- `tests/test_i3_p04_requests.py`: request, refusal, tamper and crash cases.
- `tests/experiments/i3_p04_real_rewiring.py`,
  `test_i3_p04_real_rewiring.py`, and `test_i3_p04_one_sided.py`: production
  root experiments, no fixture topology.
- `docs/implementation/I3-P04-CONTROLLED-REWIRING-VERIFICATION-REPORT.md`:
  this report.

## Scientific sources and compatibility

RC4.4 is unchanged. `python -m dgca_next verify-specs` passed:

| Source | SHA-256 |
| --- | --- |
| CORE RC4.4 | `3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c` |
| LLA RC4.4 | `ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0` |

Production journal schema is 4. Existing journal schema 3 is explicitly
rejected with `UNSUPPORTED_PRODUCTION_SCHEMA: P04 requires version 4`;
automatic migration is NOT implemented. W records use version 2 before any
recycling and version 3 once modified slots and production recycling records
exist. Cold journal validation replays ordinary evidence settlement and the
recorded physical decision from the saved root/event, checking the resulting W
and close hash. It recomputes the frozen temporal proof, without replaying the
two activation passes or adding evidence during recovery. Source/event hashes
are integrity checks, not authentication against arbitrary database forgery.

## Genuine bilateral experiment

The experiment uses a fresh SQLite database and only real RootStore external
events; the test's declared code revision is `a` repeated 40 times, not the
source commit. Exposure 1 with `a=1` committed four physical receivers.
Exposure 2 was aborted; a read-only episode also left the close serial unchanged.
Exposures 3–99 each completed real external `a=0.000001` events. Exposure 100
submitted two `a=0.2, ab=1` events and staged the request for its last event:
at close serial 99 the original pair was refused with
`CONFIRMATION_WINDOW_NOT_ELAPSED`. Exposure 101 submitted the same genuine
feature bundle, staged the same physical request, and completed at serial 100.

The deterministic nominated pair was the first two sorted `a` birth receiver
IDs, 8606 and 9345. Root 101's final event was global event 101, order 0.
Receiver 8606 was committed before that event; its canonical `X_fixed=200000`,
frozen pre-SIC `P_T=0`, local novelty `1.0`, and Q6 novelty `1000000`. Each
original dynamic occurrence was assigned at completed-close serial 0 and aged
100 closes. The post-evidence graph had no live link, reservation or protected
slot on the original pair. The single committed END produced:

| Owner | Slot/category | Old target | New target | New assigned serial |
| ---: | --- | ---: | ---: | ---: |
| 8606 | 0 / COACTIVE_INTRA | 9345 | 8694 | 100 |
| 9345 | 0 / COACTIVE_INTRA | 8606 | 8694 | 100 |

Both old reverse references disappeared and both new references appeared in
the same saved W. The ordered production recycling record contains the physical
changes, root/event/order, completed serial, observation and novelty digests,
prediction, support and Q6. Previous event/root W snapshots preserve the old
assignment metadata; the current W preserves the new metadata. The W SHA-256
immediately before END was
`e66cde28104c46fc6c062d97df5bdc2963a29ee9a3e4f5453b031ba2dff85f79`;
after END it was
`1586dd35a478346b31cd219fa30d5c42c768ef2847472585c274a9f0aa39d0fe`.
Post-END H SHA-256 was
`3f42c2aaad31a872b485e1b006bff51a969ca1672614a28f4f1117902f7a01e9`.
For reproducibility, SHA-256 of each saved `wiring` and `reverse` list
encoded using `encode_record(0x60, 1, list)` was:

| Index | Before END | After END |
| --- | --- | --- |
| Wiring | `8569da5f96e7c30dfb09d2dfb2b3f652cb9f1ca960b2bf7ad20322f0635c0065` | `b4bc1a7d65382c8b838abaf05aa1fc31f196e95d4039c6df22ba6ff3e5bc122c` |
| Reverse | `16dd6901af19c8d1a1bb1815672ee0f0ca1e6e3596584084fbcc4f22af45d6bf` | `8071b1467fcd9e7532b3cb922ec48ea9ae55c1b667779bb3f4787e96f2e8949f` |

The same experiment checked that all synapses after rewiring exactly match
ordinary post-evidence settlement, including their credits and numeric state.
A sampled preexisting `8606→8694 LOCAL` link retained `S=0.8845598845598845`,
`E_ext=0.20695192419264244`, external root count 1 and
`Q=0.018306137017328975` across this END; 36 total live links were retained.
A read-only `ab=1` probe had maximum synchronous contribution
`0.19045029547199122`; its activity and synchronous lane were identical on the
post-evidence and rewired graphs. This checks preservation, not an improvement
in learning. A separate fresh-database experiment completed 100+ external roots
and successfully changed one actual one-sided occurrence without inventing a
reverse occurrence.

An independent subprocess exited immediately before successful END commit;
reopening recovered the OPEN root, unchanged W and pending request. A second
subprocess exited immediately after commit; reopening recovered the complete
replacement and duplicate END did not repeat it or increment the close serial.
Tampered reverse references and old-target records were refused by the graph
decoder. A changed request disposition was refused on cold journal validation.
ABORT before/after-commit subprocess exits were separately tested with a staged
request and exact H_BEGIN restoration.

The next attempted pair was live-linked and was refused with
`RECYCLE_BLOCKED_LIVE_OR_PROTECTED`; its new assignment was only one completed
close old. A different old pair received `NO_RECYCLING_REPLACEMENT` with slots
unchanged. A later root created a live link across that pair during ordinary
END settlement, and the requested recycling was refused by the post-evidence
guard. Fixed and stale-event requests also refused. No valid link was deleted.

The instrumented bilateral command took 144.33338209998328 seconds and peak
traced Python allocation was 7,896,747 bytes; the SQLite file at serial 100 was
3,076,096 bytes. The concurrent local test suite affects timing; `tracemalloc`
does not include subprocess allocations or full process RSS.

## Verification and acceptance gates

Commands use `.venv/Scripts/python.exe` in this Windows workspace:

| Command | Result |
| --- | --- |
| `python -m pytest -q --basetemp=.pytest-tmp -rs` | PASS: 702 passed in 105.97s. |
| `python -m ruff check .` | PASS: All checks passed! |
| `python -m ruff format --check .` | PASS: 93 files already formatted. |
| `python -m mypy` | PASS: no issues in 48 source files. |
| `python -m dgca_next verify-specs` | PASS: both hashes above. |
| `python -m pip check` | PASS: No broken requirements found. |
| `git diff --check` | PASS. |
| `python tests/experiments/i3_p04_real_rewiring.py` | PASS: production trace and subprocess crash experiment above. |

| Gate | Verdict |
| --- | --- |
| G01 | PASS: current root's final external event and prospective completed serial are independently derived at END. |
| G02 | PASS: schema-versioned W, forward/reverse/audit metadata, journal replay and corruption checks. |
| G03 | PASS for actual fixed/live and post-evidence protection. Production-persisted pins, protected slot flags and reservations remain NOT_RUN; fixture-only cases are not production evidence. |
| G04 | PASS: actual bilateral and separate one-sided production replacements, persisted and independently reopened. |
| G05 | PASS: no-candidate, age, fixed, stale, duplicate, read-only, ABORT and subprocess END/ABORT rollback controls. |
| G06 | PASS: cold replay, recovered W/H and records, unchanged post-evidence live links and read-only neural behavior. |
| G07 | NOT_RUN / PENDING: local checks pass; GitHub has kept both Ubuntu and Windows jobs queued without assigning runners. Final-head CI must complete successfully. |
| G08 | PARTIAL: the physical and numerical evidence is recorded; final-head CI results remain pending. |

## Limitations and NOT_RUN

Automatic production recycling remains disabled. Production-persisted
contextual pins, protected slot flags and reservations are not demonstrated;
no I5 owners were fabricated. Schema-3 databases require an explicit future
migration or separate handling. Native Assemblies, contextual owners, Replay,
generation, multimodal behavior and learning/retention-benefit ablations were
NOT_RUN. The controlled experiment does not show that recycling improves
learning or memory. Full I3 remains partial pending separate review.
