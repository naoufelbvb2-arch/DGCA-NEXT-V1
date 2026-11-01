# R03 Schema-5 structural journal policy

This is an engineering serialization contract, not a scientific authority.
CORE/LLA RC4.4 remain unchanged. No SQL schema migration is performed.

`I3_SCHEMA4` retains its original interface, codec and P04 behavior.
`I4_NATIVE_FORM_V1` retains the accepted R02 first-FORM containment.
`I4_NATIVE_MAINTAIN_GROW_V1` explicitly selects the R03 operator capability
over experimental SQL schema 5. Both native capabilities reject schema
3/4 without modifying the database; neither supports P04 or automatic
recycling. The FORM-only close decoder fails closed on an R03 lifecycle
close rather than silently enabling new operators.

The R03 decoder accepts the exact accepted R02 W5 envelope. With no
structural mutations the encoder emits precisely those old bytes; it
does not insert an empty extension, update a version marker, rewrite
history or migrate saved checkpoints. Cross-revision tests generate a
database using actual source archived from accepted commit
`c66eb570b03e7653d9fa1f16c1805d52ad5f9072`, verify unchanged file bytes
and canonical W on opening in R03, and then continue through root5 GROW.
The caller-declared code revision remains the database identity; it is
not remote authentication of the executing Python code. New experiment
databases record the actual implementation HEAD separately in the trace.

The first structural mutation adds exactly two W5 envelope keys:
`structural_journal_version` (integer 1) and nonempty `mutations` (ordered
records). Empty, unknown-version, incomplete, or noncanonical extensions
are rejected. Generic binary records retain the existing canonical
sorted-key map encoding, finite big-endian binary64 encoding and strict
integer rules. Each mutation has these version-1 named fields:

- `schema_version`, dense global `ordinal`, `assembly_id`, `exposure_id`,
  `event_id`, `event_order`, `completed_close_serial`, `stage`.
- `before_members`, `after_members`, `before_generation`,
  `after_generation`, `before_status`, `after_status`.
- `observation_digest`, `event_pre_w_hash`, `event_pre_h_hash`,
  `witness_graph_hash`, `before_w_hash`, `after_w_hash`.
- `scores` (ordered physical cell, degree, density, numerator,
  denominator, specificity), `rank_support`, `inverse_removed`,
  `inverse_added`.

`witness_graph_hash` hashes canonical physical post-evidence W, excluding
native administration. `before_w_hash` hashes the full native shadow
before this change. `after_w_hash` hashes the full changed shadow with
the previous mutation log, **before appending this record itself**, to
avoid a circular self-hash. It is not the published post-END W hash.
Event references bind the last actual external EVENT of the closing
root as transaction authority. They do not turn growth into synaptic
evidence or assert that the new generation existed during that event.

MAINTAIN removal records one membership change and one generation step.
The terminal removal from three to two members is recorded as `ARCHIVE`
with one generation step, status ARCHIVED and removal of **all** former
live inverse references. The remaining two IDs are historical terminal
membership, not a live size-2 Assembly. This implements Core's instruction
to archive a subminimum set without inventing a second membership change
or retaining fictitious live references. Archived records remain in the
registry/high-watermark and cannot receive further R03 mutations.

The immutable original FORM record is never rewritten. Independent W
audit replays every membership/generation/status delta from that origin
and requires current membership/index equality. Current live members use
KEEP thresholds; initial FORM still uses its original stricter gates at
birth. Complete RootStore historical replay additionally recomputes
ordinary root settlement, MAINTAIN, ranked GROW, covered FORM exclusion
and deferred-operator guards against original root/event snapshots.
Checksums alone are insufficient authority.

R03 lifecycle closes use the existing close tag/version (0x43/5) with
`lifecycle_version=1`, `base_native` (unchanged canonical native-close
bytes), `mutation_ordinals`, `evaluations`, and `coverage`. First-FORM
roots retain their exact old close bytes. This extension records stable
no-change closes too, including empty mutation ordinals; it does not
change the W encoding when W has no structural mutation.

Only a private in-transaction hash function accepts temporarily
non-KEEP native administration over an independently audited physical
graph. Public graph encoding/loading and published W retain full
structural and history validation. Failed END discards the shadow.

The approved boundary remains one first Assembly: an additional required
FORM fails with `I4_FIRST_FORM_LAB_SCOPE_EXCEEDED`. After MAINTAIN/GROW,
multiple live Assemblies or a live size of at least N_min conservatively
fail with `I4_UNIMPLEMENTED_MERGE_SPLIT`; this is the contract-authorized
containment, not a claim that every such graph qualifies for a split.
The scientific constants K_FORM_PER_END=12 and K_max=16 are unchanged.
