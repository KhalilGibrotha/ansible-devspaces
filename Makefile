.PHONY: bootstrap lint syntax-check docx-preflight docx-preflight-all diagram-lint diagram-lint-all docx-render-all docx-render-one test smoke docx-renderer-test kroki-sidecar-test docx-render-local docx-render-local-sample print-kroki-manifest print-docx-job clean-workspace

ANSIBLE_PLAYBOOK ?= ansible-playbook
ANSIBLE_LINT ?= ansible-lint
PYTHON ?= python3
MANIFEST ?= docs/render-manifest.yaml
DOC_ID ?=
DOC_PATH ?= examples/docx/sample-diagram-gallery.md

bootstrap:
	bash ./scripts/devspace-bootstrap.sh

lint:
	$(ANSIBLE_LINT) playbooks/

syntax-check:
	$(ANSIBLE_PLAYBOOK) --syntax-check -i inventories/hosts.ini playbooks/site.yml

docx-preflight:
	$(PYTHON) ./scripts/preflight_docx.py "$(DOC_PATH)"

docx-preflight-all:
	$(PYTHON) ./scripts/docx_manifest.py preflight --manifest "$(MANIFEST)"

diagram-lint:
	$(PYTHON) ./scripts/lint_diagrams.py

diagram-lint-all:
	$(PYTHON) ./scripts/docx_manifest.py lint --manifest "$(MANIFEST)"

# Aggregate target suitable for CI or local verification
# Ensures linting and syntax validation succeed; does not execute the playbook itself.
# To run the playbook, use the separate 'smoke' target.
test: lint syntax-check diagram-lint

smoke:
	$(ANSIBLE_PLAYBOOK) -i inventories/hosts.ini playbooks/site.yml

docx-renderer-test:
	$(PYTHON) -m unittest discover -s tests -p "test_docx_renderer.py"

kroki-sidecar-test:
	$(PYTHON) ./scripts/verify-kroki.py

docx-render-local:
	bash ./scripts/docx-render-local.sh

docx-render-all:
	$(PYTHON) ./scripts/docx_manifest.py render --manifest "$(MANIFEST)"

docx-render-one:
	$(PYTHON) ./scripts/docx_manifest.py render --manifest "$(MANIFEST)" --document-id "$(DOC_ID)"

docx-render-local-sample:
	cp scripts/docx-render-local.env.example .docx-render-local.env
	@echo "# update .docx-render-local.env if needed, then run:"
	@echo "set -a && . ./.docx-render-local.env && set +a && make docx-render-local"

print-kroki-manifest:
	bash ./scripts/docx-renderer.sh print-kroki

print-docx-job:
	bash ./scripts/docx-renderer.sh print-job

clean-workspace:
	rm -rf .workspace
