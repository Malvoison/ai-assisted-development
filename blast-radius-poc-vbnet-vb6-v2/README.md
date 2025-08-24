# Blast Radius PoC

This proof-of-concept surfaces the **blast radius** of a PR across a .NET solution by:
1. Extracting *public* symbol declarations from changed C# files (Roslyn).
2. Scanning the repo for likely usages (ripgrep).
3. Posting a sticky Markdown table on the PR.

> VB6 support can be added via ctags in a follow‑up; this PoC focuses on .NET first.

## How it works
- **tools/BlastRadius.DotNet**: Roslyn console app. Given a solution path and a list of changed C# files, outputs one JSON record per public symbol.
- **tools/BlastRadius.Report**: Python script using ripgrep to find likely callers and formats a `blast_radius.md` table.
- **.github/workflows/blast-radius.yml**: Runs on each PR and posts the table as a sticky comment.

## Local test
```bash
dotnet build tools/BlastRadius.DotNet/BlastRadius.DotNet.csproj
git diff --name-only origin/main...HEAD -- '*.cs' > changed_cs.txt   # or create manually
dotnet run --project tools/BlastRadius.DotNet/BlastRadius.DotNet.csproj Your.sln changed_cs.txt > symbols.jsonl
python tools/BlastRadius.Report/report.py symbols.jsonl . blast_radius.md
```

## Roadmap
- Include VB6 via universal-ctags + a small post-processor for functions/subs.
- Replace naive ripgrep with Roslyn SymbolFinder to resolve true call sites.
- Add ranking by fan-in and project criticality.
