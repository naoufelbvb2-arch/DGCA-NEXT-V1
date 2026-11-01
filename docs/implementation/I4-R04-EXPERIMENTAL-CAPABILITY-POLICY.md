# R04 experimental capability and journal policy, version 1

This engineering policy implements only the named C01/C02 authorizations in
the owner approval and Master Contract. CORE/LLA RC4.4 remain unchanged.

`RootStore(execution_mode="I4_NATIVE_MULTI_V1")` explicitly selects the
experimental backend. Default schema-4, R02 FORM-only and R03 MAINTAIN/GROW
dispatch and their END implementations are preserved. No fixture builder,
caller-provided graph, or diagnostic can authorize a production birth.

The new capability uses the existing audited Schema-5 W representation for
FORM and single-object MAINTAIN/GROW records. Its additional capability is
multiple real births and existing live objects, not a reinterpretation of
old history. A FORM batch freezes one authorizing graph hash after ordinary
evidence settlement and MAINTAIN/GROW, before any birth in that batch. Seeds
use original verified external EVENT snapshots, ordered event/triangle
selection, disjoint assignment and the existing `K_FORM_PER_END` and `M_max`.
Each ID has its own immutable original FORM witness and current membership.
The global high-watermark and both independent membership indexes are
updated in the existing END SQLite transaction. All later events retain
these histories; physical synapses and topology are unchanged by native
operators. Every final W still passes the full accepted graph/native audit.

Close tag 0x43/schema5 gains an explicit canonical `r04_multi_version:1`
envelope around the exact R03 close encoding, with immutable ordered
operator-check byte records (tag 0x4F/version1). Checks contain actual live
ID/generation subjects, measured reciprocal mathematics and authenticated
cooldown decisions. A numeric analyzer's `NUMERIC_ONLY` field describes that
pure computation, never a publication permit. Production authority comes
from reconstruction of the original journal inside END and cold replay.

Historical dispatch uses the persisted close version: accepted R02 closes
replay the accepted FORM operator, R03 closes replay its accepted lifecycle
operator, and experimental closes replay the new operator. Selecting the
experimental reader changes no historical bytes. Accepted old readers reject
experimental closes rather than reinterpret them. No schema3/4 migration,
rewritten root, or new persisted clock is introduced.

The C01 prefix resolver runs only after full RootStore authentication. It
reconstructs consecutive completed close serials and their existing genuine
event counts, verifies historical cumulative `event_clock`, excludes future
closes during replay, and binds the prospective current END. A historical
`last_merge_split_close_serial` resolves that root's immutable prefix. None
means never edited; same-END touched IDs refuse at age0; unknown/missing
references refuse. A real completed reference without an actual native edit
tests this binding but does not demonstrate re-edit of a production Assembly.

MAINTAIN and GROW run in accepted deterministic order across the actual live
registry. FORM follows. Every actual live MERGE pair and SPLIT subject is
then inspected. An eligible MERGE/SPLIT with no verified writer throws
`I4_R04_{operator}_WRITER_NOT_PROVEN` before any publication, leaving the
root OPEN and all staged evidence unpublished. It is never silently skipped.
`inspect_pending_native` reconstructs exactly the same private shadow in a
read snapshot. Its output explicitly says **PROVISIONAL**, `committed=False`;
it is not a completed-root witness or an input accepted by END.

A real MERGE writer or derived SPLIT lineage would require a further
versioned policy/codec/journal and actual eligible production witness first.
This version implements neither writer and retains the accepted audit's
refusal of merge/split stamps. No automatic recycling, contextual owner,
Attractor, readout, generation or later milestone is enabled.
