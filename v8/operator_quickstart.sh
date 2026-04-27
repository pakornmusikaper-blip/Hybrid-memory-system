#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEMO_ROOT="/tmp/substrate_operator_pack"

rm -rf "$DEMO_ROOT"
mkdir -p "$DEMO_ROOT"

echo "[1/3] Building demo runtime and persisted mind-state..."
python3 "$REPO_DIR/v7/run_stateful_runtime_demo.py" >/tmp/substrate_operator_pack_demo.json
cp -r /tmp/v7_stateful_runtime_demo/. "$DEMO_ROOT/"

echo "[2/3] Seeding external usage ledger..."
PYTHONPATH="$REPO_DIR" python3 - <<'PY'
from pathlib import Path
from v6.usage_ledger import UsageLedger
root = Path('/tmp/substrate_operator_pack')
ledger = UsageLedger(root / 'usage-ledger.json')
ledger.record('minimax-api', 'MiniMax-M2.7', 0.0008, 'seed-1')
ledger.record('minimax-api', 'MiniMax-M2.7', 0.0004, 'seed-2')
print(root / 'usage-ledger.json')
PY

echo "[3/3] Showing unified operator view..."
python3 "$REPO_DIR/v6/operator_cli.py" "$DEMO_ROOT" full --ledger "$DEMO_ROOT/usage-ledger.json" --request-limit 4 --cost-limit 0.002

echo
echo "Demo root: $DEMO_ROOT"
echo "Try these next:"
echo "  python3 $REPO_DIR/v6/operator_cli.py $DEMO_ROOT status"
echo "  python3 $REPO_DIR/v6/operator_cli.py $DEMO_ROOT usage --ledger $DEMO_ROOT/usage-ledger.json --request-limit 4 --cost-limit 0.002"
echo "  python3 $REPO_DIR/v6/operator_cli.py $DEMO_ROOT full --ledger $DEMO_ROOT/usage-ledger.json --request-limit 4 --cost-limit 0.002"
