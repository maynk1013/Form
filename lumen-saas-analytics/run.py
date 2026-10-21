"""Rebuild the warehouse, refresh every extract, and rewrite the executive report."""

from pathlib import Path

from src.analyze import analyze
from src.warehouse import build_warehouse

ROOT = Path(__file__).resolve().parent


def main() -> None:
    db_path = ROOT / "data" / "lumen.db"
    print("Building warehouse...")
    build_warehouse(db_path)
    print(f"Warehouse: {db_path}")
    analyze(db_path)


if __name__ == "__main__":
    main()
