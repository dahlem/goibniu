# ADR-0001: Avoid use of eval()

## Status
Accepted

## Context
Using eval() can be dangerous and should be avoided.

## Decision
Do not use Python eval() in application code.

## Consequences
- Positive: Safer execution
- Negative: Might need alternatives

## Rule (optional)
```yaml
goibniu_rule:
  id: ADR-0001
  description: Avoid python eval() in application code
  patterns:
    any: ["eval("]
    all: []
  paths:
    include: ["**/*.py"]
    exclude: ["tests/**"]
```
