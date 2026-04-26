# Release Structure

Status: Draft
Date: 2026-04-26

## Goal

Define how the package should be cleaned and shaped before public release.

## Public release requirements

- package navigation must be clear
- examples must be public-safe
- schemas and templates must be internally consistent
- no private or machine-specific artifacts should remain
- the package should be understandable without external hidden context

## Suggested release tiers

### Tier 1. Documentation release
Includes:
- vision
- architecture
- quick start
- schemas
- templates
- lint pack
- examples

### Tier 2. Workflow release
Adds:
- more workflow references
- stronger maintenance guidance
- example adoption stories

### Tier 3. Tooling release
Adds optional scripts or automation only if they clearly improve the package.

## Rule of restraint

Do not publish internal noise just because it exists.
Only keep what helps another user adopt the system well.
