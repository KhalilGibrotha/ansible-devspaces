#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

TOOLKIT_DIR="${TOOLKIT_DIR:-$REPO_ROOT/workspace-repos/dac-toolkit}"
INPUT_MARKDOWN="${INPUT_MARKDOWN:-$REPO_ROOT/examples/docx/sample-diagram-gallery.md}"
OUTPUT_DOCX="${OUTPUT_DOCX:-$REPO_ROOT/examples/docx/output/sample-diagram-gallery.docx}"
ASSETS_DIR="${ASSETS_DIR:-$REPO_ROOT/examples/docx/output/generated-diagrams}"
REWRITTEN_MARKDOWN="${REWRITTEN_MARKDOWN:-/tmp/rendered-with-kroki.md}"
ORG_YAML="${ORG_YAML:-$REPO_ROOT/examples/docx/org.yaml}"
LOGO_PATH="${LOGO_PATH:-}"
KROKI_URL="${KROKI_URL:-http://127.0.0.1:8000}"
VENV_DIR="${VENV_DIR:-$REPO_ROOT/workspace-repos/.venv-docx-render}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ ! -d "$TOOLKIT_DIR/docx_builder" && -d "$REPO_ROOT/.workspace/dac-toolkit/docx_builder" ]]; then
    TOOLKIT_DIR="$REPO_ROOT/.workspace/dac-toolkit"
fi

if [[ ! -d "$TOOLKIT_DIR/docx_builder" ]]; then
    echo "docx_builder not found at $TOOLKIT_DIR/docx_builder" >&2
    echo "Synchronizing workspace repositories so dac-toolkit is available..." >&2
    bash "$REPO_ROOT/scripts/clone-repos.sh"
fi

if [[ ! -d "$TOOLKIT_DIR/docx_builder" && -d "$REPO_ROOT/.workspace/dac-toolkit/docx_builder" ]]; then
    TOOLKIT_DIR="$REPO_ROOT/.workspace/dac-toolkit"
fi

if [[ ! -d "$TOOLKIT_DIR/docx_builder" ]]; then
    echo "docx_builder is still missing after repository sync." >&2
    echo "Run 'bash ./scripts/devspace-bootstrap.sh' and confirm workspace-repos/dac-toolkit exists." >&2
    exit 1
fi

if [[ ! -f "$INPUT_MARKDOWN" ]]; then
    echo "Input markdown not found: $INPUT_MARKDOWN" >&2
    exit 1
fi

mkdir -p "$(dirname "$OUTPUT_DOCX")" "$ASSETS_DIR" "$VENV_DIR"

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip >/dev/null
python -m pip install --no-cache-dir -e "$TOOLKIT_DIR/docx_builder"

python "$REPO_ROOT/experiments/docx_renderer/render_with_kroki.py" \
  --input-markdown "$INPUT_MARKDOWN" \
  --output-markdown "$REWRITTEN_MARKDOWN" \
  --assets-dir "$ASSETS_DIR" \
  --kroki-url "$KROKI_URL"

docx_args=(--output "$OUTPUT_DOCX")
if [[ -n "$ORG_YAML" && -f "$ORG_YAML" ]]; then
    docx_args+=(--org "$ORG_YAML")
fi
if [[ -n "$LOGO_PATH" && -f "$LOGO_PATH" ]]; then
    docx_args+=(--logo "$LOGO_PATH")
fi

docx-build "$REWRITTEN_MARKDOWN" "${docx_args[@]}"

echo "DOCX written to $OUTPUT_DOCX"
