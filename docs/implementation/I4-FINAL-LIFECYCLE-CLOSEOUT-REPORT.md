# I4 final lifecycle closeout

Status: **VERIFICATION_IN_PROGRESS**. This working report does not authorize
acceptance, a merge, scientific freeze or L5.

## Authority and baseline

Repository `naoufelbvb2-arch/DGCA-NEXT-V1`; isolated existing branch
`experiment/i4-final-lifecycle-closeout`; authorized contract commit
`11d6e12c8dd41aa070b7c027d3d62aa30554b4cb`, parent
`49647dd8bcf24bd7ea7befa70c3aaf4dd9d550b8`. Both supplied authority documents
and the accepted independent review remain unchanged. Production source and
all accepted tests were initially identical to accepted R05/R06 delivery
`32305ca0e2951d10d9c6f3258a9156715794a1fb`.

The sole scientific sources remain unchanged RC4.4:

| Source | SHA-256 |
|---|---|
| CORE | `3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c` |
| LLA | `ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0` |

No production graph/dynamics/evidence/capability/codec law has been changed.
Automatic recycling remains disabled. These investigations use the accepted
`I4_NATIVE_OPERATORS_V1` capability and actual RootStore external operations;
accepted native Attractor functionality and every earlier capability remain
unchanged. No contextual owner, readout, generation or L5 is implemented.

## Gate A — genuine terminal MAINTAIN

[A01-r1 trajectory](evidence/i4-final-closeout/A01-r1.json), declared in C01
before execution, continues the byte-verified actual R04 SPLIT database. It
does not pool its copies as additional independent external confirmations.
Original source file SHA256:
`c4febc61a86b233bd4d0115a9da660e31c3bd4f3c1b5b8a00ab204ac04e23323`.
Full original history is rederived by RootStore before accepting new input.

Four original R04 feature names, support1, were predeclared with a 40-root /
112-event ceiling. Actual run stops after ten new roots60–69 and22 new events.
Roots60–63 admit twelve sensory cells; none receive same-event learning credit.
Roots64–69 use three repeated external events each for `r04-merge-820`, with
one root-maximum confirmation per legal directed link. There is no SIC search,
direct graph insertion, manually weakened/deleted synapse or synthetic witness.

Original Assembly0/1 members are8200,10035,10926, GEN13, first birth close4,
previous genuine SPLIT close59/prefix161. Reciprocal LOCAL support between
their members remains .4. New physical reciprocal neighbors8296,9158,10970
reach support .6 from six completed roots64–69 (actual q=y=1 per direction
per accepted root), increasing cell8200's whole-region denominator.

| Actual END | Cell8200 degree / density | Numerator / denominator | Specificity | Published result |
|---|---|---|---|---|
| Root68 | 2 / 1 | .8 / 3.9 | .20512820512820512 | KEEP |
| Root69 | 2 / 1 | .8 / 4.2 | .19047619047619047 | lowest failing member removed; terminal ARCHIVE |

Root69/global EVENT182/order2, completed event prefix183, publishes both IDs
as ARCHIVED, members10035,10926, generation14. Births and last SPLIT reference
remain unchanged. All live cell/inverse memberships for0/1 are removed.
Cell8200 remains lawfully in Assembly4, born66/grown67. This is MAINTAIN
terminal3→2 archival, not a MERGE archive or deletion of learned knowledge.
No fabricated replacement FORM identity is used to claim success.

| Root69 boundary | SHA-256 |
|---|---|
| pre-END W | `5aa8342b5f36bfb0f064ba15851f716d5118a481256de1e10f8932a8d1bf0d73` |
| post-END W | `7a22ee6ae80626ff93a3ebc039f05e9dc1cde07bd4056d9a928e4669ff16857c` |
| H, identical across END | `c88e774afb0fd3e0ba7b9abe066e5075851d9bb81f4633e55dfef34e88212ac2` |
| post-END R_COLD | `235c092696221c8aa82d3d19a597d211a54bffa07d15f74bdc3e1ca1f9396ddb` |

Canonical cold recovery and six genuine same-lineage transaction/falsification
controls are pending. Gate A is **ACTUAL_PUBLICATION_OBSERVED / SAFETY_PENDING**,
not yet complete PRODUCTION_PASS. Controls were declared before execution.

## Gate B — second post-cooldown operator

NOT_RUN: waiting for Gate A safety completion, preserving the contract's
sequential A-then-B execution order. Age200 alone will not count as success.
An otherwise physically eligible age199 refusal and an actual second published
same-ID MERGE/SPLIT at200 are both mandatory.

## Verification so far

| Exact command | Actual result |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q --durations=10 --basetemp=.pytest-tmp/closeout-baseline` | PASS:909 in703.02s, zero FAIL/SKIPPED; before new test collection |
| `.venv/Scripts/python.exe -m ruff check .` | PASS |
| `.venv/Scripts/python.exe -m ruff format --check .` | PASS,153 current files |
| `.venv/Scripts/python.exe -m mypy` | PASS,69 source files |
| `.venv/Scripts/python.exe -m dgca_next verify-specs` | PASS, both exact hashes above |
| `.venv/Scripts/python.exe -m pip check` | PASS, no broken requirements |
| `git diff --exit-code 32305ca0e2951d10d9c6f3258a9156715794a1fb -- src docs/specs` | PASS, accepted production/science unchanged |

Intermediate CI run42421100407 is not the eventual delivery receipt. Required
final full suite and exact delivery-HEAD Ubuntu/Windows success remain pending.
Full run commands, new-test results, control timings/storage, changed-file and
commit inventory and final gate verdicts will be completed after execution.

The [append-only log](I4-FINAL-LIFECYCLE-CLOSEOUT-CHANGELOG.md) retains all
declarations and repairs. [Evidence reproduction](evidence/i4-final-closeout/README.md)
distinguishes genuine RootStore trajectories, continuation copies, saved-state
component checks and unexecuted cases. Earlier wider scientific limitations
are not upgraded by these two lifecycle experiments.
