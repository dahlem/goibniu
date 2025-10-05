
# ADR-0008: Deterministic Analyzers — No Network Calls Inside Analyzer Modules

## Status
Accepted

## Context
Goibniu analyzers (system/component/API) must be **fast** and **deterministic**
so they run reliably in pre‑commit and CI. Network calls introduce flakiness,
non‑reproducible output, and slow checks.

## Decision
Analyzer modules **must not** make network calls:
- `src/goibniu/system.py`
- `src/goibniu/component.py`
- `src/goibniu/api.py`

If a future analyzer needs external data, it must:
1) Fetch it in a **separate, explicit step** (script or CI stage), and
2) Persist results locally under a **versioned** artifact that analyzers read
from (e.g., a JSON snapshot checked into the repo).

## Consequences
**Positive**
- Fast and predictable checks
- Fewer CI flakes and timeouts

**Negative**
- Requires a two‑step pattern when external data is needed (fetch → snapshot)

## Rule (machine‑checkable)
```yaml
goibniu_rule:
  id: ADR-0008
  description: Disallow HTTP clients in analyzer modules
  patterns:
    any: ["requests.", "httpx.", "aiohttp", "urllib.request", "urllib3"]
    all: []
  paths:
    include: [
      "src/goibniu/system.py",
      "src/goibniu/component.py",
      "src/goibniu/api.py"
    ]
    exclude: []
```

## Validation
- `goibniu check-compliance --root .` must pass.
- Analyzer runs should not vary with network availability.
