#!/bin/bash

set -euo pipefail

NAMESPACE="${NAMESPACE:-devspaces}"
WORKSPACE_PVC="${WORKSPACE_PVC:-}"
WORKSPACE_MOUNT_PATH="${WORKSPACE_MOUNT_PATH:-/workspace}"
ANSIBLE_REPO_DIR="${ANSIBLE_REPO_DIR:-$WORKSPACE_MOUNT_PATH/ansible-devspaces}"
TOOLKIT_DIR="${TOOLKIT_DIR:-$WORKSPACE_MOUNT_PATH/dac-toolkit}"
INPUT_MARKDOWN="${INPUT_MARKDOWN:-$WORKSPACE_MOUNT_PATH/content/docs/sample.md}"
OUTPUT_DOCX="${OUTPUT_DOCX:-$WORKSPACE_MOUNT_PATH/content/exports/sample.docx}"
ASSETS_DIR="${ASSETS_DIR:-$WORKSPACE_MOUNT_PATH/content/exports/generated-diagrams}"
REWRITTEN_MARKDOWN="${REWRITTEN_MARKDOWN:-/tmp/rendered-with-kroki.md}"
ORG_YAML="${ORG_YAML:-}"
LOGO_PATH="${LOGO_PATH:-}"
KROKI_URL="${KROKI_URL:-http://kroki:8000}"
JOB_NAME="${JOB_NAME:-docx-render}"
JOB_TIMEOUT="${JOB_TIMEOUT:-600s}"
PYTHON_IMAGE="${PYTHON_IMAGE:-python:3.13-slim}"
KROKI_IMAGE="${KROKI_IMAGE:-yuzutech/kroki:0.28.0}"
KUBE_BIN="${KUBE_BIN:-oc}"

usage() {
    cat <<'EOF'
Usage: ./scripts/docx-renderer.sh <command>

Commands:
  print-kroki   Print the Kroki deployment/service manifest
  apply-kroki   Apply the Kroki deployment/service manifest
  print-job     Print the DOCX render Job manifest
  run-job       Apply the DOCX render Job manifest
  wait-job      Wait for the DOCX render Job to complete
  logs-job      Stream logs from the DOCX render Job
  delete-job    Delete the DOCX render Job
EOF
}

print_kroki() {
    cat <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kroki
  namespace: ${NAMESPACE}
  labels:
    app.kubernetes.io/name: kroki
    app.kubernetes.io/part-of: ansible-devspaces
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: kroki
  template:
    metadata:
      labels:
        app.kubernetes.io/name: kroki
    spec:
      containers:
        - name: kroki
          image: ${KROKI_IMAGE}
          ports:
            - containerPort: 8000
              name: http
          readinessProbe:
            httpGet:
              path: /health
              port: http
          livenessProbe:
            httpGet:
              path: /health
              port: http
---
apiVersion: v1
kind: Service
metadata:
  name: kroki
  namespace: ${NAMESPACE}
spec:
  selector:
    app.kubernetes.io/name: kroki
  ports:
    - name: http
      port: 8000
      targetPort: http
EOF
}

print_job() {
    if [[ -z "${WORKSPACE_PVC}" ]]; then
        echo "WORKSPACE_PVC is required for print-job and run-job." >&2
        exit 1
    fi

    cat <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: ${JOB_NAME}
  namespace: ${NAMESPACE}
  labels:
    app.kubernetes.io/name: docx-render
    app.kubernetes.io/part-of: ansible-devspaces
spec:
  backoffLimit: 0
  ttlSecondsAfterFinished: 3600
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: renderer
          image: ${PYTHON_IMAGE}
          workingDir: ${ANSIBLE_REPO_DIR}
          command:
            - /bin/bash
            - -lc
            - |
              set -euo pipefail
              mkdir -p "$(dirname "${OUTPUT_DOCX}")" "${ASSETS_DIR}"
              python -m pip install --no-cache-dir "${TOOLKIT_DIR}/docx_builder"
              python "${ANSIBLE_REPO_DIR}/experiments/docx_renderer/render_with_kroki.py" \\
                --input-markdown "${INPUT_MARKDOWN}" \\
                --output-markdown "${REWRITTEN_MARKDOWN}" \\
                --assets-dir "${ASSETS_DIR}" \\
                --kroki-url "${KROKI_URL}"
              docx_args=(--output "${OUTPUT_DOCX}")
              if [[ -n "${ORG_YAML}" ]]; then
                docx_args+=(--org "${ORG_YAML}")
              fi
              if [[ -n "${LOGO_PATH}" ]]; then
                docx_args+=(--logo "${LOGO_PATH}")
              fi
              docx-build "${REWRITTEN_MARKDOWN}" "${docx_args[@]}"
          volumeMounts:
            - name: workspace
              mountPath: ${WORKSPACE_MOUNT_PATH}
      volumes:
        - name: workspace
          persistentVolumeClaim:
            claimName: ${WORKSPACE_PVC}
EOF
}

case "${1:-}" in
    print-kroki)
        print_kroki
        ;;
    apply-kroki)
        print_kroki | "$KUBE_BIN" apply -f -
        ;;
    print-job)
        print_job
        ;;
    run-job)
        print_job | "$KUBE_BIN" apply -f -
        ;;
    wait-job)
        "$KUBE_BIN" -n "$NAMESPACE" wait --for=condition=complete "job/${JOB_NAME}" --timeout="$JOB_TIMEOUT"
        ;;
    logs-job)
        "$KUBE_BIN" -n "$NAMESPACE" logs "job/${JOB_NAME}" --follow
        ;;
    delete-job)
        "$KUBE_BIN" -n "$NAMESPACE" delete job "${JOB_NAME}" --ignore-not-found
        ;;
    *)
        usage
        exit 1
        ;;
esac
