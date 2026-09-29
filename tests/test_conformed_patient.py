import pandas as pd

from src.conformed_patient import conform_patients


def test_inpatient_wins_over_claims():
    raw = pd.DataFrame(
        [
            {"MRN": "1", "BirthDate": "1980-01-01", "Sex": "F", "SourceSystem": "claims"},
            {"MRN": "1", "BirthDate": "1980-01-01", "Sex": "F", "SourceSystem": "clarity_inpatient"},
        ]
    )
    out = conform_patients(raw)
    assert len(out) == 1
    assert out.iloc[0]["SourceSystem"] == "clarity_inpatient"
