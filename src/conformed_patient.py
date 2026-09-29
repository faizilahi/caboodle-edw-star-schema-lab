"""Conformed DimPatient build with source priority."""
from __future__ import annotations

import pandas as pd

SOURCE_PRIORITY = {"clarity_inpatient": 1, "clarity_ambulatory": 2, "claims": 3}


def conform_patients(raw: pd.DataFrame) -> pd.DataFrame:
    """Collapse MRN collisions; lowest priority number wins."""
    df = raw.copy()
    df["prio"] = df["SourceSystem"].map(SOURCE_PRIORITY).fillna(99)
    df = df.sort_values(["MRN", "prio"])
    winners = df.groupby("MRN", as_index=False).first()
    winners["PatientDurableKey"] = winners["MRN"].apply(lambda m: f"PDK-{m}")
    return winners.drop(columns=["prio"])


def collision_report(raw: pd.DataFrame) -> pd.DataFrame:
    counts = raw.groupby("MRN").size().reset_index(name="source_rows")
    return counts[counts["source_rows"] > 1]
