#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR/.."

echo "[bootstrap] Cloning upstream repositories into workspace-repos/"
bash ./scripts/clone-repos.sh

WORK_ROOT_DEFAULT=$(cd .. && pwd)/.docx-work
DOCX_WORK_ROOT="${DOCX_WORK_ROOT:-$WORK_ROOT_DEFAULT}"
mkdir -p "$DOCX_WORK_ROOT"
echo "[bootstrap] Prepared workspace DOCX root at $DOCX_WORK_ROOT"

echo "[bootstrap] Installing Ansible Galaxy roles and collections"
ansible-galaxy install -r requirements.yml --force

echo "[bootstrap] Bootstrap complete."
