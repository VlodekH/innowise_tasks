from pathlib import Path
import runpy


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    runpy.run_path(repo_root / "scripts" / "init_db.py", run_name="__main__")


if __name__ == "__main__":
    main()
