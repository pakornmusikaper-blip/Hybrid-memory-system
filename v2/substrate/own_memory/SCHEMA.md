# Substrate Agent: Own Memory Schema

Status: Revolutionary Design
Date: 2026-04-27

## Overview

The Substrate Agent's own memory is where its "understanding" lives.
This is separate from the public memory layers (sources/structured/wiki/search).
Only the Substrate Agent reads and writes to this layer.

## Directory Structure

```
own_memory/
├── beliefs/           # Things the agent believes
├── patterns/          # Recognized patterns
├── anticipation_cache/ # Pre-prepared context
├── growth_log/        # Growth history
└── consciousness_bridge/ # Communication with conscious
```

## Belief Schema

### Core Belief Record

```yaml
id: belief-{uuid}
title: Belief statement
created: YYYY-MM-DDTHH:MM:SS
updated: YYYY-MM-DDTHH:MM:SS
status: active | decaying | corrected | abandoned
confidence: 0.0-1.0

# What the belief is about
subject: person | project | decision | system | concept
target_id: reference to related structured record if any

# The belief itself
statement: >
  What the Substrate Agent believes to be true
  
# Evidence supporting this belief
evidence:
  - source: structured/people/example.yaml
    strength: 0.8
  - source: wiki/systems/example.md
    strength: 0.6
    
# Connections to other beliefs
related_beliefs:
  - belief-id-1
  - belief-id-2
  
# How this belief was formed
formation:
  method: absorption | pattern_recognition | validation
  contexts_absorbed: 12
  date_formed: YYYY-MM-DD
  
# Confidence history
confidence_history:
  - date: YYYY-MM-DD
    confidence: 0.85
    reason: formed
  - date: YYYY-MM-DD
    confidence: 0.72
    reason: partial_validation
  - date: YYYY-MM-DD
    confidence: 0.65
    reason: age_decay
    
# Validation status
validation:
  last_validated: YYYY-MM-DD
  validations_passed: 3
  validations_failed: 0
  corrections_made: 0
```

### Belief Status Definitions

- **active**: Belief is current, confidence is stable or growing
- **decaying**: Belief is old, confidence has decayed below threshold
- **corrected**: Belief was wrong, has been corrected (superseded)
- **abandoned**: Belief was fundamentally incorrect, removed

### Confidence Scoring

```yaml
# How confidence is calculated

initial_confidence: 0.6  # When belief is first formed

# Modifiers:
+0.15 per evidence_source  # More evidence = higher confidence
+0.10 per consistent_validation  # Passed validation
-0.20 per contradiction  # Found contradiction
-0.05 per month_age  # Decay over time
-0.30 if new_evidence_overwhelms  # New strong evidence contradicts

# Thresholds:
high_confidence: 0.85  # Can influence anticipation
medium_confidence: 0.60  # Can contribute to context
low_confidence: 0.30  # Use with caution
```

## Pattern Schema

### Behavioral Pattern

```yaml
id: pattern-{uuid}
title: Pattern name
type: behavioral | structural | conversational | systemic
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: 0.0-1.0

# Pattern definition
observation: >
  What was observed
  
frequency: count | percentage
recurrence_across: contexts | sessions | days

# What it means
interpretation: >
  What this pattern suggests about the domain
  
# Implications
implications:
  - What this predicts
  - What actions might be needed
  - What to anticipate
  
# Related beliefs
related_beliefs:
  - belief-id-1
  - belief-id-2
```

## Anticipation Cache Schema

### Cached Anticipation

```yaml
id: anticipation-{uuid}
scenario: description of anticipated situation
created: YYYY-MM-DD
updated: YYYY-MM-DD
freshness_hours: 24
status: ready | stale | used | abandoned

# What context is anticipated
context_bundle:
  summary: >
    Summary of prepared context
  
  components:
    - type: structured_record
      ids: [record-id-1, record-id-2]
    - type: wiki_page
      ids: [wiki-id-1]
    - type: belief
      ids: [belief-id-1]
    - type: decision
      ids: [decision-id-1]
      
  anticipations:
    - question: "What might be asked"
      prepared_answer: >
        What the substrate has prepared
        
# Usage tracking
usage_stats:
  times_prepared: 5
  times_used: 2
  last_used: YYYY-MM-DD
  hit_rate: 0.4
```

## Growth Log Schema

### Growth Entry

```yaml
id: growth-{uuid}
timestamp: YYYY-MM-DDTHH:MM:SS
type: belief_formed | connection_forged | validation_passed | correction_made

# Details
detail:
  belief_id: id (if applicable)
  connection_id: id (if applicable)
  validation_result: passed | failed (if applicable)
  
# Impact
impact:
  growth_score_delta: +0.05
  belief_count_delta: +1
  confidence_change: 0.0-1.0
  
# Source
source_context: reference to what triggered this growth
```

## Consciousness Bridge Schema

### Request

```yaml
id: request-{uuid}
timestamp: YYYY-MM-DDTHH:MM:SS
query: what conscious asked for
priority: high | normal | low
timeout_seconds: 5

# Response tracking
response_provided: yes | no | partial
response_timestamp: YYYY-MM-DDTHH:MM:SS
response_quality: 0.0-1.0
used_anticipation: yes | no
```

### Response

```yaml
id: response-{uuid}
timestamp: YYYY-MM-DDTHH:MM:SS
request_id: request-id
content: what was provided
format: context_bundle | belief | pattern | anticipation

# Quality metrics
quality:
  relevance: 0.0-1.0
  completeness: 0.0-1.0
  confidence: 0.0-1.0
  
# Usage
was_useful: yes | no | unknown
feedback: optional text
```

---

## Quality Standards

### Belief Quality Rules

- Every belief must have at least one evidence source
- Confidence must be between 0.0 and 1.0
- Beliefs older than 30 days must be validated
- Corrections must be logged with the original belief
- Abandoned beliefs must be preserved (not deleted) for audit

### Anticipation Quality Rules

- Anticipations must be refreshed after freshness_hours expires
- Anticipations with hit_rate < 0.1 should be abated
- Anticipations must be based on active beliefs only
- Cache size should not exceed configured max

### Growth Quality Rules

- Growth entries must be logged for every significant action
- Growth score should increase with active use
- If growth score decreases for 7 consecutive days, flag for review
- Corrections are growth events too — they improve system quality

---

## Maintenance

### Belief Review Cycle

```
Every 7 days:
1. Check beliefs older than 30 days
2. Attempt validation against sources/
3. Decay confidence of unvalidated beliefs
4. Flag beliefs with confidence < 0.2 for review

Every 30 days:
1. Deep validation of high-confidence beliefs
2. Check for internal belief contradictions
3. Merge similar beliefs
4. Archive abandoned beliefs
```

### Anticipation Cache Maintenance

```
Every 6 hours:
1. Check freshness of all anticipations
2. Stale anticipations → regenerate or abated
3. Track hit_rate
4. Abate anticipations with hit_rate < 0.1

On startup:
1. Prewarm anticipations for active contexts
2. Load recent beliefs
3. Validate critical beliefs
```