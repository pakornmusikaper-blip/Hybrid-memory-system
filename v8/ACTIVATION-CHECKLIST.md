# Activation Checklist

## Before enabling external

- [ ] API key exported (`MINIMAX_API_KEY`)
- [ ] `runtime-config.example.json` copied to real runtime config
- [ ] `external_enabled` reviewed and set intentionally
- [ ] daily request limit chosen
- [ ] daily cost limit chosen
- [ ] ledger path exists and is writable
- [ ] preflight passes
- [ ] smoke test passes
- [ ] usage dashboard checked after smoke test

## First real activation

- [ ] Start with starter budget
- [ ] Run only 1-2 scenarios
- [ ] Inspect ledger and dashboard
- [ ] Confirm fallback path still works
