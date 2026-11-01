# DGCA NEXT — I4-R03 Independent Engineering Acceptance Review

**ID:** I4-R03-INDEPENDENT-ACCEPTANCE-REVIEW
**Review date:** 2026-10-31
**Reviewed production implementation/report SHA:** `439430c14132bc9d139504da46f4278b4fb412e9`
**Verdict:** **I4-R03 ACCEPTED — REAL PRODUCTION 3→4 GROW AND STABLE MAINTAIN; MAINTAIN REMOVAL/ARCHIVE ONLY COMPONENT-VERIFIED.**
**Final-head CI:** GitHub Actions `41269646550`; exact `head_sha=439430c14132bc9d139504da46f4278b4fb412e9`; Ubuntu and Windows completed **SUCCESS**.
**Scientific sources:** CORE RC4.4 and LLA RC4.4 unchanged, DESIGN CANDIDATES / NOT FROZEN / NOT EMPIRICALLY VERIFIED.
**Main:** unchanged `88fc596c178c8a89c24b991e280d7a0ca8c07779`. No merge or R04 code is included here.

## Independently examined evidence

Reviewed the complete R03 committed verification report; exact source diff; `graph/native_lifecycle.py` pure scoring/MAINTAIN/GROW ranking; `graph/native_mutation.py` immutable provenance; `learning/native_lifecycle.py` production root-close shadow integration; `native_assembly.py` history/KEEP checks; `docs/implementation/I4-R03-SCHEMA5-STRUCTURAL-JOURNAL.md`; and the original Core §2.0 executable rules. Verified GitHub final-head CI against the delivery SHA and both matrix jobs. The report claims **796 local pytest PASS** (+43 over R02's 753), 0 final fail/skip, Ruff/format/mypy/dependency/spec-integrity PASS; reviewer did **not** independently run Python tests or subprocess crashes.

The report candidly includes a prior failed intermediate CI/test expectation and its corrected standalone test change. The final green code+report SHA supersedes that earlier run, and the source update does not alter RC4.4 numeric laws.

## Genuine production life-cycle results

Fresh actual Schema-5 LANGUAGE RootStore trial:
- Roots1–4 reproduce the accepted real first FORM: AssemblyID=0, LIVE, GEN1, members `8606,9345,11795`, birth completed serial4 and immutable original FORM root4/event5.
- Root5 event7 is genuine `EXTERNAL_DIRECT/LEARN`; direct support `X_fixed=1000000` for four previously committed physical receivers, frozen final A=.7259368601806818 and legal emitter/F_step. Ordinary learning first updates twelve independent LOCAL synapses with accepted `q=.5269843249689868`, paired `y=.8576295377561982`, new `E_ext=3.526984324968987`, `S=.9787277189155831`, `Q=.34519573230279144`, external root count4. GROW itself does not mint any synapse/evidence.
- Existing Assembly0 old-member MAINTAIN scores d=2,D=1,Spec=2/3 PASS. The actual fourth physical cell 12181 has lawful 3 reciprocal links with ranked support1.0355871969083743, prospective d=3,D=1,Spec=1; previous members also preserve KEEP. The root5 atomic END changes **current membership** to `8606,9345,11795,12181`, ID0 stays, GEN1→GEN2, last_mutation_completed_serial5, original birth serial4 unchanged.
- Exactly one ROOT5/EVENT7 `GROW_ADD` mutation record, ordinal0, both member and reverse indexes updated; full trusted cold historic rederivation and independent interpreter recovery preserve FORM and edit histories.
- Real root6 event8 is an empty external feature event; W/GEN2/mutation journal are byte-identical to root5, no evidence credit or new ID. H legally adapts in this completed external event and is **not** claimed unchanged. Separate READ_ONLY does not mutate W/H/evidence/identity.
- Actual subprocess kills before/after END5 and ABORT and duplicate completed END demonstrate the reported pre/post-transaction state and one generation step, not repeated structural mutation. Forensic tests re-sign simple checksums for tampered history and validate that historical rederivation still refuses invalid origin/sequence.
- R03's `I4_NATIVE_MAINTAIN_GROW_V1` capability accepts authentic accepted-source prior R02 Schema-5 journals with original W bytes preserved until mutation. Default I3/P04 and R02 FORM-only mode remain separate, with no auto recycling.

## Strict limitations and carried-forward risks

**MAINTAIN no-change is production-tested; removal of a failing member and ARCHIVE are NOT production-tested.** Lowest-ID iterative removal, terminal 3→2 ARCHIVE, KEEP-vs-FORM thresholds, no-reused identity, physical-only temporary validation and mutation codec are component/isolated-fault checks. They are NOT a demonstrated genuine lawfully degraded learned W. Do not mark LG-T03 whole lifecycle PASS from them.

**R04 reachability is unresolved.** Current lab permits only the first FORM and conservatively refuses an END with multiple live Assemblies or a live Assembly reaching Core N_min=6. An actual Core MERGE needs overlapping LIVE identities with Jaccard>=.70, nonempty exclusives and exclusive-pair mean reciprocal strength>=.40, and legal union KEEP/capacity/cooldown. A SPLIT needs size>=6 and a valid 3+3 or larger partition with all cross support<=.15 and mean<.10. The controlled `a` four-cell clique and GEN2 size4 prove neither operation. Their physical feasibility must be measured, never assumed or fabricated by fixture injection.

**Cooldown source ambiguity for R04:** Core §2.0 says `T_c=200 completed external events` while the persistent identity field is `last_merge_split_close_serial` and completed-close serial counts completed external roots. Before an authoritative production MERGE/SPLIT cooldown implementation, define a documented consistent counter/clock mapping (or stop SPEC_BLOCKED) rather than silently equating every event with a completed root. Do not change Core/LLA science text to resolve an engineering choice.

**R03 data limits:** Schema5 structural mutation log is canonical and backward-compatible with accepted R02 records in its explicit mode; schema3/4 migration remains unsupported. Native contextual pins/reservations, P04 coexistence, Attractor, readout, Replay, generation and automatic recycling are NOT_RUN; R04 cannot claim them by inheritance.

**Scientific claim:** Proven production FORM then one rooted GROW and persisted GEN2, NOT autonomous cognitive organization/semantic language understanding, not true production removal, not native MERGE/SPLIT. Preserve the 796 reported regressions and scientific hashes.

**Disposition:** **I4-R03 ACCEPTED within its scoped first-LANGUAGE production FORM→GROW lifecycle. Full I4 remains PARTIAL.** Next authorized work is a narrowly read-only/pure **I4-R04-P00 reachability and policy gate** before permitting irreversible native MERGE/SPLIT runtime implementation. No main merge, no source change.
