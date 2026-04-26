# Cross-Link Sweep

Status: Draft
Date: 2026-04-26

## Purpose

This file captures the intended high-level linking pattern across the package.

## Root navigation flow

- `README.md` should point new users to `PACKAGE-INDEX.md`, `PACKAGE-VISION.md`, `QUICKSTART.md`, and `FIRST-30-MINUTES.md`
- `PACKAGE-INDEX.md` should act as the main navigation hub
- `QUICKSTART.md` should move users toward schemas, templates, and lint review
- `FIRST-30-MINUTES.md` should lead directly into first-use validation

## Quality flow

- `LINT-PACK-V1.md` should point to lint rules, quality standards, common failures, and workflow
- onboarding docs should point users toward lint and quality review before scaling

## Release flow

- `repo/RELEASE-STRUCTURE.md` should pair with `repo/FIRST-GITHUB-RELEASE-SET.md`
- `repo/PUBLISHING-SEQUENCE.md` should be the operational publishing checklist
- `FINAL-RELEASE-MANIFEST.md` should summarize the final release boundary

## Rule

Avoid unnecessary cross-link spam. Prefer a few strong navigational links over many weak ones.
