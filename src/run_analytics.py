import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from paths import DATA_DIR, DB_PATH, OUTPUT_DIR  # noqa: E402
from star_schema import run_analytics  # noqa: E402


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    results = run_analytics(DB_PATH, DATA_DIR)
    for name, df in results.items():
        path = OUTPUT_DIR / f"{name}.csv"
        df.to_csv(path, index=False)
        print(df.to_string(index=False))
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
