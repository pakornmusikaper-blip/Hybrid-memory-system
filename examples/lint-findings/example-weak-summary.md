# Example Lint Finding

Rule: R007
Severity: Warning
Path: structured/systems/example-memory-system.yaml

## Problem

The summary is too vague to explain the durable meaning of the record.

## Why it matters

The record may still be found, but the summary does not help an agent quickly understand why it exists.

## Recommended fix

Rewrite the summary to state what the system is and why it matters.
