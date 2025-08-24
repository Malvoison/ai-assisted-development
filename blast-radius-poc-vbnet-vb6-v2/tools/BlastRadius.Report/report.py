#!/usr/bin/env python3

"""
BlastRadius.Report — usage scan & Markdown generation with VB6 With-desugar.

Inputs:
  1) symbols.jsonl (or merged all_symbols.jsonl)
  2) repo_root
  3) output_md

Behavior:
  - Builds a temporary mirror of VB6 files with With-blocks desugared so that `.Member`
    becomes `<target>.Member` (see with_desugar.py).
  - Uses ripgrep to count occurrences of symbol names across the mirror.
  - Produces a table sorted by fan-in.
"""
import json, os, subprocess, sys, shlex, tempfile, shutil
from collections import Counter
from pathlib import Path

def rg(pattern: str, repo: Path, exclude_file: str):
    cmd = f"rg -n --no-heading -S {shlex.quote(pattern)}"
    proc = subprocess.run(cmd, cwd=str(repo), shell=True, capture_output=True, text=True)
    hits = []
    if proc.returncode in (0,1):  # 0 found, 1 not found
        for line in proc.stdout.splitlines():
            try:
                path, ln, *_ = line.split(":", 2)
            except ValueError:
                continue
            # We cannot reliably map to original path here; paths are relative within mirror
            if exclude_file and os.path.normpath(path) == os.path.normpath(exclude_file):
                continue
            hits.append((path, int(ln)))
    return hits

def main():
    if len(sys.argv) < 4:
        print("Usage: report.py <symbols.jsonl> <repo_root> <output_md>", file=sys.stderr)
        sys.exit(1)
    symbols_jsonl = Path(sys.argv[1])
    repo = Path(sys.argv[2])
    out_md = Path(sys.argv[3])

    # Create VB6 desugared mirror
    vb6_mirror = Path(tempfile.mkdtemp(prefix="vb6_desugar_"))
    try:
        desugar = Path(__file__).parent / "with_desugar.py"
        subprocess.run(["python3", str(desugar), str(repo), str(vb6_mirror)], check=False)
        search_root = vb6_mirror

        # Load symbols
        symbols = []
        with open(symbols_jsonl, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    symbols.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        rows = []
        for s in symbols:
            name = s.get("name","")
            file = s.get("file","")
            project = s.get("project","")
            signature = s.get("signature","")
            if not name: continue

            hits = rg(name, search_root, file)
            files = [h[0] for h in hits]
            counts = Counter(files)
            fanin = sum(counts.values())
            top = ", ".join([f"{p}({c})" for p,c in counts.most_common(5)]) if counts else "—"
            rows.append({
                "symbol": f"{signature}",
                "declFile": file,
                "project": project,
                "callersTop": top,
                "fanin": fanin,
                "notes": "—"
            })

        # Sort by fan-in
        rows.sort(key=lambda r: r["fanin"], reverse=True)

        with open(out_md, "w", encoding="utf-8") as md:
            md.write("### Blast Radius (PoC)\n")
            md.write("| Public Symbol | Declared In | Project | Likely Callers (top files) | Fan-in | Notes |\n")
            md.write("|---|---|---|---|---|---|\n")
            for r in rows:
                md.write(f"| `{r['symbol']}` | `{r['declFile']}` | `{r['project']}` | {r['callersTop']} | {r['fanin']} | {r['notes']} |\n")

    finally:
        shutil.rmtree(vb6_mirror, ignore_errors=True)

if __name__ == "__main__":
    main()
