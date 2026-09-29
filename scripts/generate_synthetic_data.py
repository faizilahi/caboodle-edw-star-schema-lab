"""Generate star-schema dimension and fact CSVs (synthetic Caboodle-style lab)."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
random.seed(99)

FACILITIES = [
    (1, "Synthetic Medical Center"),
    (2, "Synthetic Community Hospital"),
    (3, "Synthetic Ambulatory Pavilion"),
]
ENC_TYPES = [(1, "Inpatient"), (2, "Emergency"), (3, "Ambulatory")]
N_PATIENTS = 600
N_FACT = 2800


def date_dim() -> pd.DataFrame:
    rows = []
    d = date(2024, 1, 1)
    for key in range(1, 367):
        rows.append(
            {
                "date_key": key,
                "full_date": d.isoformat(),
                "year": d.year,
                "month": d.month,
                "day_of_week": d.strftime("%A"),
            }
        )
        d += timedelta(days=1)
    return pd.DataFrame(rows)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dim_patient = pd.DataFrame(
        [
            {
                "patient_key": i,
                "patient_id": f"P{i:05d}",
                "sex": random.choice(["F", "M"]),
                "birth_year": random.randint(1940, 2010),
            }
            for i in range(1, N_PATIENTS + 1)
        ]
    )
    dim_facility = pd.DataFrame(
        [{"facility_key": k, "facility_id": f"F{k}", "facility_name": n} for k, n in FACILITIES]
    )
    dim_encounter_type = pd.DataFrame(
        [{"encounter_type_key": k, "encounter_type": n} for k, n in ENC_TYPES]
    )
    dim_date = date_dim()

    facts = []
    for eid in range(1, N_FACT + 1):
        et_key = random.choices([1, 2, 3], weights=[0.22, 0.33, 0.45])[0]
        admit_offset = random.randint(0, 365)
        los = round(random.uniform(1.0, 7.0), 1) if et_key == 1 else None
        facts.append(
            {
                "encounter_id": eid,
                "patient_key": random.randint(1, N_PATIENTS),
                "facility_key": random.choice([1, 2] if et_key == 1 else [1, 2, 3]),
                "encounter_type_key": et_key,
                "admit_date_key": admit_offset + 1,
                "length_of_stay_days": los if los is not None else "",
            }
        )
    fact_encounter = pd.DataFrame(facts)

    dim_patient.to_csv(DATA_DIR / "dim_patient.csv", index=False)
    dim_facility.to_csv(DATA_DIR / "dim_facility.csv", index=False)
    dim_date.to_csv(DATA_DIR / "dim_date.csv", index=False)
    dim_encounter_type.to_csv(DATA_DIR / "dim_encounter_type.csv", index=False)
    fact_encounter.to_csv(DATA_DIR / "fact_encounter.csv", index=False)
    print(
        f"Generated dims + {len(fact_encounter)} fact rows into {DATA_DIR}"
    )


if __name__ == "__main__":
    main()
