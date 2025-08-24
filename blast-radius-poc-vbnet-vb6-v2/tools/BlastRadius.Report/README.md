# BlastRadius.Report (PoC)

Naive usage scanner using ripgrep to approximate "who calls/uses this symbol?" and produce a Markdown table.

## Requirements
- `ripgrep` available in PATH (`rg`)

## Run
```bash
python tools/BlastRadius.Report/report.py symbols.jsonl . blast_radius.md
```


Note: If `vb6_symbols.jsonl` is present, you can concatenate with `.NET` symbols before calling the reporter:

```bash
cat symbols.jsonl vb6_symbols.jsonl > all_symbols.jsonl
python tools/BlastRadius.Report/report.py all_symbols.jsonl . blast_radius.md
```
