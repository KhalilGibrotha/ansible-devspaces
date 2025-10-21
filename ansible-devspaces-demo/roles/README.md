# Ansible Roles Documentation

This directory contains Ansible roles that are used in the playbooks of this project. Each role is designed to encapsulate specific tasks and configurations, making it easier to manage and reuse code across different playbooks.

## Role Structure

Each role typically includes the following directories:

- **tasks/**: Contains the main tasks for the role, defined in YAML files.
- **handlers/**: Contains handlers that can be called by tasks to respond to events.
- **templates/**: Contains Jinja2 templates that can be used to generate configuration files.
- **files/**: Contains static files that can be deployed to the target hosts.
- **vars/**: Contains variable files that define role-specific variables.
- **defaults/**: Contains default variables for the role, which can be overridden by playbook variables.

## Usage

To use a role in a playbook, include it in the `roles` section of the playbook YAML file. For example:

```yaml
- hosts: all
  roles:
    - role_name
```

Replace `role_name` with the name of the role you wish to use.

## Contribution

If you wish to contribute to this project, please follow the guidelines outlined in the main README.md file. Ensure that your roles are well-documented and tested before submitting a pull request.
