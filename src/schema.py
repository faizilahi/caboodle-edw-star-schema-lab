"""Star object definitions and required columns."""
from __future__ import annotations

REQUIRED = {
    "DimPatient": ["PatientDurableKey", "MRN", "BirthDate", "Sex", "SourceSystem"],
    "DimDiagnosis": ["DxCode", "DxDescription", "DxType"],
    "FactEncounter": [
        "EncounterKey",
        "PatientDurableKey",
        "AdmitTs",
        "DischargeTs",
        "Department",
        "LOSDays",
    ],
    "BridgeEncounterDiagnosis": [
        "EncounterKey",
        "DxCode",
        "DiagnosisSeq",
        "PresentOnAdmission",
    ],
    "FactMedicationAdmin": [
        "AdminEventKey",
        "EncounterKey",
        "PatientDurableKey",
        "Medication",
        "AdminTs",
        "Dose",
    ],
}


def validate_columns(name: str, columns: set[str]) -> list[str]:
    need = set(REQUIRED[name])
    return sorted(need - columns)
