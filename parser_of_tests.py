from pathlib import Path

EXTENSIONS = {".py", ".toml", ".yaml", ".yml"}


def collect_files(root: Path):
    return [f for f in root.rglob("*") if f.is_file() and f.suffix in EXTENSIONS]


def write_files(files, output: Path):
    with output.open("w", encoding="utf-8") as out:
        for f in files: out.write(f"{f}\n{f.read_text(encoding='utf-8')}\n\n")


def main():
    root = Path.cwd()
    write_files(collect_files(root / "tests"), root / "tests_dump.txt")


if __name__ == "__main__":
    main()
