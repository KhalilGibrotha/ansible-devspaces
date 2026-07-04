#!/bin/bash

set -euo pipefail

BOOTSTRAP_LOG=/tmp/devspace-bootstrap.log
BOOTSTRAP_OK=/tmp/devspace-bootstrap.ok
BOOTSTRAP_FAIL=/tmp/devspace-bootstrap.fail
PROJECT_ROOT=/projects/ansible-devspaces
POST_START_SCRIPT="$PROJECT_ROOT/scripts/devspace-post-start.sh"

run_bootstrap() {
    rm -f "$BOOTSTRAP_OK" "$BOOTSTRAP_FAIL"
    : > "$BOOTSTRAP_LOG"

    echo "[container-start] Waiting for project sources at $PROJECT_ROOT" >>"$BOOTSTRAP_LOG"
    for _ in $(seq 1 60); do
        if [[ -f "$POST_START_SCRIPT" ]]; then
            echo "[container-start] Found post-start script" >>"$BOOTSTRAP_LOG"
            break
        fi
        sleep 2
    done

    if [[ ! -f "$POST_START_SCRIPT" ]]; then
        echo "[container-start] Post-start script not found after waiting; skipping automatic bootstrap." >>"$BOOTSTRAP_LOG"
        touch "$BOOTSTRAP_FAIL"
        return 0
    fi

    cd "$PROJECT_ROOT"
    echo "[container-start] Running automatic bootstrap" >>"$BOOTSTRAP_LOG"
    if bash ./scripts/devspace-post-start.sh >>"$BOOTSTRAP_LOG" 2>&1; then
        echo "[container-start] Automatic bootstrap completed successfully" >>"$BOOTSTRAP_LOG"
        touch "$BOOTSTRAP_OK"
    else
        rc=$?
        echo "[container-start] Automatic bootstrap failed with exit code $rc" >>"$BOOTSTRAP_LOG"
        touch "$BOOTSTRAP_FAIL"
    fi
}

run_bootstrap
