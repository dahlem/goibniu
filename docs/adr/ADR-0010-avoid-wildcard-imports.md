# ADR-0010: Avoid Wildcard Imports

## Status
Accepted

## Context
Wildcard imports (`from X import *`) make dependencies opaque, hinder static
analysis, and confuse both agents and humans.

## Decision
Avoid `from ... import *` across the codebase.

## Consequences
- Positive: Clearer dependencies; easier analysis; fewer namespace collisions.
- Negative: Slightly more verbose imports.

## Rule (optional)
```yaml
goibniu_rule:
  id: ADR-0010
  description: Avoid wildcard imports
  patterns:
    any: ["import *"]
    all: []
  paths:
    include: ["**/*.py"]
    exclude: ["tests/**"]
