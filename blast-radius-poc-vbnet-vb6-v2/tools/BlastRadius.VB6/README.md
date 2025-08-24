# BlastRadius.VB6 (PoC)

Extracts VB6 symbols from changed `.bas/.cls/.frm` files using **universal-ctags** and outputs JSONL records compatible with the .NET extractor.

## Requirements
- `universal-ctags` installed on the runner (Ubuntu: `sudo apt-get install -y universal-ctags`).

## Usage
```bash
# given a list of changed files in changed.txt
python tools/BlastRadius.VB6/vb6_extract.py changed.txt -o vb6_symbols.jsonl
```


## Tips & Gotchas (VB6)
- **`With … End With` blocks** obscure the qualifier (e.g., `.Foo` instead of `obj.Foo`). The PoC reporter uses name-based grep,
  so it will still find `Foo`, but may over-report. For higher fidelity, consider enhancing the extractor to track the symbol referenced
  in the `With` header and attribute dotted members to that symbol.
- Ensure files retain `Attribute VB_Name = "ModuleOrClassName"` lines; ctags uses these for better container scoping.
- Event handlers on forms (e.g., `Command1_Click`) should be considered part of the form's public surface for blast‑radius purposes.

### Notes on `With ... End With`

- We rewrite `.Member` to `<target>.Member` using a stack of active `With` targets.
- We intentionally **skip string literals and comments**, so literals like `".Text"` are untouched.
- Nested `With` blocks resolve to the **innermost** target.
- Limitations: default members and late-bound COM calls may still be ambiguous; this heuristic
  greatly improves grep accuracy without a full VB6 type system.
