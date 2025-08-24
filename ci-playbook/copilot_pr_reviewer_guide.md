# Getting the Most Out of GitHub Copilot Reviewer (One‑Pager)

Use this guide to “steer” Copilot so its PR feedback aligns with your team’s standards—without any private betas or special org settings.

---

## What Copilot Actually Reads
Copilot forms its review from **(a)** files in the PR, **(b)** the **PR description + comments**, and **(c)** **repo docs** it can see. Treat these as your levers.

---

## Goals for Copilot on Every PR
- Catch **spec/API drift**, **tests/coverage gaps**, **security & secrets**, **breaking changes**, and **style/consistency**.
- Produce comments that reviewers can act on immediately (paths, lines, diffs).

---

## 10 Practical Moves (General, not just tests)

1) **Pin your house rules in the repo**  
   Put short, explicit standards in `/docs/` and reference them by link and version (e.g., *“Coding Standards v2.1”*, *“API Guidelines v1.4”*). Short > verbose.

2) **Make the PR body a checklist prompt**  
   Include a concise checklist that mirrors your rules (design impact, API changes, perf risks, security items). Copilot will follow it if it’s visible.

3) **Summarize intent + scope first**  
   Two–three lines: *“Refactors cache layer; no public API changes; target latency P50 –10%.”* Copilot uses this to weigh risks.

4) **Surface the blast radius**  
   Add *“Impacted modules: cache, billing, orders.”* Copilot is better at spotting missing changes in those areas.

5) **Add a simple “Risk & Review focus” section**  
   Bullet 3–5 things you want scrutiny on: *“thread safety in CacheStore”*, *“cursor pagination edge cases”*. Copilot will echo and check them.

6) **Use conventional titles**  
   `feat:`, `fix:`, `refactor:`, `perf:`—this helps Copilot (and humans) set expectations for the type of review.

7) **Prefer many small PRs**  
   Copilot is best on narrow, cohesive diffs. Split feature + tests + docs if needed but keep each PR logically complete.

8) **Let CI leave “stage whispers”**  
   Run format/analyzers, spec drift checks, secret scans, size labeler, etc. Copilot sees the comments/logs and amplifies them in its review.

9) **Name things predictably**  
   Consistent traits/annotations, config keys, and folder names make it easier for Copilot to spot omissions (e.g., missing counterpart files).

10) **Link the source of truth**  
   If there’s a design doc, ticket, or spec PR, link it. Copilot can infer mismatches when the doc is in reach.

---

## PR Template (General Purpose)
Copy into `.github/PULL_REQUEST_TEMPLATE.md` or paste into the PR body.

```markdown
## Summary
<!-- What changed and why (2–3 lines). -->

## Scope / Blast Radius
- Modules: <!-- e.g., cache, billing -->
- Public API changed: yes/no
- Migrations: yes/no

## Review Focus (risk areas)
- <!-- e.g., thread safety in CacheStore; pagination edge cases -->

## Checklist
- [ ] Docs updated or N/A
- [ ] Public API noted (changelog/SDK docs) or N/A
- [ ] Performance impact considered (baseline vs. after) or N/A
- [ ] Security: no secrets, authz unchanged, input validation intact
- [ ] Telemetry & errors: logs/metrics/alerts updated or N/A
- [ ] Tests added/updated (unit/integration/e2e) or N/A
```
> Tip: Start the PR with: *“Copilot, review for compliance with /docs/coding-standards.md#v2.1 and the checklist below.”*

---

## Repo Hygiene That Improves Copilot
- **Short standards**: `docs/coding-standards.md`, `docs/api-guidelines.md`, `docs/perf-budget.md`, `docs/security.md`.  
- **CODEOWNERS** to route reviews automatically.  
- **EditorConfig + analyzers** so Copilot’s nitpicks are handled by tools.  
- **Changelog** (`CHANGELOG.md`) so public API changes are obvious.

---

## Non‑Testing Use Cases Copilot Is Great At
- **Public API diffs**: ask it to enumerate breaking changes and downstream impact.
- **Migration safety**: highlight deleted/renamed symbols and suggest deprecation shims.
- **Perf awareness**: call out new allocations, sync-over-async, or hot-path logging.
- **Security review**: look for unvalidated inputs, widened access, plaintext secrets.
- **Observability**: verify key paths emit metrics/logs and error handling is consistent.
- **Documentation drift**: point out README or sample code mismatches after changes.

---

## Anti‑Patterns (Avoid)
- Giant PRs with mixed concerns.  
- Vague PR bodies (“misc fixes”).  
- Burying the checklist in a linked doc—paste it inline.  
- Rules that are essays—Copilot follows bullets, not novellas.

---

## Troubleshooting
- **Copilot missed something obvious**: tighten the checklist item (*“All new endpoints must include error mapping table”*).  
- **No comments from Copilot**: ensure Copilot is added as a reviewer and the PR is public to the bot (some orgs restrict bot access).  
- **Generic feedback**: move critical rules into the PR body and name the files/paths explicitly.

---

## Quick Starter Checklist (copy/paste to your repo)
- [ ] Add `/docs/coding-standards.md` (short, versioned).  
- [ ] Add `/docs/api-guidelines.md` (short, versioned).  
- [ ] Install PR template above.  
- [ ] Turn on CI checks (format/analyzers, secret scan, size label, linkcheck).  
- [ ] Use conventional titles and small PRs.  
- [ ] In each PR, include *Summary • Scope • Review Focus • Checklist*.  
