"""Audit every normative LLA/LG test; component PASS is not scientific PASS."""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

UPDATES = {
    "LLA-T13": (
        "COMPONENT_LEVEL_ONLY",
        "Native production R/history cold resets and root isolation now pass. "
        "No separate injected-residual BEGIN scientific experiment is claimed.",
    ),
    "LLA-T15": (
        "COMPONENT_LEVEL_ONLY",
        "Genuine native END/retry and IDs/generations pass. "
        "Specified contextual OwnerIDs/reservations are absent.",
    ),
    "LLA-T16": (
        "COMPONENT_LEVEL_ONLY",
        "Genuine native read-only processing is immutable. "
        "Full owned P/B scenario is not implemented.",
    ),
    "LLA-T17": (
        "COMPONENT_LEVEL_ONLY",
        "Actual comparable transient Attractor error is computed; "
        "negative evidence remains disabled. "
        "Full owned contrast scenario is not executed.",
    ),
    "LG-T01": (
        "FULL_SCIENTIFIC_SCENARIO_EXECUTED_PASS",
        "Actual Root4 legal consolidated reciprocal triangle, deterministic Assembly0 GEN1 "
        "and inverse membership, reproduced in R02 and F01/F02/F03.",
    ),
    "LG-T02": (
        "COMPONENT_LEVEL_ONLY",
        "Actual Root2/3 candidate-only branch produces zero Assemblies. "
        "One-direction-only consolidated branch is component coverage, "
        "not a new genuine production scenario.",
    ),
    "LG-T03": (
        "COMPONENT_LEVEL_ONLY",
        "Actual FORM/GROW/M/S IDs/generations/restarts and stale refusal pass. "
        "No readout ledger/rendering/outbox exists; the full named scenario is NOT_RUN.",
    ),
    "LG-T16": (
        "NOT_RUN_OR_OUTSIDE_SCOPE",
        "Prescribed q=.2025/.36/.49/.64 cold schedules and surface attestations are not executed. "
        "Genuine FORM with other actual q does not satisfy that full scenario.",
    ),
}


def run():
    source = ROOT / "docs/specs/DGCA_LLA_RC4_4.md"
    prior = (ROOT / "docs/implementation/I3-FINAL-CONSOLIDATED-VERIFICATION-REPORT.md").read_text(
        encoding="utf-8"
    )
    old = {
        m[0]: m[1]
        for m in re.findall(r"^\| \[(LLA-T\d+|LG-T\d+)\].*? \| (?:.*?) \| (.*?) \|$", prior, re.M)
    }
    rows = []
    for lineno, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        match = re.match(r"^\| `?(LLA-T\d+|LG-T\d+)`? \| (.*?) \| (.*?) \|$", line)
        if not match:
            continue
        identity, given, required = match.groups()
        previous = old[identity]
        if identity in UPDATES:
            disposition, note = UPDATES[identity]
        elif previous.startswith("FULL_SCENARIO_EXECUTED_PASS"):
            disposition = "FULL_SCIENTIFIC_SCENARIO_EXECUTED_PASS"
            note = (
                previous.split(" - ", 1)[1]
                + "; accepted historical I3 evidence retained, not relabeled as new I4 evidence."
            )
        elif previous.startswith("COMPONENT_OPERATOR_PASS"):
            disposition = "COMPONENT_LEVEL_ONLY"
            note = previous.split(" - ", 1)[1]
        else:
            disposition = "NOT_RUN_OR_OUTSIDE_SCOPE"
            note = (
                "Full scientific scenario not executed; contextual owners, Replay, "
                "readout or generation are outside this assignment."
            )
        rows.append(
            dict(
                id=identity,
                normative_line=lineno,
                given=given,
                required=required,
                disposition=disposition,
                note=note,
            )
        )
    expected = {f"LLA-T{i:02}" for i in range(1, 42)} | {f"LG-T{i:02}" for i in range(1, 17)}
    assert len(rows) == 57 and {r["id"] for r in rows} == expected
    result = dict(
        authority="docs/specs/DGCA_LLA_RC4_4.md",
        scientific_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        status="SCIENTIFIC_COVERAGE_NOT_A_FREEZE",
        categories=dict(Counter(r["disposition"] for r in rows)),
        tests=rows,
    )
    target = ROOT / "docs/implementation/evidence/i4-r05-r06/SCIENTIFIC-COVERAGE.json"
    target.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["categories"], sort_keys=True))


if __name__ == "__main__":
    run()
