# R05/R06 evidence boundaries and reproduction

`F01-r2.json` and `F02-r2.json` record two independent empty-to-learned
RootStore experiments at `ca4a4cf9a424ec722d15013f11f78963a1963cae`.
Runtime source is unchanged since72d746a. F01-r1/F02-r1 reached their completed
roots but failed a tuple/list reporting assertion; no success receipt is claimed
for those reporting attempts. The original ignored databases/logs are retained.

From the repository root with Python3.14 and the editable dev environment:

```powershell
python tests/experiments/i4_r05_native_attractor_trace.py --family F01 --out .pytest-tmp/reproduce-F01
python tests/experiments/i4_r05_native_attractor_trace.py --family F02 --out .pytest-tmp/reproduce-F02
```

The output directories must not exist. The driver records the actual executing
Git HEAD as the database's declared code revision, submits canonical features
through the production API and saves actual checkpoints. It never uses
FixtureBuilder or inserts connections. Re-execution at another commit changes
revision attribution; do not falsely relabel it as an original root. A separate
child process opens and audits the final database before comparing final state.

Rows under `events` are decoded canonical R2 records. Binary `event` fields are
encoded as `{"base64": "..."}` for JSON storage. W/H final bytes are also base64.
JSON numbers round-trip binary64 in Python; the authoritative internal R2 codec
uses tagged finite binary64. Re-encoding or decoding a receipt is a component
check, not RootStore historical authority or external learning evidence.

`learned_links` describes each frozen read-only checkpoint, not an instruction
to manufacture links. It includes actual source/target physical IDs, scope,
Q, E_ext/E_int,S, counts and selected original credits with q/y and root/event
witnesses. `events` contains the original root/order, base EVENT bytes, W/H/R
hashes, direct SIC, normal/fresh passes and native transitions. `readonly`
contains matched ablations and the full age horizon, without evidence updates.

The original SQLite databases remain ignored under `.pytest-tmp`. Multi-GB
databases are not committed. Positive receipts and scripts provide bounded
inputs for independent re-execution. Do not count control copies as additional
independent external confirmations or pool roots across network namespaces.

The generation, original-R04 identity and crash receipts, when present, are
negative/recovery controls only. R04's actual operator curricula are documented
in the immutable R04 report and its existing experiment drivers. No new R04
operator is performed by the R05 identity checker. A bare published W snapshot
alone does not authenticate original RootStore history.

Final acceptance remains subject to the R05 local gate and exact delivered-head
Ubuntu/Windows CI; no data file changes the authority of CORE/LLA RC4.4.

Actual-lineage controls (source revision is the original database attribution):

```powershell
python tests/experiments/i4_r05_runtime_crash_controls.py .pytest-tmp/reproduce-F01/root-5.sqlite ORIGINAL_REVISION .pytest-tmp/reproduce-crashes
python tests/experiments/i4_r05_generation_control.py .pytest-tmp/reproduce-F01/root-4.sqlite .pytest-tmp/reproduce-F01/root-5.sqlite ORIGINAL_REVISION .pytest-tmp/reproduce-generation.json
```

Use the new trial receipt's actual `revision`, not the literal placeholder.
The six crash cases reuse copies of one original lineage. Every case submits
real RootStore events and recovers in a separate process; no copy earns an
additional independent experimental confirmation. The generation control
reprocesses actual frozen snapshots read-only; it does not backdate learning.

F03-r3 is the final integrated R06 receipt at
724c915a95facee825862428683b582569e47a74. Reproduce only after the local
R05 gate exists and passes:

```powershell
python tests/experiments/i4_r06_consolidated_trace.py .pytest-tmp/reproduce-F03 --trial-id F03-r3
python tests/experiments/i4_r06_scientific_coverage.py
```

The first two F03 reporting attempts are retained locally and disclosed in
C10/C11. No earlier result is pooled into the final F03-r3 root confirmations.
The scientific coverage audit includes every normative Given/Required row;
component and unexecuted scenarios remain explicit. CI-CODE-CHECKPOINT.json
refers to03cc31a, not the final delivery commit. Its own Actions receipt must
be verified and linked in the final handoff before REVIEW_READY.
