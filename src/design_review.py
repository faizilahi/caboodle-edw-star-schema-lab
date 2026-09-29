"""Run all star-schema design checks and return a report dict."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .bridge import assert_bridge_seq_unique, primary_dx
from .conformed_patient import collision_report, conform_patients
from .grain import bridge_explodes_fact, duplicate_keys, orphan_bridge
from .schema import validate_columns

DATA = Path(__file__).resolve().parents[1] / "data"


def load_star() -> dict[str, pd.DataFrame]:
    return {
        "DimPatient_raw": pd.read_csv(DATA / "DimPatient_raw.csv"),
        "DimDiagnosis": pd.read_csv(DATA / "DimDiagnosis.csv"),
        "FactEncounter": pd.read_csv(DATA / "FactEncounter.csv"),
        "BridgeEncounterDiagnosis": pd.read_csv(DATA / "BridgeEncounterDiagnosis.csv"),
        "FactMedicationAdmin": pd.read_csv(DATA / "FactMedicationAdmin.csv"),
    }


def review() -> dict:
    star = load_star()
    dim_pat = conform_patients(star["DimPatient_raw"])
    fact = star["FactEncounter"]
    bridge = star["BridgeEncounterDiagnosis"]
    admin = star["FactMedicationAdmin"]

    issues = []
    for name, df in [
        ("DimPatient", dim_pat),
        ("DimDiagnosis", star["DimDiagnosis"]),
        ("FactEncounter", fact),
        ("BridgeEncounterDiagnosis", bridge),
        ("FactMedicationAdmin", admin),
    ]:
        miss = validate_columns(name, set(df.columns))
        if miss:
            issues.append(f"{name} missing columns: {miss}")

    dup_enc = duplicate_keys(fact, "EncounterKey")
    if len(dup_enc):
        issues.append(f"FactEncounter duplicate keys: {len(dup_enc)}")

    orphans = orphan_bridge(bridge, fact)
    if len(orphans):
        issues.append(f"Bridge orphans: {len(orphans)}")

    try:
        assert_bridge_seq_unique(bridge)
    except ValueError as exc:
        issues.append(str(exc))

    if bridge_explodes_fact(fact, bridge):
        # Expected when bridge is many: documenting the fight, not a failure
        grain_note = "Bridge is many-per-encounter (correct); do not left-join raw onto reports without aggregating"
    else:
        grain_note = "Bridge unexpectedly 1:1 with fact"

    collisions = collision_report(star["DimPatient_raw"])
    return {
        "conformed_patients": len(dim_pat),
        "raw_patient_source_rows": len(star["DimPatient_raw"]),
        "mrn_collisions": len(collisions),
        "fact_encounters": len(fact),
        "bridge_rows": len(bridge),
        "primary_dx_rows": len(primary_dx(bridge)),
        "med_admin_events": len(admin),
        "grain_note": grain_note,
        "issues": issues,
        "pass": len(issues) == 0,
    }
