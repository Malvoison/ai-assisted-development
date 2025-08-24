# Provenance Header CI Check

This document describes how to enforce provenance headers in AI-assisted test files
using GitHub Actions and simple regex checks.

---

## Purpose

All new or modified test files must include a provenance header that records:
- AI-Assisted flag
- Source Guidelines version
- Template reference
- Target (controller under test)
- Generated date
- Models used

**Example required header:**

```csharp
/* 
  AI-Assisted: yes
  Source Guidelines: /docs/testing-instructions.md#v1.8
  Template: /tests/Templates/ExistingTestClass.cs
  Target: CustomersController
  Generated: 2025-08-24
  Models: ask=Claude-3.5, review=GPT-4.1
*/
```

---

## GitHub Actions Workflow

Add the following to `.github/workflows/provenance-check.yml` in your repo:

```yaml
name: Provenance Header Check

on:
  pull_request:
    paths:
      - 'tests/**/*.cs'   # adjust to your test file paths

jobs:
  check-provenance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Get changed test files
        id: changed
        run: |
          git fetch origin ${{ github.base_ref }}
          files=$(git diff --name-only origin/${{ github.base_ref }}...HEAD -- 'tests/**/*.cs')
          echo "files=$files" >> $GITHUB_OUTPUT

      - name: Check provenance headers
        run: |
          failed=0
          for f in ${{ steps.changed.outputs.files }}; do
            echo "Checking $f..."
            if ! grep -q "AI-Assisted:" "$f"; then
              echo "::error file=$f::Missing AI-Assisted provenance header"
              failed=1
            fi
            if ! grep -q "Source Guidelines:" "$f"; then
              echo "::error file=$f::Missing Source Guidelines tag"
              failed=1
            fi
          done
          exit $failed
```

---

## How It Works

1. Runs on every pull request that modifies `tests/**/*.cs`.  
2. Collects changed test files compared to the base branch.  
3. Uses `grep` to verify each file contains at least:  
   - `AI-Assisted:`  
   - `Source Guidelines:`  
4. Fails the job if any required field is missing.  

---

## Stricter Regex Option

You can make the check stricter by ensuring all six required fields exist:

```bash
if ! grep -q "Template:" "$f"; then
  echo "::error file=$f::Missing Template field"
  failed=1
fi
if ! grep -q "Target:" "$f"; then
  echo "::error file=$f::Missing Target field"
  failed=1
fi
if ! grep -q "Generated:" "$f"; then
  echo "::error file=$f::Missing Generated date"
  failed=1
fi
if ! grep -q "Models:" "$f"; then
  echo "::error file=$f::Missing Models field"
  failed=1
fi
```

---

## Recommendation

Start lightweight (just check for `AI-Assisted:` and `Source Guidelines:`).  
If adoption goes smoothly, tighten the regex to require all six fields for full compliance.
