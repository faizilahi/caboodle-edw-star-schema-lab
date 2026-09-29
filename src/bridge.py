"""BridgeEncounterDiagnosis helpers."""
from __future__ import annotations

import pandas as pd


def assert_bridge_seq_unique(bridge: pd.DataFrame) -> None:
    dup = bridge.duplicated(["EncounterKey", "DiagnosisSeq"], keep=False)
    if dup.any():
        raise ValueError("Bridge has duplicate EncounterKey+DiagnosisSeq")


def primary_dx(bridge: pd.DataFrame) -> pd.DataFrame:
    return bridge[bridge["DiagnosisSeq"] == 1][["EncounterKey", "DxCode"]].rename(
        columns={"DxCode": "PrimaryDxCode"}
    )
