# Lint Workflow

Status: Draft
Date: 2026-04-26

## Objective

Review the memory system periodically without making maintenance expensive.

## Suggested pass order

1. Check validity
   - required fields
   - required frontmatter
   - missing sources

2. Check canonicality
   - duplicate records
   - category mismatch

3. Check content quality
   - weak summaries
   - low-value pages
   - copied raw text

4. Check discoverability
   - orphan wiki pages
   - poor linking

5. Check staleness
   - old active decisions
   - outdated project or system state

## Suggested output format

- file path
- rule id
- severity
- problem summary
- recommended fix

## Cadence

- light review weekly
- deeper review monthly

## Rule of restraint

If a lint pass produces many low-value suggestions, tighten the rules. The system should stay useful, not bureaucratic.
