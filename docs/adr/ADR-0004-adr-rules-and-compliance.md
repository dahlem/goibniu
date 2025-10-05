# ADR-0004: Machine‑Checkable ADR Rules via `goibniu_rule`

## Status
Accepted

## Context
Some decisions are amenable to static checks (e.g., forbidden calls,
anti‑patterns). Encoding those directly in ADRs allows automated guardrails.

## Decision
Use a fenced YAML block with the `goibniu_rule` key inside ADRs to define
machine-checkable policies. Enforce with `goibniu check-compliance` locally and
in CI.

## Consequences
- Positive: Decisions become enforceable; reduced drift.
- Negative: Rules are substring/regex-like; nuanced design rules may still
  require human review.

*(No rule here—the ADR explains the mechanism.)*
