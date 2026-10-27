# DGCA NEXT V1

Research implementation of the **Dynamic Graph Cognitive Architecture — DCR**.

## Project status

**I0 — Repository & Contract Foundation (IN PROGRESS).**

The implementation is based on two design-candidate specifications to be added under `docs/specs/`:

- `DGCA_CORE_RC4_1.md` — Core anatomy, dynamics, assemblies, contextual memory and bounded generation.
- `DGCA_LLA_RC4_1.md` — local learning, evidence, consolidation and derived context witnesses.

Both specifications are **RC4.1 / NOT FROZEN / NOT IMPLEMENTED / NOT EMPIRICALLY VERIFIED**. They are design contracts, not evidence of model capabilities. Scientific or numerical changes require explicit documentation and tests; coding agents must not tune thresholds to make tests pass.

## Implementation direction

Python reference implementation, sparse graph, deterministic event ordering, local learning without backpropagation, CPU-first. First experiments validate actual learned synapses, native assemblies, contextual next-event retrieval, hierarchical context, and read-only autoregressive generation. Compositional G3 is a separate unproven research goal.

`DGCA NEXT` is a standalone repository; the original DGCA and DGCA LITE repositories must remain untouched.

## Development policy

- Each implementation milestone uses a feature branch, review, regression suite and recorded evidence.
- Distinguish unit tests using constructed network fixtures from empirical tests learning from real input events.
- Do not report an unexecuted test as passed.
- Maintain independent `W` (learned graph), `R` (working runtime state), and `H_slow` (slow adaptation) boundaries.
- Do not copy text labels or expected answers into the neural learning or selection path.
