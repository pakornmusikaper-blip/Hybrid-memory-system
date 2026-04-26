# Example Lint Finding

Rule: R004
Severity: Error
Paths:
- structured/decisions/example-a.yaml
- structured/decisions/example-b.yaml

## Problem

Two records appear to act as canonical homes for the same decision.

## Why it matters

Future answers may become inconsistent if multiple records compete as the source of truth.

## Recommended fix

Choose one canonical record, merge or archive the other, and add links instead of duplication.
