#!/usr/bin/env python3
from __future__ import annotations

import signal
import sys
from pathlib import Path

from daemon.runtime import SubstrateRuntime

RUNNING = True


def handle_term(signum, frame):
    global RUNNING
    RUNNING = False


signal.signal(signal.SIGTERM, handle_term)
signal.signal(signal.SIGINT, handle_term)


def main():
    root = Path(sys.argv[1])
    config_dir = Path(sys.argv[2])
    cycles = int(sys.argv[3])
    sleep_seconds = int(sys.argv[4])

    runtime = SubstrateRuntime(root, config_dir)
    count = 0
    runtime.log("supervised-runtime:start")
    while RUNNING and count < cycles:
        runtime.tick()
        count += 1
        import time

        time.sleep(sleep_seconds)
    runtime.log("supervised-runtime:stop")


if __name__ == "__main__":
    main()
