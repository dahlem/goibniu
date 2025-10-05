# ADR-0005: Enforce API Correctness with OpenAPI + Static Client Checks

## Status
Accepted

## Context
A frequent failure mode with AI assistants is **hallucinated endpoints** or
missing required params/body. We need a protective check.

## Decision
- Keep OpenAPI specs in `.ai-context/contracts/`
- Run `goibniu check-api` in CI and locally/pre-commit
- Block merges that violate documented endpoints or required params/body

## Consequences
- Positive: Stops most API call hallucinations; keeps contracts as a source of
  truth.
- Negative: Requires maintaining OpenAPI specs; false positives may occur if
  URLs are overly dynamic.

*(No rule here—enforced via `goibniu check-api` step.)*
