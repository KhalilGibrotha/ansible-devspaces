.PHONY: bootstrap lint syntax-check test smoke docx-renderer-test print-kroki-manifest print-docx-job clean-workspace

ANSIBLE_PLAYBOOK ?= ansible-playbook
ANSIBLE_LINT ?= ansible-lint
PYTHON ?= python3

bootstrap:
	bash ./scripts/devspace-bootstrap.sh

lint:
	$(ANSIBLE_LINT) playbooks/

syntax-check:
	$(ANSIBLE_PLAYBOOK) --syntax-check -i inventories/hosts.ini playbooks/site.yml

# Aggregate target suitable for CI or local verification
# Ensures linting and syntax validation succeed; does not execute the playbook itself.
# To run the playbook, use the separate 'smoke' target.
test: lint syntax-check

smoke:
	$(ANSIBLE_PLAYBOOK) -i inventories/hosts.ini playbooks/site.yml

docx-renderer-test:
	$(PYTHON) -m unittest discover -s tests -p "test_docx_renderer.py"

print-kroki-manifest:
	bash ./scripts/docx-renderer.sh print-kroki

print-docx-job:
	bash ./scripts/docx-renderer.sh print-job

clean-workspace:
	rm -rf .workspace
