# ADR-0006: RFE (Request for Engineering) Required for ADR Conflicts

## Status
Accepted

## Context
Architecture evolves. When a proposed change contradicts an ADR, we need a
human-in-the-loop process.

## Decision
If a change violates an ADR:
1) Stop implementation
2) Create an RFE using `goibniu generate-rfe ADR-XXXX "<short reason>"`
3) Obtain human review/approval (update ADRs if needed) before continuing

## Consequences
- Positive: Transparent decision evolution; less accidental erosion of design.
- Negative: Adds a step when challenging existing decisions.
