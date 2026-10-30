# I3-R00 production authority preflight

Baseline: `aacd16f` on `feature/i3-local-learning`, based on accepted I2 main
`f63935c143b3fa1ef016078a58309f648a51bd22`. Sources: Core/LLA RC4.3; both
are unchanged design candidates. Existing I0–I2 regressions must remain intact.

## Existing boundaries

- `Cell`, `Synapse`, `SlotAssignment` and `FixtureEventSnapshot` reject
  production-origin committed records. `_Editor` and `FixtureBuilder` create
  fixture records and `validate_graph` rechecks them. Synthetic records cannot
  serve as external witnesses. A production engine must add a separately gated
  origin and validated root-close authority; relabeling fixture data is invalid.
- L01 selection functions use a single immutable `FixtureEventSnapshot`; its
  type and assignment metadata are explicitly fixture-only. Production must use
  a separately authenticated event snapshot and preserve atomic co-birth,
  slots, reverse index, metadata and the existing graph audits.
- I2 `two_pass`, `GraphSnapshot`, `regional_firing` and `adapt` are pure numeric
  operators, but I2 `read_only_step` deliberately produces only READ_ONLY
  provenance. An I3 LEARN event must create its own typed witness and must not
  promote a read-only trace or fixture marker into training authority.
- `Homeostasis` has no default g/r_bar/region EMA. I2 explicitly identifies
  `uniform_language` as a **synthetic fixture**. Any initial H state must be
  explicit, frozen, versioned and durable; it cannot be inferred from fixture
  values. The owner-approved profile fixes LANGUAGE theta=.20, not these values.
- I1 source creation timing uses a scalar committed/event index; I3 must preserve
  physical source/target commitment order across independent roots, rather than
  confusing per-root event order with a globally ordered event identity.
- `debug_dump` and its hash are diagnostic only, not a complete persistence
  codec. A durable store needs an explicitly versioned record schema, canonical
  binary64 and provenance validation. Read-only graph views must never be the
  only authority for accepting external evidence.

## Unresolved decisions identified during preflight

**I3-S01: sensory cohort arbitration at capacity.** Core §§1.3.1 and 12,
LLA §§5.1 and 7, and the I3 contract define `K_R=12`, directly observed
eligibility, and how the **already accepted** cohort initializes its latent
slots. They do not define how to choose an accepted subset when more than 12
uncommitted receivers qualify. The `(-score_q6,cell_id)` ordering in Core
§1.3.4 selects **latent targets after the cohort is accepted**; it does not
specify sensory admission priority. Minimal physical reproducer:

```python
from dgca_next.peripheral.sic import project
p = project(tuple((f, "1") for f in ("a", "ab", "c", "d")))
assert len(p.X_fixed) == 16  # all 16 distinct direct receivers have support 1
```

With a cold graph all 16 qualify but at most 12 may be admitted; no normative
accepted subset or tie rule is given. Do not silently choose 12 by physical ID,
feature order or a new ranking. This blocks a general EVENT admission contract.

**I3-S02: initial slow state for a cold graph and later newborns.** Core §1.2
sets `g∈[.70,1.40]`, §5 gives update laws and §12 sets only LANGUAGE's initial
threshold. Neither source nor the I3 contract supplies a newborn `g`/`r_bar`
or initial regional `rho_bar`, or defines how a cold run receives them. For
the same lone committed LANGUAGE receiver and direct `X=1`, the existing I2
normalizer yields different legal pass-1 activities for `g=.70` and `g=1.0`;
both satisfy the bound and influence creation/coactivity. No default can be
deduced from the equations. A caller-supplied fully explicit pre-existing H
snapshot can be encoded for transaction skeleton tests, but it does not by
itself define values for newly admitted cells or authorize choosing experiment
initialization. Owner clarification must specify initial state or authorize an
explicit experiment profile and newborn rule.

These are scientific gaps, not proof that the model cannot learn. Until they
are resolved, the cold-start learning experiment cannot be executed through a
complete lawful LEARN interface and is **NOT_RUN / SPEC_BLOCKED**, not an
empirical failure. Independent, unambiguous transaction and numeric work may
continue without changing scientific sources or fabricating production roots.

## Transaction and provenance design boundary

Use a SQLite local database with one atomic transaction per state publication,
monotonic nonreused root IDs, an exclusive persisted OPEN marker and canonical
versioned H/W/R/journal records. BEGIN must snapshot the exact supplied H and
reset R; ABORT restores that BEGIN image, clears root-local staging and cannot
overwrite later completed-root H. Event and END publication require, respectively,
a verified external event capability and a validated same-root close capability.
Record source/spec/config identities and reject unsupported schemas or integrity
mismatches. A Python-private capability is a process-boundary discipline, not
authentication of real-world truth; caller-supplied external features are not
semantic ground truth. No synthetic witness, fixture graph or arbitrary scalar
may mint a production evidence root.

I3-R01 may safely implement the closed/OPEN/ABORT persistence skeleton with a
caller-supplied explicit H image while keeping EVENT and END fail-closed until
the missing rules and production graph path are implemented. Pure evidence
arithmetic may be verified separately without treating its inputs as witnesses.
