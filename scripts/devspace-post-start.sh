#!/bin/bash

set -u

log() {
    printf '[devspace-post-start] %s\n' "$*"
}

run_step() {
    local label="$1"
    shift

    log "Starting: ${label}"
    if "$@"; then
        log "Completed: ${label}"
    else
        local rc=$?
        log "WARNING: ${label} failed with exit code ${rc}. Workspace startup will continue."
    fi
}

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR/.."

run_step "Prepare workspace roots" ./scripts/devspace-prepare-workspace.sh
run_step "Clone upstream repositories" ./scripts/clone-repos.sh
run_step "Install Galaxy dependencies" ansible-galaxy install -r requirements.yml --force

log "Post-start bootstrap finished."
