# I3 final consolidated verification

Scope: **LANGUAGE first-lab engineering closure**, not a scientific freeze or
claim of language acquisition. Branch `feature/i3-local-learning`; accepted P04
implementation `ab7021f7e41f5531edc7bdfd46ad84b47dee7f5c`, final contract
`15afb76fe7013179f09410e7d353af77e7d3d250`, integrated-test commit
`8c808c58070757b118a8e4c8a547ce2ccbe1a56a`. The report commit is the delivery
head. Changed files are this report, `tests/experiments/i3_final_integration.py`,
`tests/experiments/test_i3_final_integration.py`, and
`tests/test_i3_final_compatibility.py`; no runtime or scientific source changed.

The P01, P02, P03 and P04 contracts, verification reports and available
independent acceptance reviews were examined. P02's review records P01's
accepted scope; no separate P01 review document was present in this checkout.
Referenced heads are P01 implementation `991d206382352ba0a907c5ca06c9d515b586fcdf`,
P02 audited delivery `80ae771283bb9397660b740338e169bf6cbe8c32`, P03 audited
delivery `bc2e195946b98a14fc138498761f0e435ea33375`, and P04 audited delivery
`ab7021f7e41f5531edc7bdfd46ad84b47dee7f5c`.
The [P04 independent review](I3-P04-INDEPENDENT-ACCEPTANCE-REVIEW.md) supersedes
the earlier P04 pending CI report: run 41101983231 succeeded on both platforms
at the exact accepted P04 SHA. P01–P04 remain accepted only within their named
engineering scopes.

Normative source hashes are CORE RC4.4
`3829494e85b85c1421379324a1702013bed3c970e353ad3b71c08da1901eb93c`
and LLA RC4.4
`ba38b7916add57090f088460adb0baa351111cc1757c4a062c89a9d35ca6f2e0`.
The fixed lab configuration manifest SHA-256 is
`088363eb89484c9605fa52e7c06743e5a1867be22bf3d87692492221fd317e27`;
`src/dgca_next/config.py` SHA-256 is
`acb89d657a1c0578686120995ad9abb584de19e55a7fb20cf736e65e3f89ce1c`.
Both scientific documents remain design candidates, not frozen or empirically
verified. The isolated database's declared revision is `a` repeated 40 times,
not a claim that it is a Git commit or an authenticated external identity.

## Single production evidence chain

`python tests/experiments/i3_final_integration.py` started with zero committed
cells and zero synapses in a new schema-4 database. Only the public production
RootStore API mutated W; no fixture graph, inserted synapse, fabricated q,
expected answer or synthetic root was used. Root 1 event 0 projected `a=1`,
committed physical IDs 8606, 9345, 11795, 12181, deferred none, and produced
no same-event proposals. All four have 24 typed slots; pre-event population was
zero; the RC4.4 virtual profile has gain 1.0, cell firing EMA 0.05,
LANGUAGE regional EMA 0.030 and LANGUAGE threshold 0.2. P01 separately tests
the 16-receiver/12-admission oversubscription case.

Roots 2–4 supplied genuine repeated `a` events, staged LOCAL and one-step
ASSOCIATIVE proposals, and published one maximum q with its paired y per key
and completed root. At root 4 the physical `8606→9345 LOCAL` link had
`q=1.0`, `y=1.0`, `E_ext=3.0`, `S=1.0`, `Q=0.3`, three independent roots
`[2,3,4]`, and was `CONSOLIDATED`. Its sampled source and target event were
both global event 7. The corresponding `8606→9345 ASSOCIATIVE` link was
`CANDIDATE`, with `q=0.5380584331830818`, `y=1.0`,
`E_ext=1.6154612164973288`, `S=1.0`, `Q=0.16154612164973287`, and the same
three independent roots; its sampled source/target events were 6/7. Root 4's
source emitter and F_step sets were `[8606,9345,11795,12181]`. The test checks
full-precision root-MAX and paired y, event-time activity and actual D guards.

After cold reopen, a frozen two-event read-only `a` episode used the same
physical population and H for learned W and the saved link-free W. For each of
the four receivers, trained synchronous input was `0.5211568710341401` and
trained one-step temporal input was `0.3120138817213053`; the matching
link-free lanes were empty. Store W/H/R and evidence did not change. Root 3
event 4 had direct `X_fixed=1000000`, true frozen pre-SIC
`P_T=0.11297496516614403`, novelty `0.887025034833856` (Q6 `887025`); a later
prediction-only event had no direct novelty authority, and the next root's cold
first event had P_T=0.

Root 5 staged genuine qualified proposals, then observed `ab=1`, committing
new receivers `[8694,10273,10513,11641]`. ABORT restored byte-exact H_BEGIN,
left learned links and completed-close serial 4 unchanged, and retained the
lawful newborn topology. Aborted novelty was rejected.
H_BEGIN and H_ABORT each had SHA-256
`b3eca03ad5c1f9eae079ea82766c0ff64a567780421215354bb9b55603377810`;
W changed from `1d7e7d50d4bcc8a919c0fc9d4284c1e6a22ed475e7ef53151e572d724f6f0144`
to `a51d2c2cc5779c38c07f9682c38a421a8b7160beae9f520761c58b7914254c40`
because the permitted sensory births remained. Roots 6–104 were actual
completed external roots, not injected counts. At root 104 serial 103, the
newborn pair's age was 99 and the requested replacement was refused. Root 105
global event 109 used the distinct genuine bundle `ab=0.2, ac=1`; endpoint
8694 had X_fixed 200000, frozen P_T 0, and novelty Q6 1000000. At the
prospective and committed serial 104, age 100, post-evidence guards permitted:

| Physical slot | Old target | New target | New assignment serial |
| --- | ---: | ---: | ---: |
| 8694 slot 2 | 10273 | 8783 | 104 |
| 10273 slot 1 | 8694 | 8783 | 104 |

Both forward and reverse references were checked, the saved production
recycling record refers to root 105/event 109, and new assignment ages reset.
W before/after SHA-256 was
`3f189e2a6edd45ccda9a82cb7894e64d5988a70b73686bc627c5de0bda811996` /
`d5611513ecd1f3d739dd7ea31f4aadcba64a3131ae532a3c41c979d39914348d`;
post-END H SHA-256 was
`14f6926324c94f12c97b95385b711459881f0dd81fb4bd027759bd63ff92d543`.
The closed-root R is `520100000000` (SHA-256
`235c092696221c8aa82d3d19a597d211a54bffa07d15f74bdc3e1ca1f9396ddb`).
The original LOCAL and ASSOCIATIVE records were bit-identical across this END;
their read-only activity on the original receivers also matched before/after.
Cold reload reproduced W/H and the recycling record. Actual subprocess exits
before and after this END recovered respectively the complete OPEN state and
the complete committed state; duplicate END added no second close. The recovered
root high-watermark was 105 and completed-close serial 104. P04's separate
genuine-root test executes one-sided replacement, and existing P01
and P04 subprocess tests cover EVENT and ABORT before/after-commit exits.
Tampered witness/checkpoint, graph reverse/old-target and close-disposition
tests reject corruption; no synthetic graph is presented as evidence here.

## Falsification and operational limits

| Check | Disposition |
| --- | --- |
| F01 | PASS: existing canonical SIC, collision, permutation and admission tests; root 1 physical IDs above. |
| F02 | PASS for mechanical physical eligibility across `a`, `ab`, `ac`; no semantic discrimination or expected Y was supplied. |
| F03 | PASS for witnessed LOCAL/ASSOC production q/y, paired root max, prior F_step and no newborn evidence; stale D_close and capacity refusals also have isolated operator tests. |
| F04 | PASS: the actual LOCAL link meets all three consolidation predicates; read-only leaves W/H/evidence unchanged; negative learning is disabled. |
| F05 | PASS: ABORT, completed-root serial, H_BEGIN and idempotent END; resumed order and subprocess controls in P01/P02/P04 tests. |
| F06 | PASS: P04 real same-END/live-pair protection and 100-root guard. In the integrated database, root 105 completed at event clock 108; the genuine `8606→9345 ASSOCIATIVE` candidate remained live with deadline 103, E_ext 1.6154612164973288 and three credits, despite expiry. No automatic deletion occurred. |
| F07 | PASS: actual bilateral and separate one-sided changes, reverse/wiring/recycle audit and new age. |
| F08 | PASS within scope: no native Assembly/owner/generation/Replay or auto recycling implemented. `GraphSnapshot.capture` can inspect learned post-I3 W; persistent native Assembly state and its compatibility require a separately reviewed I4 implementation. |
| F09 | PASS: schema-3 journal is explicitly rejected without modification; existing schema-3 user data cannot be opened by schema 4 until separately approved migration or compatibility support exists. |
| F10 | PASS as bounded measurements below; not a scale or performance guarantee. |
| F11 | Local source/config and checks PASS; final-head CI result must be verified against the report commit. |

With Python tracing enabled, diagnostic measurements on the same run were:

| Completed closes | Event snapshots | W bytes | SQLite logical/file/allocated bytes | Last root append | Cold reopen and audit |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 6,014 | 40,960 / 40,960 / 40,960 | 0.239 s | 0.138 s |
| 10 | 16 | 33,487 | 1,536,000 / 1,536,000 / 1,536,000 | 0.675 s | 4.958 s |
| 100 | 106 | 33,487 | 14,114,816 / 14,114,816 / 14,114,816 | 0.611 s | 47.060 s |

The measured parent-process peak was 19,267,458 bytes tracemalloc and
59,289,600 bytes peak RSS; child processes are excluded. Elapsed time through
the final committed state was 459.901 s with tracing and concurrent tests;
that figure excludes the final independent cold reopen. Appends persist
pre/post W snapshots per event; storage grows with event count and snapshot
size, and cold validation replays history. These limited measurements do not
establish an asymptotic benchmark or a new threshold.

## Milestone and gate disposition

P01 EVENT, P02 synaptic evidence, P03 novelty/guard and P04 controlled
rewiring are **PASS within their independent-review scopes**. Production pins,
slot-protection flags and reservations have no end-to-end persisted proof;
automatic recycling, native owners and Replay remain NOT_RUN.

| Original I3 gate | Disposition |
| --- | --- |
| G01 | PASS: genuine ordered external roots, cold resets, committed-before-event witnesses. |
| G02 | PASS: physical birth and topology; oversubscription in P01 tests. |
| G03 | PASS within LOCAL/ASSOCIATIVE first-lab scope: witnessed proposals, event/close D and budgets. |
| G04 | PASS: production q/y, root deduplication, evidence and actual LOCAL consolidation. |
| G05 | PASS: atomic lifecycle and crash/retry, H rollback and persisted chain. |
| G06 | PASS: event-bound novelty and controlled P04 guard; automatic recycling remains OFF. |
| G07 | PASS: cold genuine LOCAL and ASSOCIATIVE learning, independent reinforcement, persistence and causal read-only response. |
| G08 | Local checks and final-head CI must pass; no claim that all scientific scenarios passed. |

## Named scientific test accounting

The following table transcribes each scenario's *given* from the actual
[LLA RC4.4 §8.1/§8.3](../specs/DGCA_LLA_RC4_4.md) tables. `FULL` means the full
scenario was executed on a production RootStore path; `COMPONENT` means only
an identified isolated or partial behavior was verified. `NOT_RUN` includes
scenarios beyond I3; it is not a claim of failure or of scientific success.

| ID / source line | Normative given | Classification and evidence |
| --- | --- | --- |
| [LLA-T01](../specs/DGCA_LLA_RC4_4.md#L420) | First observed A on uncommitted receivers | FULL_SCENARIO_EXECUTED_PASS - First real sensory event and no newborn q in the consolidated production chain |
| [LLA-T02](../specs/DGCA_LLA_RC4_4.md#L421) | A/B direct witnesses with no C/E comparator | COMPONENT_OPERATOR_PASS - Direct proposals verified; contrast comparator not implemented |
| [LLA-T03](../specs/DGCA_LLA_RC4_4.md#L422) | Different observed C/E with identical neural SIC footprint | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T04](../specs/DGCA_LLA_RC4_4.md#L423) | Prediction-only E alongside externally observed C | COMPONENT_OPERATOR_PASS - Prediction-only witness refusal verified; full competing-output scenario not run |
| [LLA-T05](../specs/DGCA_LLA_RC4_4.md#L424) | Two q proposals `.20,.50` same link/root | COMPONENT_OPERATOR_PASS - Exact q=.20/.50 and paired y tested with synthetic arithmetic; real root reduction separately verified |
| [LLA-T06](../specs/DGCA_LLA_RC4_4.md#L425) | Provisional link lost D_close by latent recycling | COMPONENT_OPERATOR_PASS - Stale D_close refusal tested in an isolated shadow |
| [LLA-T07](../specs/DGCA_LLA_RC4_4.md#L426) | Contextual pinned latent slot under recycling | COMPONENT_OPERATOR_PASS - Pinned-slot guard tested with fixture, not persisted production pin |
| [LLA-T08](../specs/DGCA_LLA_RC4_4.md#L427) | Candidate only one selected P→z consolidated | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T09](../specs/DGCA_LLA_RC4_4.md#L428) | Both P, ≥1 selected C, ≥1 selected Y consolidated; PRE/POST scratch identical | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T10](../specs/DGCA_LLA_RC4_4.md#L429) | Candidate no-probe NORMAL passes but CONSOLIDATED-only fails | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T11](../specs/DGCA_LLA_RC4_4.md#L430) | Contrast ledger expires; repeated same physical observed branch with new roots | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T12](../specs/DGCA_LLA_RC4_4.md#L431) | Two distinct branch owners support same new branch | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T13](../specs/DGCA_LLA_RC4_4.md#L432) | BEGIN new root with residual previous Attractor and A_hist | COMPONENT_OPERATOR_PASS - Cold R/frontier isolation verified; native Attractor lifecycle not implemented |
| [LLA-T14](../specs/DGCA_LLA_RC4_4.md#L433) | Root aborted after staged evidence | FULL_SCENARIO_EXECUTED_PASS - Qualified staged root aborted; H_BEGIN exact and lawful births retained |
| [LLA-T15](../specs/DGCA_LLA_RC4_4.md#L434) | Crash/retry at END | COMPONENT_OPERATOR_PASS - Atomic END crash verified; OwnerIDs and production reservations absent |
| [LLA-T16](../specs/DGCA_LLA_RC4_4.md#L435) | READ_ONLY P/B, no root open | COMPONENT_OPERATOR_PASS - Read-only no-credit verified; context runtime scenario not executed |
| [LLA-T17](../specs/DGCA_LLA_RC4_4.md#L436) | Negative target miss in first lab | COMPONENT_OPERATOR_PASS - No negative production update; expected-outcome comparator not implemented |
| [LLA-T18](../specs/DGCA_LLA_RC4_4.md#L437) | Replay same external experience multiple times | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T19](../specs/DGCA_LLA_RC4_4.md#L438) | A=.8, Q=.3 ASSOC prior F_step, A_target=.6 real external | COMPONENT_OPERATOR_PASS - q and temporal-drive arithmetic verified in component tests |
| [LLA-T20](../specs/DGCA_LLA_RC4_4.md#L439) | Replay comparator enabled for same source/target | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T21](../specs/DGCA_LLA_RC4_4.md#L440) | Same-event source Pass1=.40, final=.80, target final=.50 | COMPONENT_OPERATOR_PASS - Final-source/Pass-1 gate arithmetic and production proposals verified separately |
| [LLA-T22](../specs/DGCA_LLA_RC4_4.md#L441) | New candidate WIRED, first qualifying root emits but no Y | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T23](../specs/DGCA_LLA_RC4_4.md#L442) | Candidate reaches age=239; a completed last root brings age=240 | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T24](../specs/DGCA_LLA_RC4_4.md#L443) | OPEN root modifies g/threshold then ABORT | FULL_SCENARIO_EXECUTED_PASS - Production H_BEGIN restoration and subprocess crash/retry tests |
| [LLA-T25](../specs/DGCA_LLA_RC4_4.md#L444) | strong C→z without P; cold B-only | COMPONENT_OPERATOR_PASS - Context gate operator covered with fixtures; native owner scenario absent |
| [LLA-T26](../specs/DGCA_LLA_RC4_4.md#L445) | exact owned P/B and consolidated P/C/Y, probe off | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T27](../specs/DGCA_LLA_RC4_4.md#L446) | completed unique z for DB; generic B→C remains strong | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T28](../specs/DGCA_LLA_RC4_4.md#L447) | B alone, same W/H, no owner match | COMPONENT_OPERATOR_PASS - Masking operator covered with fixtures; complete owned scenario absent |
| [LLA-T29](../specs/DGCA_LLA_RC4_4.md#L448) | two matching different owners same current anchor | COMPONENT_OPERATOR_PASS - Ambiguity handling covered in fixture dynamics; no production owner registry |
| [LLA-T30](../specs/DGCA_LLA_RC4_4.md#L449) | A_src=A_tgt=.50 on LOCAL/ASSOC proposal | COMPONENT_OPERATOR_PASS - Exact arithmetic and 17-root illustration are synthetic |
| [LLA-T31](../specs/DGCA_LLA_RC4_4.md#L450) | first 8 roots yield valid z→Y; next 17 valid consolidation roots | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T32](../specs/DGCA_LLA_RC4_4.md#L451) | top-eight P candidates saturated at 64 but next candidates have headroom | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T33](../specs/DGCA_LLA_RC4_4.md#L452) | z candidate own microcolumn/radius1 full but radius2 has feasible slot | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T34](../specs/DGCA_LLA_RC4_4.md#L453) | feature receiver has 64 live outgoing and appears in P/C | COMPONENT_OPERATOR_PASS - 64/65 source budget component covered; no production context candidate |
| [LLA-T35](../specs/DGCA_LLA_RC4_4.md#L454) | preflight owner shadow before COMPLETE and after retirement | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T36](../specs/DGCA_LLA_RC4_4.md#L455) | selected P pair has `L_owned=.80`, `U_rival=.20`, `m_P=.05`, rival supports both positive | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T37](../specs/DGCA_LLA_RC4_4.md#L456) | admitted P pair exact boundary `L=250000`, `U=200000` (Q6), m_P=50000 | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T38](../specs/DGCA_LLA_RC4_4.md#L457) | `NO_PROBE_TEST` fails initially with E=3, insufficient drive; next independent owned OPEN LEARN P/B/Y | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T39](../specs/DGCA_LLA_RC4_4.md#L458) | failing NO_PROBE_TEST followed only by read-only/replay/missing Y | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T40](../specs/DGCA_LLA_RC4_4.md#L459) | save/load or PRE/POST without RC3.1 threshold triple, or legacy StableBindingV1 record | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LLA-T41](../specs/DGCA_LLA_RC4_4.md#L460) | rival P supports positive but below stored `tau_ctx_q6`, repeated while owner in LEARN | NOT_RUN / OUT_OF_I3_SCOPE - full scientific scenario not executed |
| [LG-T01](../specs/DGCA_LLA_RC4_4.md#L482) | two committed source cells have reciprocal LOCAL CONSOLIDATED edges to third, all triangle pairs R≥.10, fresh witnessed emission | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T02](../specs/DGCA_LLA_RC4_4.md#L483) | only one direction of each triangle link has consolidated, or candidate links are not consolidated | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T03](../specs/DGCA_LLA_RC4_4.md#L484) | mutate Assembly membership, merge/split or restart twice | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T04](../specs/DGCA_LLA_RC4_4.md#L485) | z1 completed and emitted without probe on true external P/B; z2 chooses z1 as P and then sees external Y | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T05](../specs/DGCA_LLA_RC4_4.md#L486) | z1 emitted only from LEARN probe, or from a predicted-only/replay/internal-generated event | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T06](../specs/DGCA_LLA_RC4_4.md#L487) | depth 8 child tries to spawn ninth-level context; stale parent ID/generation or cycle | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T07](../specs/DGCA_LLA_RC4_4.md#L488) | selected best Assembly G outputs SIC receiver j whose prior P_Tj>0 | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T08](../specs/DGCA_LLA_RC4_4.md#L489) | two same-surface/different-bundle events or two surfaces attach to same Assembly | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T09](../specs/DGCA_LLA_RC4_4.md#L490) | after independent text root confirms G only once or G formed same END | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T10](../specs/DGCA_LLA_RC4_4.md#L491) | GENERATE with 5 uniquely decodable legal Assembly steps then EOS | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T11](../specs/DGCA_LLA_RC4_4.md#L492) | generated trace enters repeated winner/frontier pair twice consecutively or exceeds 32 accepted steps | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T12](../specs/DGCA_LLA_RC4_4.md#L493) | winner G not readout-attested but runner-up is printable | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T13](../specs/DGCA_LLA_RC4_4.md#L494) | context source z1 activations are direct-only/but wrong prior event order, or synthetic matched source during LEARN | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T14](../specs/DGCA_LLA_RC4_4.md#L495) | training unseen combination held out entirely | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |
| [LG-T15](../specs/DGCA_LLA_RC4_4.md#L496) | Depth-1 z1 uniquely matches W1/W2, so `μ_p1=1` for direct W2 source p1; a legal depth-2 contextual z2 with `(z1,p1)` as prior P has a live incoming p1→z2 ASSOCIATIVE key; concurrently generic p1→Y exists | COMPONENT_OPERATOR_PASS - directed temporal masking covered by fixture dynamics; hierarchical generation not run |
| [LG-T16](../specs/DGCA_LLA_RC4_4.md#L497) | Cold word starts with uncommitted SIC receivers; directed LOCAL triangle E per edge accrues q=.2025, .36, .49, or .64 independently per complete root; track FORM then the next distinct roots | NOT_RUN / OUT_OF_I3_SCOPE - full Assembly, owner, readout or generation scenario not executed |

The essential I3-local scenarios not marked FULL remain explicit qualifications:
T02 contrast comparison, T03 collision contrast, T04 competing predicted and
observed outcomes, T05's exact synthetic numbers, T06's stale D_close physical
transition, T07's persisted candidate pin, T13 native Attractor state, T15
owner/reservation crash state, T16 contextual retrieval, T17 expected-target
miss, and the exact numerical scenarios T19/T21/T30 have not been executed as
their complete production scientific scenarios. Relevant physical and numeric
subcomponents pass as identified; they do not establish the whole scenarios.
The P02 isolated stale transition and P03 fixture pin tests cannot be promoted
into production scenario evidence. None is represented as scientific PASS.
For T06, a physical D_close loss during one OPEN root is not currently
reachable through the exclusive production API: P04 rechecks and settles
ordinary evidence before its one END-time rewiring. The isolated refusal is
therefore a qualification for future mutation paths, not a claim that this
production transition was executed. T02/T03's contrast and ownership behavior
is deferred outside the bounded I3 production learning path.
Component evidence is in `tests/test_i3_r03_r04_evidence_arithmetic.py`
(T05, T19, T21, T30), `tests/test_i3_p02_proposals.py` (T06),
`tests/test_latent_recycling.py` (T07), `tests/test_graph_budgets.py` (T34),
and the I2 `tests/test_dynamics_context.py` / routing tests for contextual
operators. Production lifecycle subsets are covered by
`tests/test_i3_p01_production_event.py`, `tests/test_i3_p02_learning.py`,
`tests/test_i3_p03_novelty.py` and `tests/test_i3_p04_requests.py`.

### Previously reviewed milestone gates

P01 and P03 reports used pending final-head CI language when written. Their
subsequent independent acceptance and the P04 review's verified final-head CI
supersede those historical pending labels only for the reviewed milestone SHAs;
they do not substitute for the present report head's CI.

| Gate | Current scoped disposition |
| --- | --- |
| P01-G01 | PASS - genuine EVENT and ordered external journal. |
| P01-G02 | PASS - sensory cohort, oversubscription and indexed topology. |
| P01-G03 | PASS - frozen neural EVENT state and frontiers. |
| P01-G04 | PASS - default H and ABORT restoration. |
| P01-G05 | PASS - EVENT checkpoint and cold OPEN recovery. |
| P01-G06 | PASS - scoped production process-crash and invalid-input controls. |
| P01-G07 | PASS for the independently accepted milestone; current delivery CI is separately required. |
| P01-G08 | PASS - scoped physical report; no newborn learning claim. |
| P02 checkpoint A / T01-T02 | PASS - production W, index and credit authority. |
| P02 checkpoint B / T03-T04, T08-T09 | PASS - real direct observations, sampled emitters and prior F_step. |
| P02 checkpoint C / T05-T07, T10-T13 | PASS - evidence settlement and atomic END; stale pair tested in isolated shadow. |
| P02 checkpoint D / T14-T17 | PASS - real LOCAL/ASSOC learning, independent roots and persistence. |
| P02 T18/T20 | PASS within approved restrictions; contextual and generative scenarios NOT_RUN. |
| P02 T19 | PASS for the independently accepted milestone; current delivery CI is separate. |
| P03-G01 | PASS - genuine event-bound direct support and temporal novelty. |
| P03-G02 | PASS - provisional/completed/aborted separation. |
| P03-G03 | PASS - actual 99/100 completed-close boundary. |
| P03-G04 | PARTIAL - fixed/live production guards pass; persisted pins, slot protection and reservations NOT_RUN. |
| P03-G05 | PASS - actual ranked feasibility, no mutation in inspection. |
| P03-G06 | PASS - read-only equality, restart and corruption refusal. |
| P03-G07 | PASS for accepted P03 SHA; current delivery CI is separate. |
| P03-G08 | PASS for scoped forensic report and explicit limits. |
| P04-G01 | PASS - genuine final-event/root/serial trigger. |
| P04-G02 | PASS - versioned production W and root replay audit. |
| P04-G03 | PARTIAL - actual fixed/live protection pass; persisted pins and reservations NOT_RUN. |
| P04-G04 | PASS - actual bilateral and one-sided production mutations. |
| P04-G05 | PASS - actual process crash, refusal, abort and duplicate END. |
| P04-G06 | PASS - cold persistence and unrelated link/read-only preservation. |
| P04-G07 | PASS for accepted P04 SHA, run 41101983231; current delivery CI is separate. |
| P04-G08 | PASS for scoped evidence and limitations, with later CI independently verified. |

### Local verification and recommendation

All commands use the workspace `.venv/Scripts/python.exe`. The integrated
executable trial and schema-3 rejection test are included in pytest.

| Command | Result |
| --- | --- |
| `python -m pytest -q --basetemp=.pytest-tmp -rs` | PASS: 704 passed in 346.59s; no skips. |
| `python tests/experiments/i3_final_integration.py` | PASS: measured single-database trace above. |
| `python -m ruff check .` | PASS: All checks passed! |
| `python -m ruff format --check .` | PASS: 96 files already formatted. |
| `python -m mypy` | PASS: no issues in 48 source files. |
| `python -m dgca_next verify-specs` | PASS: both exact RC4.4 hashes above. |
| `python -m pip check` | PASS: No broken requirements found. |
| `git diff --check` | PASS. |

The first exploratory integrated pytest run failed on three unclosed diagnostic
SQLite connections. The harness was corrected to close them, and the measured
trial and final complete suite above subsequently passed. This was a test
harness cleanup failure; no production mutation was fabricated or repaired.
The code/test-head CI run is
[41137244412](https://github.com/naoufelbvb2-arch/DGCA-NEXT-V1/actions/runs/41137244412)
for `8c808c58070757b118a8e4c8a547ce2ccbe1a56a`. Final-head CI for the report
commit must be verified separately; its SHA cannot be the earlier code head.

Recommendation: subject to successful final-head Ubuntu and Windows CI,
propose this branch for **scoped LANGUAGE first-lab engineering review**.
Explicit schema-3 migration/version policy and production persisted
pin/reservation support remain separate prerequisites for deployment or any
future phase that requires them. Scientific validity, generalization and the
out-of-scope complete scenarios remain unverified. No merge or I4 work is
authorized by this report.
