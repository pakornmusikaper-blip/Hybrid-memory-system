# Substrate Agent v2 Test Plan

Status: Draft
Date: 2026-04-27

## Goal

Validate that Substrate Agent v2 works correctly before adding more features.

## Test Layers

### 1. Functional Tests

Verify each component works in isolation.

#### Core CLI
- `python -m substrate status`
- `python -m substrate stats`
- `python -m substrate beliefs`
- `python -m substrate growth`
- `python -m substrate bridge`
- `python -m substrate gpu`

#### Growth System
- Belief validation runs
- Pattern recognition runs
- Contradiction detection runs
- Growth summary renders

#### Bridge System
- Query creation works
- Response creation works
- Inbox/outbox stats work
- Intuition listing works

### 2. Scenario Tests

Simulate realistic usage.

#### Scenario A: absorb → belief → growth
1. Create a small fake knowledge-system fixture
2. Absorb new context
3. Verify a belief file is created
4. Run growth summary
5. Check belief confidence/status

#### Scenario B: bridge workflow
1. Send a query
2. Send a response
3. Verify bridge files appear
4. Verify stats update

#### Scenario C: contradiction workflow
1. Create two conflicting beliefs
2. Run contradiction detection
3. Verify contradiction reported

### 3. Long-run / Stability Tests

#### CPU-only loop
- Run background loop for a short window
- Verify no crash
- Verify log files write correctly

#### Resource checks
- Check startup time
- Check memory footprint
- Check model load behavior on CPU-only environment

## Exit Criteria

The system is ready for v2.5 hardening when:
- Core CLI commands run without crashing
- Functional tests pass
- Scenario tests pass
- Known CPU limitations are documented clearly
- Bugs are captured with patches or follow-ups

## Known Risk Areas

- CPU inference may still be too slow for real interactive use
- Model generation paths may need timeout/fallback behavior
- Bridge and growth components may work architecturally but need deeper integration tests

## Output of This Test Pass

1. Test results summary
2. Bug list
3. Bottleneck list
4. v2.5 patch recommendations
