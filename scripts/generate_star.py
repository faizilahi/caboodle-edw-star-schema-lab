#!/usr/bin/env python3
from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
RNG = random.Random(42)

DX = [
    ("I10", "Essential hypertension", "ICD10"),
    ("E11.9", "Type 2 diabetes NOS", "ICD10"),
    ("J18.9", "Pneumonia unspecified", "ICD10"),
    ("N18.3", "CKD stage 3", "ICD10"),
    ("F32.9", "Depression NOS", "ICD10"),
]


def main() -> None:
    raw_pat = []
    # 300 MRNs; 40 appear in two source systems
    for i in range(1, 301):
        mrn = f"{100000+i}"
        raw_pat.append(
            {
                "MRN": mrn,
                "BirthDate": f"{RNG.randint(1945,2000)}-06-15",
                "Sex": RNG.choice(["F", "M"]),
                "SourceSystem": "clarity_inpatient",
            }
        )
        if i <= 40:
            raw_pat.append(
                {
                    "MRN": mrn,
                    "BirthDate": f"{RNG.randint(1945,2000)}-06-15",
                    "Sex": RNG.choice(["F", "M"]),
                    "SourceSystem": "claims",
                }
            )

    dim_dx = pd.DataFrame([{"DxCode": c, "DxDescription": d, "DxType": t} for c, d, t in DX])

    facts, bridge, admins = [], [], []
    admin_n = 0
    for i in range(1, 501):
        ek = f"ENC-{i:05d}"
        mrn = f"{100000 + RNG.randint(1, 300)}"
        admit = datetime(2024, 1, 1) + timedelta(days=RNG.randint(0, 300))
        los = RNG.randint(1, 12)
        facts.append(
            {
                "EncounterKey": ek,
                "PatientDurableKey": f"PDK-{mrn}",
                "AdmitTs": admit.isoformat(sep=" "),
                "DischargeTs": (admit + timedelta(days=los)).isoformat(sep=" "),
                "Department": RNG.choice(["MED", "SURG", "ICU", "ED"]),
                "LOSDays": los,
            }
        )
        # 1-4 diagnoses
        n_dx = RNG.randint(1, 4)
        chosen = RNG.sample(DX, n_dx)
        for seq, (code, _, _) in enumerate(chosen, start=1):
            bridge.append(
                {
                    "EncounterKey": ek,
                    "DxCode": code,
                    "DiagnosisSeq": seq,
                    "PresentOnAdmission": RNG.choice(["Y", "N", "U"]),
                }
            )
        for _ in range(RNG.randint(0, 3)):
            admin_n += 1
            admins.append(
                {
                    "AdminEventKey": f"ADM-{admin_n:06d}",
                    "EncounterKey": ek,
                    "PatientDurableKey": f"PDK-{mrn}",
                    "Medication": RNG.choice(["metformin", "lisinopril", "heparin", "ondansetron"]),
                    "AdminTs": (admit + timedelta(hours=RNG.randint(1, los * 24))).isoformat(sep=" "),
                    "Dose": RNG.choice(["5mg", "10mg", "500mg", "2mg"]),
                }
            )

    pd.DataFrame(raw_pat).to_csv(DATA / "DimPatient_raw.csv", index=False)
    dim_dx.to_csv(DATA / "DimDiagnosis.csv", index=False)
    pd.DataFrame(facts).to_csv(DATA / "FactEncounter.csv", index=False)
    pd.DataFrame(bridge).to_csv(DATA / "BridgeEncounterDiagnosis.csv", index=False)
    pd.DataFrame(admins).to_csv(DATA / "FactMedicationAdmin.csv", index=False)
    print(f"Star generated: {len(facts)} encounters, {len(bridge)} bridge rows, {len(admins)} admin events")


if __name__ == "__main__":
    main()
