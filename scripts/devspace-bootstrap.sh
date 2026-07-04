#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR/.."

echo "[bootstrap] Preparing workspace roots"
bash ./scripts/devspace-prepare-workspace.sh

echo "[bootstrap] Cloning upstream repositories into workspace-repos/"
bash ./scripts/clone-repos.sh

echo "[bootstrap] Installing Ansible Galaxy roles and collections"
ansible-galaxy install -r requirements.yml --force

echo "[bootstrap] Bootstrap complete."
