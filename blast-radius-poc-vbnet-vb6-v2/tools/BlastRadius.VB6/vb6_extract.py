#!/usr/bin/env python3

"""
BlastRadius.VB6 — extract VB6 symbols via universal-ctags and output JSONL.

Inputs:
  - changed list file (one path per line)
Outputs:
  - vb6_symbols.jsonl (to stdout if -o not provided)

Notes:
  - Requires `universal-ctags` in PATH (package: universal-ctags).
  - Parses .bas/.cls/.frm files listed in changed file list.
  - Emits records compatible with the .NET extractor:
    { lang, kind, name, container, signature, file, line, project, assembly, publicSurface }
"""
import argparse, json, os, subprocess, sys, shlex
from pathlib import Path

VB6_EXTS = {'.bas', '.cls', '.frm'}

def run_ctags(files):
    # Use JSON output; include fields: access (public/private), scope, signature if available
    cmd = ["ctags", "--output-format=json", "--fields=+nksa", "--extras=+q", "--languages=VB"]
    cmd += [str(f) for f in files]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode not in (0,1):  # 1 can happen if no tags found
        print(proc.stderr, file=sys.stderr)
    return proc.stdout.splitlines()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("changed_list", help="Path to file containing changed paths (one per line)")
    ap.add_argument("-o", "--output", help="Output JSONL path (defaults to stdout)")
    args = ap.parse_args()

    changed_path = Path(args.changed_list)
    if not changed_path.exists():
        print(f"Changed list not found: {changed_path}", file=sys.stderr)
        sys.exit(1)

    # Collect VB6 files
    vb_files = []
    for line in changed_path.read_text(encoding="utf-8").splitlines():
        p = line.strip()
        if not p: continue
        ext = Path(p).suffix.lower()
        if ext in VB6_EXTS:
            vb_files.append(Path(p))

    # If nothing to do, write nothing and exit
    if not vb_files:
        if args.output:
            Path(args.output).write_text("", encoding="utf-8")
        sys.exit(0)

    # Run ctags
    lines = run_ctags(vb_files)

    out_fh = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout

    for ln in lines:
        ln = ln.strip()
        if not ln: continue
        try:
            obj = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if obj.get("_type") != "tag":  # skip meta
            continue

        name = obj.get("name")
        file = obj.get("path")
        line = obj.get("line", 0)
        kind = obj.get("kind")  # function, sub, class, const, etc.
        access = obj.get("access")  # public/private
        scope = obj.get("scope", "")
        scopeKind = obj.get("scopeKind", "")
        signature = obj.get("signature", "") or name

        # Normalize kinds a bit
        kind_map = {
            "function": "function",
            "sub": "sub",
            "class": "class",
            "const": "const",
            "property": "property",
            "variable": "variable",
            "method": "method",
        }
        norm_kind = kind_map.get(kind, kind)

        public_surface = True if (access or "").lower() in ("public", "") else False
        container = f"{scopeKind} {scope}".strip() if scope else ""

        record = {
            "lang": "vb6",
            "kind": norm_kind,
            "name": name,
            "container": container,
            "signature": signature,
            "file": file.replace("\\", "/") if file else "",
            "line": line or 0,
            "project": "",      # not resolved for VB6 in this PoC
            "assembly": "",     # n/a
            "publicSurface": public_surface
        }
        out_fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    if args.output:
        out_fh.close()

if __name__ == "__main__":
    main()
