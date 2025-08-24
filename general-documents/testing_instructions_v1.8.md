# API Testing Instructions (v1.8)

These guidelines define the required standards, helpers, and patterns for testing our REST APIs.

---

## 1. Authentication (Azure AD B2C)
**Requirement:** All API tests execute with **valid B2C tokens** by default and include explicit **auth‑failure** cases.

**Standard helper:**
```csharp
// B2CAuthHelper.cs (shared test lib)
public static class B2CAuthHelper
{
    public static async Task AttachBearerAsync(HttpClient client, string scope)
    {
        // get cached test token or mint via client credentials / ROPC in B2C test tenant
        var token = await TestTokenCache.GetAsync(scope);
        client.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);
    }
}
```

**Usage in tests:**
```csharp
[Fact, Trait("Area","API"), Trait("Controller","Customers"), Trait("Type","Happy")]
public async Task GetCustomer_Returns200()
{
    await B2CAuthHelper.AttachBearerAsync(Client, "api://app-id/customers.read");
    var res = await Client.GetAsync("/api/customers/123");
    res.EnsureSuccessStatusCode();
}

[Fact, Trait("Type","Auth")]
public async Task GetCustomer_Unauthorized_WithoutToken()
{
    var res = await Client.GetAsync("/api/customers/123");
    Assert.Equal(System.Net.HttpStatusCode.Unauthorized, res.StatusCode);
}
```

---

## 2. Contract Conformance (OpenAPI/Swagger)
**Goal:** Responses conform to the **shared spec** (we publish YAML; internal canonical JSON is the source of truth).

**Standard helper:**
```csharp
// ContractAssert.cs (shared test lib)
public static class ContractAssert
{
    public static void MatchesOpenApi(string path, string method, int statusCode, string jsonBody, OpenApiIndex index)
    {
        // Locate schema for (path, method, status) and validate jsonBody → schema
        var schema = index.GetSchema(path, method, statusCode);
        var result = JsonSchemaValidator.Validate(jsonBody, schema);
        Assert.True(result.IsValid, $"Contract mismatch: {result.ErrorMessage}");
    }
}
```

**Usage in tests:**
```csharp
[Fact, Trait("Type","Contract")]
public async Task GetCustomer_ContractMatches()
{
    await B2CAuthHelper.AttachBearerAsync(Client, "api://app-id/customers.read");

    var res = await Client.GetAsync("/api/customers/123");
    var body = await res.Content.ReadAsStringAsync();

    ContractAssert.MatchesOpenApi("/api/customers/{id}", "get", 200, body, OpenApiIndex.Current);
}
```

---

## 3. Data Independence (no “known IDs”)
**Rule:** Tests must not depend on pre‑known DB IDs. Acquire inputs dynamically.

**Pattern:**
```csharp
private async Task<string> AnyCustomerIdAsync()
{
    await B2CAuthHelper.AttachBearerAsync(Client, "api://app-id/customers.read");
    var res = await Client.GetAsync("/api/customers?take=1");
    res.EnsureSuccessStatusCode();
    var list = JsonNode.Parse(await res.Content.ReadAsStringAsync())!.AsArray();
    return list[0]!["id"]!.GetValue<string>();
}

[Fact]
public async Task GetCustomer_ByDiscoveredId_Works()
{
    var id = await AnyCustomerIdAsync();
    var res = await Client.GetAsync($"/api/customers/{id}");
    res.EnsureSuccessStatusCode();
}
```

---

## 4. Multi‑Database CI Matrix (scrubbed sets)
**Rule:** The suite must run against **≥3 scrubbed databases** in CI to harden against data‑shape drift.

**GitHub Actions (excerpt):**
```yaml
jobs:
  api-tests:
    strategy:
      fail-fast: false
      matrix:
        dataset: [scrubbedA, scrubbedB, scrubbedC]
    env:
      DATASET_NAME: ${{ matrix.dataset }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '8.0.x' }
      - name: Run API tests
        run: dotnet test tests/Api --logger trx
        env:
          ConnectionStrings__ApiDb: ${{ secrets[matrix.dataset] }}
```

---

## 5. Provenance Header (required in every generated test)
```csharp
/* 
  AI-Assisted: yes
  Source Guidelines: /docs/testing-instructions.md#v1.8
  Template: /tests/Templates/ExistingTestClass.cs
  Target: <ControllerUnderTest>
  Generated: 2025-08-24
  Models: ask=<model>, review=<model>
*/
```

**CI check:** PR fails if provenance header or guideline version tag is missing.

---

## 6. Required Sections Per Controller
Each controller’s test file must contain:
- **Happy path** for each operation  
- **Auth** (missing/insufficient/expired token)  
- **Validation** (malformed, boundary sizes, type spoofing)  
- **Idempotency** (PUT/DELETE semantics)  
- **Contract** (schema conformance for 2xx/4xx/5xx as applicable)  
- **Concurrency** (when applicable)  
- **Uploads** (for multipart: wrong content‑type, too large, empty part, bad boundary)  

---

## 7. Prompt Snippets (to standardize generation)

**Pre‑flight coverage map:**
```
Use openapi.json and MyController.cs to produce a checklist of operations,
required/optional params, auth requirements, expected statuses, idempotency
notes, and edge/abuse cases. Output as a Markdown checklist.
```

**Test generation:**
```
Follow docs/testing-instructions.md (v1.8). Use ExistingTestClass.cs as style.
Use B2CAuthHelper for tokens. Use ContractAssert for schema checks.
Acquire IDs dynamically (no hard-coded IDs). Include [Trait] tags and the
provenance header. Cover Auth, Validation, Idempotency, Contract, and Uploads.
```

**Gap auditor:**
```
Given NewTestClass.cs + guidelines v1.8 + ExistingTestClass.cs, list [MISSING] /
[IMPROVE] / [OK] items, propose method names and minimal patches to close gaps.
```
