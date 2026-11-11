import ast,io,tokenize
from pathlib import Path

EXCLUDED_DIRS={".venv","__pycache__","uv.lock"}
HIDDEN_FILES={".env","README.md","pyproject.toml"}
EXCLUDED_FILES={"python_parser.py","project_dump.txt"}
EXTENSIONS={".py",".toml",".env.example",".gitignore",".csv",".txt",".md"}

def should_exclude(path:Path)->bool:
    return path.name in EXCLUDED_FILES or any(p in EXCLUDED_DIRS for p in path.parts)

def remove_python_docstrings(source:str)->str:
    try: tree=ast.parse(source)
    except SyntaxError: return source
    nodes=(ast.Module,ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)
    ranges={(n.body[0].lineno,n.body[0].end_lineno) for n in ast.walk(tree) if isinstance(n,nodes) and n.body and isinstance(n.body[0],ast.Expr) and isinstance(n.body[0].value,ast.Constant) and isinstance(n.body[0].value.value,str)}
    return "\n".join(line for i,line in enumerate(source.splitlines(),1) if not any(a<=i<=b for a,b in ranges))

def remove_python_comments(source:str)->str:
    lines=source.splitlines()
    try: tokens=tokenize.generate_tokens(io.StringIO(source).readline)
    except (tokenize.TokenError,IndentationError): return source
    comments={t.start[0] for t in tokens if t.type==tokenize.COMMENT}
    return "\n".join(line[:next((i for i,c in enumerate(line) if c=="#"),len(line))].rstrip() if n in comments else line for n,line in enumerate(lines,1))

def clean_content(path:Path)->str:
    text=path.read_text(encoding="utf-8")
    if path.name in HIDDEN_FILES:return "HIDDEN"
    if path.suffix==".py":text=remove_python_comments(remove_python_docstrings(text))
    return "\n".join(line for line in text.splitlines() if line.strip())

def collect_files(root:Path)->list[Path]:
    return sorted(f for f in root.rglob("*") if f.is_file() and (f.suffix in EXTENSIONS or f.name in HIDDEN_FILES) and not should_exclude(f.relative_to(root)))

def write_files(root:Path,files:list[Path],output:Path)->None:
    with output.open("w",encoding="utf-8") as out:
        for f in files:out.write(f"{f.relative_to(root)}\n{clean_content(f)}\n\n")

def main()->None:
    root=Path.cwd()
    write_files(root,collect_files(root),root/"project_dump.txt")

if __name__=="__main__":main()
