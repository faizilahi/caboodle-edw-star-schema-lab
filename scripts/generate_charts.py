import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from paths import DATA_DIR, DB_PATH  # noqa: E402
from star_schema import run_analytics  # noqa: E402

IMG_DIR = ROOT / "docs" / "images"


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    results = run_analytics(DB_PATH, DATA_DIR)
    alos = results["alos_by_facility"]
    readmit = results["readmission_proxy"]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(alos["facility_name"], alos["avg_los"], color="#3A86FF")
    ax.set_title("Star Schema KPI: ALOS by Facility (Synthetic)")
    ax.set_ylabel("Days")
    plt.xticks(rotation=15, ha="right")
    fig.tight_layout()
    fig.savefig(IMG_DIR / "kpi_alos_by_facility.png", dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 4))
    rate = float(readmit["readmit_proxy_rate"].iloc[0])
    ax.bar(["30-day readmit proxy"], [rate], color="#FF006E")
    ax.set_ylim(0, max(0.15, rate * 1.5))
    ax.set_title("Readmission Proxy Rate (Educational)")
    fig.tight_layout()
    fig.savefig(IMG_DIR / "kpi_readmission_proxy.png", dpi=120)
    plt.close(fig)
    print(f"Saved charts to {IMG_DIR}")


if __name__ == "__main__":
    main()
