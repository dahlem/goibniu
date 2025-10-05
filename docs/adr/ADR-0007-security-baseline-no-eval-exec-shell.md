# ADR-0007: Security Baseline — Disallow Dangerous Dynamic Execution and Shell Spawning

## Status
Accepted

## Context
Dynamic code execution and shelling out can introduce exploitable behavior
unless carefully constrained.

## Decision
Disallow `eval()`, `exec()`, and direct shell spawning via `os.system` or
`subprocess.Popen`/`subprocess.call` in application code.

## Consequences
- Positive: Reduces risk surface; easier reasoning about code behavior.
- Negative: Requires safer alternatives (parsers, whitelisting, libraries).

## Rule (optional)
```yaml
goibniu_rule:
  id: ADR-0007
  description: Disallow eval/exec and direct shell spawning
  patterns:
    any: ["eval(", "exec(", "os.system(", "subprocess.Popen(", "subprocess.call("]
    all: []
  paths:
    include: ["**/*.py"]
    exclude: ["tests/**"]
```

## Validation
- `goibniu check-compliance --root .` must pass.
- Any exception must include an approved docs/rfes/RFE-*.md and reference this
  ADR.
