# Operator Playbook

## Fastest path

```bash
cd /home/pakorn/.openclaw/workspace/hybrid-memory-system
bash v8/operator_quickstart.sh
```

This will:
1. build a demo runtime
2. seed persisted memory files
3. seed external usage ledger
4. show the unified operator view

## Core commands

### Full operator view
```bash
python3 v6/operator_cli.py /tmp/substrate_operator_pack full \
  --ledger /tmp/substrate_operator_pack/usage-ledger.json \
  --request-limit 4 \
  --cost-limit 0.002
```

### Runtime + mind-state only
```bash
python3 v6/operator_cli.py /tmp/substrate_operator_pack status
```

### External usage only
```bash
python3 v6/operator_cli.py /tmp/substrate_operator_pack usage \
  --ledger /tmp/substrate_operator_pack/usage-ledger.json \
  --request-limit 4 \
  --cost-limit 0.002
```

## What you should see

- runtime alive/degraded/critical
- queue state
- belief counts and stages
- concept counts and coherence
- cognition mode distribution and wake ratio
- reflection summary
- external usage totals and provider breakdown
