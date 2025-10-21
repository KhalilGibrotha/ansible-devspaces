.PHONY: bootstrap lint syntax-check test smoke clean-workspace

ANSIBLE_PLAYBOOK ?= ansible-playbook
ANSIBLE_LINT ?= ansible-lint

bootstrap:
	./scripts/clone-repos.sh
	ansible-galaxy install -r requirements.yml --force

lint:
	$(ANSIBLE_LINT) playbooks/

syntax-check:
	$(ANSIBLE_PLAYBOOK) --syntax-check -i inventories/hosts.ini playbooks/site.yml

# Aggregate target suitable for CI or local verification
# Ensures linting and syntax validation succeed before running the sample playbook
# Execution of the playbook itself is optional and can be invoked separately.
test: lint syntax-check

smoke:
	$(ANSIBLE_PLAYBOOK) -i inventories/hosts.ini playbooks/site.yml

clean-workspace:
	rm -rf .workspace
