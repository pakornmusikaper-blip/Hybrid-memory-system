# v4.2 Conscious Wake Policy

Status: Draft
Date: 2026-04-27

## Goal

Make Substrate decide when to wake the conscious layer versus staying silent.

## Core idea

Substrate should not interrupt the conscious layer unless the value of interruption exceeds the cost.

## Wake cost model

### Wake costs
- conscious attention interruption
- context injection overhead
- potential distraction from primary task
- token cost of awareness

### Wake benefits
- critical decisions needing human judgment
- high-confidence insight that changes behavior
- contradictions on high-stakes beliefs
- user-relevant urgency
- proactive value delivery

## Wake conditions

### Should wake
- critical event with high confidence
- strong intuition with actionable insight
- important contradiction requiring human resolution
- urgent correction from external source
- user-related readiness signal

### Should defer
- low-confidence anomalies
- noisy or unstable signals
- already-handled duplicates
- maintenance events
- speculative patterns without actionable value

### Should accumulate
- moderate-confidence signals
- weak but recurring patterns
- unclear contradictions
- batch insights for periodic review

## Accumulation strategy

Instead of waking immediately for moderate signals, accumulate evidence:
- track signal strength over time
- wait for pattern confirmation
- batch similar insights
- deliver periodic summary instead of individual interrupts

## Escalation triggers

Wake immediately if:
- belief confidence drops sharply on high-stakes belief
- repeated failures on critical queue items
- new high-confidence belief contradicts existing high-confidence belief
- user directly queries the substrate
