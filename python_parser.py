from pathlib import Path
import ast
import io
import tokenize

EXCLUDED_DIRS = {".venv", "tests", "docs", "data"}
EXCLUDED_FILES = {"python_parser.py", "parser_of_tests.py"}
EXTENSIONS = {".py", ".toml", ".yaml", ".yml"}


def should_exclude(path: Path) -> bool:
    return path.name in EXCLUDED_FILES or (
        path.parts[:2] != ("src", "data")
        and ("data" in path.parts or EXCLUDED_DIRS & set(path.parts))
    )


def remove_python_docstrings(source: str) -> str:
    ranges = [(n.body[0].lineno, n.body[0].end_lineno) for n in ast.walk(ast.parse(source))
              if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
              and n.body and isinstance(n.body[0], ast.Expr)
              and isinstance(n.body[0].value, ast.Constant)
              and isinstance(n.body[0].value.value, str)]
    return "\n".join(line for i, line in enumerate(source.splitlines(), 1) if not any(a <= i <= b for a, b in ranges))


def remove_python_comments(source: str) -> str:
    out = io.StringIO()
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type != tokenize.COMMENT: out.write(tok.string)
        if tok.type in (tokenize.NEWLINE, tokenize.NL): out.write("\n")
    return out.getvalue()


def clean_content(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".py": text = remove_python_comments(remove_python_docstrings(text))
    return "\n".join(line for line in text.splitlines() if line.strip())


def collect_files(root: Path):
    return [f for f in root.rglob("*") if f.suffix in EXTENSIONS and not should_exclude(f.relative_to(root))]


def write_files(files, output: Path):
    with output.open("w", encoding="utf-8") as out:
        for f in files: out.write(f"{f}\n{clean_content(f)}\n\n")


def main():
    write_files(collect_files(Path.cwd()), Path.cwd() / "project_dump.txt")


if __name__ == "__main__":
    main()
