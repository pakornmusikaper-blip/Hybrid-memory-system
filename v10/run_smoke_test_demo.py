#!/usr/bin/env python3
"""
Demo for smoke test.
"""

from __future__ import annotations

import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo))

from v10.smoke_test import run_smoke_test


def main():
    result = run_smoke_test()
    print(f"\nSmoke test: {result['status']}")
    if result['errors']:
        print("Errors:")
        for e in result['errors']:
            print(f"  - {e}")
    if result['warnings']:
        print("Warnings:")
        for w in result['warnings']:
            print(f"  - {w}")
    print("\nAll clear." if result['status'] == 'PASS' else "FAILED.")


if __name__ == '__main__':
    main()
