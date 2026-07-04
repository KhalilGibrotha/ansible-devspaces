#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR/.."

WORK_ROOT_DEFAULT=$(cd .. && pwd)/.docx-work
DOCX_WORK_ROOT="${DOCX_WORK_ROOT:-$WORK_ROOT_DEFAULT}"

mkdir -p "$DOCX_WORK_ROOT" workspace-repos

echo "[prepare-workspace] Prepared workspace-repos at $(cd workspace-repos && pwd)"
echo "[prepare-workspace] Prepared workspace DOCX root at $DOCX_WORK_ROOT"
