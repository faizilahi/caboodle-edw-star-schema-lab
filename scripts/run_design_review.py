#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.conformed_patient import conform_patients
from src.design_review import load_star, review

OUTPUT = ROOT / "output"


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    report = review()
    print("=== Caboodle star design review ===")
    print(json.dumps(report, indent=2))
    star = load_star()
    conform_patients(star["DimPatient_raw"]).to_csv(OUTPUT / "DimPatient.csv", index=False)
    with (OUTPUT / "design_review.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
