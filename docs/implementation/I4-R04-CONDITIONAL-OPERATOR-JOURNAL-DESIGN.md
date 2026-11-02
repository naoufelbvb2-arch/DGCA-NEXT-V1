# Conditional structural operator journal design

Status: implemented in the explicit experimental `I4_NATIVE_OPERATORS_V1`
capability after genuine eligibility receipts at F05r3/root59 and
F06r2/root109. Publication, recovery and final acceptance require separate
verification receipts; this design document alone grants no acceptance.
Authority: the bounded Master Contract, conditional on an actual eligible
RootStore END shadow. RC4.4 and all scientific numbers remain unchanged.

The accepted capabilities and experimental MULTI close versions1/2 retain
their exact replay behavior. A subsequent explicitly selected operator
capability must select a distinct close version and reject unsupported
operators before publication. Historical dispatch must select by the
persisted record version, never a current heuristic.

W5 can receive an optional, versioned operator journal extension, omitted
entirely for old states. Accepted old decoders reject this extension. The
extension cannot be a fake FORM record. A true derived SPLIT birth records
its actual parent ID/generation, partition and completed root reference;
no historical event is invented as an external three-cell birth witness.

Each immutable operator record must contain version, global operator
ordinal, operator kind, source IDs and complete before/after structural
rows, authentic root/event identity and observation/pre-W/pre-H digests,
completed close serial and completed-event prefix, actual eligibility and
cooldown calculation, plus before/after private-shadow hashes. The after
hash excludes the record itself, as in the accepted R03 journal. Original
FORM birth provenance is never rewritten. The canonical W hash must include
the new journal. No transient repair shadow is a public final-W codec.

SPLIT retains the parent ID and immutable original birth on L, increments
its current generation, and allocates the next never-used ID on R. The
derived child begins its own structural generation1 at the current close,
with explicit derived provenance rather than external FORM authority. Both
last-merge/split references identify this close. Subsequent old or new
operators must respect this lineage and the event-clock cooldown. Newly
derived IDs are not revisited by SPLIT in this END.

MERGE, if actually witnessed, retains the lower ID's original birth,
increments that survivor generation, and changes its members to the union.
The higher ID is archived permanently, retaining its last member tuple and
generation for historical inspection; it is removed from all LIVE cell and
inverse indexes. This records archival of the old version, not a fictional
new live generation. Both objects' last mutation and merge/split references
identify the actual close. Archived IDs are never allocated again.

Rebuild both membership indexes from the resulting LIVE registry and verify
each physical cell's independent membership list. Do not modify synapses,
credits, H, latent slots or physical reverse indexes for a native operation.
Ordinary positive synaptic settlement remains earlier in the same shadow.
Replay must interleave chronological MAINTAIN/GROW, FORM, MERGE, SPLIT
records in Core order, including derived births before any later mutation.
All final objects must pass actual reciprocal KEEP and capacity guards.

At runtime, inspect sorted initial live pairs, recalculate from each current
shadow, and never process an initial pair twice. Any ID edited in this END
receives age0 and is skipped by later MERGE/SPLIT checks. SPLIT enumerates
the surviving original live subjects after MERGE, with exact existing
partition ranking. Missing historical cooldown provenance refuses END.
No caller-supplied inspection, scalar diagnostic or proposed graph can
authorize publication.

Before enabling any corresponding writer: preserve a real eligible OPEN
journal, test the versioned representation and lineage refusal cases, then
verify production END publication, duplicate END, ABORT/rollback, repaired-
checksum tamper refusal, process exits on both sides of COMMIT, and cold
historical reconstruction. Copies of a real production checkpoint used for
crash controls are copies of the same lineage, not independent evidence
roots. An unavailable corresponding candidate keeps that writer disabled.
