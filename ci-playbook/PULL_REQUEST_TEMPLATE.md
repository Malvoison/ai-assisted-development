# Pull Request Template — AI-Assisted Testing

## Summary
<!-- Short description of what this PR changes and why -->


## AI Assistance
- [ ] AI was used for part/all of this PR
- **Models used:** <!-- e.g., Claude 3.5 (ask), GPT-4.1 (review) -->
- **Guidelines version:** <!-- e.g., v1.8 -->
- **Prompts stored:** <!-- link to design/test doc with prompt snippets (if applicable) -->

## Coverage Checklist
<!-- Paste the pre-flight coverage checklist generated from OpenAPI + controller here -->
- [ ] Happy path tests for all operations
- [ ] Auth scenarios (valid, missing, insufficient, expired)
- [ ] Validation (malformed inputs, boundary sizes, type spoofing)
- [ ] Idempotency (PUT/DELETE semantics)
- [ ] Contract checks (response ⇄ OpenAPI schema) for 2xx/4xx/5xx where applicable
- [ ] Upload scenarios (wrong content-type, too large, empty part, bad boundary) — if applicable
- [ ] Concurrency tests — if applicable

## Provenance
- [ ] All new/modified test files include the required header block:
  ```csharp
  /* 
    AI-Assisted: yes
    Source Guidelines: /docs/testing-instructions.md#v1.8
    Template: /tests/Templates/ExistingTestClass.cs
    Target: <ControllerUnderTest>
    Generated: <YYYY-MM-DD>
    Models: ask=<model>, review=<model>
  */
  ```

## OpenAPI / Spec Alignment
- [ ] I reviewed the OpenAPI diff for this PR
- [ ] New/changed operations have corresponding tests
- Link to spec: <!-- e.g., /spec/openapi.json or PR for spec change -->

## Data & Environments
- [ ] Tests do not rely on hard-coded IDs (inputs acquired dynamically)
- [ ] CI executed against multiple scrubbed datasets (matrix): <!-- A / B / C -->
- [ ] Any data assumptions or seed fixtures documented below

## Risks / Notes
<!-- Limitations, follow-ups, or gaps intentionally left for later -->
- ...

## Reviewer Checklist (for code reviewers)
- [ ] Tests reflect guidelines v1.8 (Auth, Validation, Idempotency, Contract, Uploads as applicable)
- [ ] No secrets in code or prompts; tokens handled via helpers
- [ ] Test names and [Trait] tags are clear and filterable
- [ ] Contract assertions target the correct (path, method, status)
- [ ] Negative/abuse cases are present where relevant
- [ ] Changes are small, reviewable, and follow repo conventions
