# I4-R05 Native Context Attractor verification

Status: **LOCAL_ACCEPTANCE_PENDING**. R06 has not started. This draft records
observations already executed; pending checks below are not PASS claims.

## Authority, isolation and preservation

- Repository: `naoufelbvb2-arch/DGCA-NEXT-V1`.
- Isolated branch: `experiment/i4-r05-r06-autonomous-completion`.
- Exact accepted base: `b4549d2f9c38d665f19a87848ae22b4b950c8fac`.
- Owner authority and master were copied byte-for-byte and committed first in
  `1c8f697b26e651f24a8c80b3e4728d9bda532159`; planning/CI trigger in
  `0d302243f341e77830fe5e0f076dacbedd8a34ea`.
- Runtime implementation: `72d746a36192c167d1845433b4fbb0c5cf34535d`.
- Reporting correction and actual independent trial source:
  `ca4a4cf9a424ec722d15013f11f78963a1963cae`.
- Evidence/test checkpoint: `def707d` (full release history in the changelog).
- CORE SHA256: `3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c`.
- LLA SHA256: `ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0`.

Both scientific papers, configuration and source manifest remain unchanged.
Their design-candidate status is not upgraded to scientific freeze. No protected
branch was merged or edited. No fixture Assembly or manually inserted synapse
authorizes a positive result below.

## Implementation and state boundary

`I4_NATIVE_ATTRACTOR_V1` explicitly selects a fresh Schema5 native database plus
the separate `p05_runtime` table. No old database is migrated. W5 and native
FORM/MAINTAIN/GROW/MERGE/SPLIT encodings retain the accepted representation;
old capabilities retain their original event and END semantics. Old readers
refuse the additional table. R05 refuses an old database without its R journal.

The new typed runtime obtains real LIVE Assembly IDs, generations and members
from an audited RootStore. Physical graph validation checks consolidated
reciprocal LOCAL support, KEEP, membership inverses and immutable native history.
The public read-only bridge accepts RootStore authority, not a caller graph,
`AssemblyFixture`, membership tuple, predicted score or expected target list.
An unknown/archive/stale reference cannot contribute contextual sigma.

Each EVENT freezes W/H, computes the normal two-pass with **prior** native sigma,
and separately computes fresh with zero previous activity, temporal drive, sigma
and bootstrap, using the one ordinary synchronized LOCAL/CROSS pass. Actual
reciprocal weights give the sorted weighted fresh cohesion. Both admission
thresholds must pass in the same event. New strength affects the next event.
Age grows once per event; fresh does not reset error. Boundary precedes age30,
which precedes error>1.5. Collapse does not immediately readmit in the same event.

The observation scope is the existing LLA2.1 enumeration. UNSPECIFIED/PARTIAL
cannot authorize miss. COMPLETE_NEXT_EVENT is recorded at the actual external
ingress. Predictions use frozen prior member emitters in prior F_step and real
ASSOCIATIVE neural Q. Comparable targets must also have current positive direct
SIC support. No absent target is supplied as zero and no evaluator Y enters the
runtime. Error is transient R, not a negative synaptic update.

R2 stores the base EVENT bytes, scope, prior-R hash, pre/post W/H hashes, exact
fresh passes, sigma, physical evaluations and bounded transient state. It is
published in the **same** SQL transaction as sensory births, H, proposals and
event order. Native cold validation recomputes the whole original event timeline,
then the accepted physical/root-close audit verifies the resulting historical W.
Decoding or re-signing an R record alone supplies no authority. BEGIN/END/ABORT
retain R_COLD; ABORT restores exact H_BEGIN while lawful sensory births remain.

Read-only processing preserves persistent W/H/R, evidence and root counts as
well as the caller's immutable runtime. The sigma-zero ablation is read-only.
Native contextual owners/bindings are unavailable, so mu is empty in this
bounded LANGUAGE capability. No owner mechanism or generation is implied.

## Genuine independent production trajectories

The curricula were declared in changelog C02 **before** trials. Namespaces
F01-r2 and F02-r2 are separate empty databases. Numeric root IDs repeated across
databases are not pooled. Their control copies supply no extra confirmations.

| Measurement | F01-r2 | F02-r2 |
|---|---|---|
| External canonical feature | a | ab |
| Initially committed cells / synapses | 0 / 0 | 0 / 0 |
| Original completed roots | 1..7 | 1..13 |
| Physical receivers | 8606,9345,11795,12181 | 8694,10273,10513,11641 |
| Actual FORM | Root4, Assembly0 GEN1 | Root4, Assembly0 GEN1 |
| Actual GROW | Root5, same ID, GEN2 | Root5, same ID, GEN2 |
| Learned links at frozen RO checkpoint | 12 LOCAL +12 ASSOCIATIVE | 12 LOCAL +12 ASSOCIATIVE |
| Fresh mean at support1 | 0.7255200171716478 | 0.7146330465646903 |
| Weighted fresh cohesion | 0.7255200171716477 | 0.7146330465646903 |
| Runtime + cold child check, wall seconds | 106.5771896999795 | 139.90456639998592 |
| Final SQLite bytes | 4526080 | 5160960 |

The receipts contain every actual EVENT, R2 source hashes, fresh raw/normalized/
final activity, pair weights, prior sigma, age/error transition and collapse,
all frozen-checkpoint directed Q/E/S/root counts and complete selected credits
(root/event IDs, source/target digests, q and paired y). They also contain final
W/H bytes, final hashes and the independent cold-child result.

- [F01-r2 receipt](evidence/i4-r05-r06/F01-r2.json).
- [F02-r2 receipt](evidence/i4-r05-r06/F02-r2.json).

F01 root5 W SHA256 is
`240aa43d90731aeadc2b2f862da0f7e6f2093c6f87afa2d6680cec0595bce66b`, H is
`b3eca03ad5c1f9eae079ea82766c0ff64a567780421215354bb9b55603377810`.
The cross-platform tests check these genuine physical fingerprints. Final F01 W
is `539ceb94074c6d1340b630d449a9e7e6fb1af7ac286765e3e6f41a4767bc2414`;
final F02 W is
`2ab9d454609b97d6b6b68db986d83081750e00d6521ee83c5261408486b3ef7a`.

### Admission, continuation and falsification

At the same frozen F01 root5 W/H, external support0.4 gives mean and cohesion
`0.4312481340589534`: mean PASS, cohesion FAIL, **no admission**. Support0.2
gives `0.15648470958604166`: both FAIL. Empty input gives fresh=0 despite an
active prior runtime. The reverse single-threshold negative uses explicitly
numerical component inputs; it was not physically reached by this uniform SIC
curriculum and is not a genuine production claim.

F01 root6 orders0/1 are a1; order2 is empty; orders3..31 are a1; order32 has
HARD_BOUNDARY. Order0 suppresses admission under the root's existing cold boundary.
Order1 admits age0, repeated fresh never resets age, order31 collapses at30,
and order32 clears prior sigma before processing. Read-only controls independently
execute the complete age0..30 horizon on the same frozen learned W/H.

### Actual comparable error

F01 root7 orders0/1 use a1, order2 a0.1, order3 a1, orders4..9 a0.1,
all with explicit COMPLETE_NEXT_EVENT. At order2 each of the four genuinely
direct targets has frozen p=`0.5534450244888269` and actual observed o=`0.1`.
The mean miss is `0.49810052203994426`. Error progresses:

| Root7 order | Error / result |
|---|---|
| 1 | admitted,0 |
| 2 | 0.49810052203994426 |
| 3, fresh a1 | 0.49810052203994426, not reset |
| 4 | 0.9962010440798885 |
| 5 | 1.494301566119833, not collapsed |
| 6 | error collapse, next cumulative value exceeds1.5 |

F02 root13 independently obtains p=`0.9307225726097181`, miss
`0.8376503153487463`, and error collapse at order4. These are actual current
direct SIC observations, not synthetic expected-outcome values. UNSPECIFIED and
PARTIAL controls compute real predictions but never accumulate error.

### Causal ablation and limitation

Both ablations use exactly the same learned W/H and immutable prior R. Fresh is
identical with sigma enabled/disabled. Prior sigma changes pass1 raw-drive L1 by
`1.4374633010699807` in F01 and `0.3992273926074854` in F02. **Final-activity
L1 is0 in both** because the normally stimulated cells clip to1. This shows a
causal drive contribution and zero final-activity benefit in these trials.
It does not demonstrate better learning, semantic understanding or language.

## Recovery, negative controls and current verification

The new suite exercises actual RootStore input/order/type validation, lawful
sensory persistence, native identity/generation, prior sigma, no-input fresh,
age/boundary precedence, genuine comparable error, no-error scopes, read-only
invariance, cold recovery, ABORT, old-reader refusal, R2 corruption and repaired
age/generation/fresh/scope/version/missing-record forgeries. Separate process
exits cover BEFORE/AFTER COMMIT for EVENT, END and ABORT; completed END is
idempotent. Failed historical test/report attempts remain in changelog C04/C05.

| Command / experiment | Actual result so far |
|---|---|
| `python -m pytest -q --basetemp=.pytest-tmp/r05-baseline` | PASS:884 in2183.15s before production edits |
| Targeted legacy P01/R02/fixture-Attractor suite | PASS:57 in63.43s |
| `python -m pytest -q tests/test_i4_r05_native_attractor.py --basetemp=.pytest-tmp/r05-targeted-v3` | PASS:21 in231.37s |
| Same file `-k 'frozen_zero or fingerprints'` | PASS:2,21 deselected in4.78s |
| Empty RO / EVENT / ABORT checkpoint test | PASS:1 in19.35s |
| Full retained regression, `--basetemp=.pytest-tmp/r05-complete` | IN_PROGRESS |
| `python -m ruff check .` | PASS |
| `python -m ruff format --check .` | PASS,147 files at C06 |
| `python -m mypy` | PASS,69 source modules |
| `python -m dgca_next verify-specs` | PASS,both unchanged scientific hashes |
| `python -m pip check` | PASS,no broken requirements |
| `git diff --check` | PASS,engineering working changes |
| Authentic original-R04 identity controls | PASS,F05 SPLIT stale IDs and F06 MERGE stale/archive IDs; original DB hashes unchanged |
| Actual F01 lineage process-exit controls | PASS:6 cases in216.30455380002968s |
| Final delivery-head Ubuntu/Windows CI | NOT_RUN; earlier ca4a4cf run41686737916 is in progress |

The v3 targeted suite preceded four additional tests; the final unique test count
is expected to be909 (884 retained +25 R05). Expected counts are not completed
results. Peak memory and scalability benchmarking: NOT_RUN. Measured wall times
include competing validation processes and are not clean latency benchmarks.

Additional recovery receipts:

- [Actual F01 runtime crash controls](evidence/i4-r05-r06/runtime-crash-controls.json):
  copies of original roots1..5; no independent-root evidence is pooled. An
  AFTER_COMMIT weak external EVENT recovers age1 and exactly one actual miss;
  BEFORE_COMMIT restores every prior W/H/R hash. END is idempotent and ABORT
  restores exact H_BEGIN.
- [Actual root4 to root5 generation control](evidence/i4-r05-r06/grow-generation-control.json):
  a real read-only GEN1 Attractor has strength0.7259368601806818; actual root5
  GEN2 refuses its runtime before influence and refuses old GEN1 lookup.
  Both original snapshot databases retain byte-identical W/H/R.
- New cold sensory ABORT test:PASS in0.85s. Two genuine external events change
  H but do not publish proposals; ABORT restores initial H exactly, retains all
  four lawful sensory births, keeps zero synapses, and cold reopening verifies
  a subsequent independent root with lawful default H materialization.

Original R04 cold-history identity negatives are complete:

- [F05 original SPLIT history](evidence/i4-r05-r06/r04-f05-split-identity-control.json),
  Root59: both actual pre-SPLIT GEN12 references fail against GEN13.
- [F06 original MERGE history](evidence/i4-r05-r06/r04-f06-merge-identity-control.json),
  Root109: old survivor GEN4 fails against GEN5; archived ID1 is refused.
- Full database hashes still match their original accepted R04 receipts:
  F05 `c4febc61a86b233bd4d0115a9da660e31c3bd4f3c1b5b8a00ab204ac04e23323`;
  F06 `c3f0985cb046d38ef5264cafea33c990c26ae1548e292092938fae2dd584adf0`.
  These controls do not execute an operator or claim historical R04 Attractors.
- Additional genuine RootStore END/GROW boundary test:PASS in9.12s. An OPEN
  root actually admits GEN1, END lawfully grows the same ID to GEN2 and clears
  R; cold replay authenticates the original GEN1 event rather than backdating
  the four-member post-END structure. The next independent root begins cold.

## R05 local acceptance gates

| Gate | Current disposition | Evidence classification |
|---|---|---|
| G01 native eligibility and persistence | PRODUCTION_PASS | Genuine F01/F02 authority; authenticated original-R04 archive/stale negatives |
| G02 fresh and dual admission | PRODUCTION_PASS | Actual frozen external scratch; reverse-only threshold control NUMERIC_ONLY |
| G03 next-event sigma,age,boundary | PRODUCTION_PASS | Actual root6 and immutable read-only horizon |
| G04 externally comparable error | PRODUCTION_PASS | Actual F01 root7/F02 root13; unqualified outcomes refused |
| G05 independent traces/non-retroactivity | PRODUCTION_PASS | Two empty-to-learned lineages; original pre-event W/GEN |
| G06 W/evidence/RO invariance,H separation | PRODUCTION_PASS | Unchanged persistent state; lawful LEARN H and ABORT |
| G07 cold history/failure atomicity | PRODUCTION_PASS | Actual F01 lineage controls,6 process exits; new cold sensory ABORT passed |
| G08 retained regressions/static/integrity | PENDING full regression |884 baseline PASS; current full run in progress |

Aggregate: **PENDING**. R06 is prohibited until all required local gates pass.
This document does not authorize a merge, scientific freeze or L5.
