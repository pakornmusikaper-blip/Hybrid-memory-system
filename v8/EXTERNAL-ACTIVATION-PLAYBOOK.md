# External Activation Playbook

## 1. Set API key

```bash
export MINIMAX_API_KEY=your_key_here
```

## 2. Run preflight

```bash
PYTHONPATH=. python3 v8/external_activation_check.py
```

You want all checks to be `ok: true`.

## 3. Run smoke test

```bash
PYTHONPATH=. python3 v8/external_smoke_test.py
```

## 4. Expected outcome

- preflight passes
- adapter health is ok when key/config are present
- result is external path if enabled and configured
- otherwise result safely falls back without crashing

## 5. Safety reminders

- keep `external_enabled` off until preflight passes
- keep budget limits low at first
- inspect ledger and dashboard after each smoke test
