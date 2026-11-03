# R05 native runtime authority and checkpoint design

Engineering design; execution results are not yet verified. CORE/LLA RC4.4
remain unchanged and are the only scientific authorities.

`I4_NATIVE_ATTRACTOR_V1` explicitly selects the new capability. Default I3,
R02/R03 and R04 modes retain their exact event/W/close behavior. No existing
database is migrated. Fresh R05 databases retain native SQL schema5 and add
one explicitly recognized native runtime table. Old readers refuse that
table set; new LEARN mode refuses an old database lacking its R journal.
Read-only native processing can inspect an authenticated existing native
RootStore without altering its database or enabling a learning mode.

W5, immutable FORM/mutation/operator history and native END remain R04's
representation. Attractors are not Assembly knowledge, synapses or W fields.
The accepted ExternalEventObservation v2 remains the source of actual normal
activity, direct SIC and q/y proposals. Only the R05 backend computes its
normal activity with native prior sigma. A separate R record binds that
observation to the native dynamics/provenance that actually produced it.

Native R uses a new canonical tagged binary version, distinct from R_COLD.
It contains the base event bytes, actual external observation scope, prior
runtime hash, event-start W/H hashes, committed checkpoint W/H hashes,
fresh pass1/pass2, prior sigma, native ID/generation/member references,
computed fresh mean/cohesion, sorted prior-member predictions/current direct
comparables, miss/error/age/collapse diagnostics and bounded runtime state.
All maps/numbers use the accepted binary record codec, strict field types,
finite binary64, physical-ID order and exact Q6 comparisons. Error may exceed
one, so the already existing nonnegative Q6 sum quantizer handles it.

The per-EVENT table is keyed by the actual p01 EVENT ID and stores the same
native R bytes that become metadata.r_state. Both records, normal event,
proposals, sensory W, H and next order publish in the existing EVENT SQL
transaction. BEGIN, ABORT and successful END retain the existing R_COLD
semantics. Failure before COMMIT leaves all old bytes; failure after COMMIT
recovers the one new checkpoint. Duplicate event order is refused, never
replayed as another runtime step. A later independent root starts cold.

Native validation replays each original root from R_COLD over its original
per-event W/H, actual SIC and recorded scope. It recomputes actual passes,
frontiers, native state and permitted H/births and requires exact canonical
R and checkpoint equality. Then existing root settlement/FORM/MG/operators
are rederived with the verified native event witnesses. A checksum or a
decoder alone is not historical authority. Temporary audit results confer
no public learning permission. Unknown versions and missing/forged native
records fail closed; accepted historical modes keep their original verifier.

Observation scope is the existing LLA2.1 ingress concept, explicitly recorded
for this new capability. No scope is inferred from a desirable result.
COMPLETE_NEXT_EVENT is supplied as part of a real external observation;
PARTIAL and UNSPECIFIED cannot authorize miss. Every compared target must
also be currently directly SIC-witnessed and previously committed, and its
prediction must be computed from real prior native member F_step emitters
and legal ASSOCIATIVE Q. Absence of an expected target is not a supplied
zero; no expected-outcome label, target list, prediction or miss scalar is
an ingress parameter. Error changes only transient R, never negative q/W.

Read-only sessions freeze authenticated W/H, construct native-only typed
state, process real SIC, and preserve W/H/evidence/caller R exactly. Fixture
Assemblies/bindings and arbitrary runtime records cannot authorize this API.
Current structural identity/generation is checked before any contextual
influence. A changed/archive subject cannot retain sigma through its old ID.
The declared zero-context ablation is isolated read-only computation on the
same checkpoint, not a production learning option or performance promise.

No native contextual owner, surface ledger, generation, Replay, automatic
recycling or native/P04 coexistence is added. Runtime validity is not a
new external evidence lane. Final details and exact codec fields are to be
verified in implementation/tests; no synthetic example is native production
acceptance. R06 begins only after the required genuine R05 gate passes.
