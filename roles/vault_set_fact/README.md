# Role: Vault Set Fact | ansible-collection-infrastructure

Fetches a HashiCorp Vault secret path and exposes its contents as
Ansible facts.

Lookups use `no_log: true` to avoid secrets appearing in output.

Subsequent tasks and roles can then make use of individual fields, using
the format `{{ <fact_name>.<field> }}`.

In the event you need to fetch multiple paths, re-use this role with 
different `vault_set_fact_path`s and `vault_set_fact_name`s.

## Requirements

- Ansible `>= 2.15.6`
- `community.hashi_vault` collection (declared in `galaxy.yml` dependencies)
- A HashiCorp Vault server reachable from the control node
- An AppRole with read access to a specific vault path

AppRole requires the following:
- `ANSIBLE_HASHI_VAULT_ADDR`
- `ANSIBLE_HASHI_VAULT_ROLE_ID`
- `ANSIBLE_HASHI_VAULT_SECRET_ID`

To skip this presence check (auth itself still requires the vars), set
`vault_set_fact_skip_env_check` to `true`.

## Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `vault_set_fact_path` | yes | — | Vault KV2 path |
| `vault_set_fact_name` | yes | — | Name to register as the Ansible fact. Must be a valid identifier (letters, digits, underscores; not starting with a digit) |
| `vault_set_fact_skip_env_check` | no | `false` | Skip the env var presence assertion. Auth still requires the vars; useful when a caller validates them once up-front |

## Usage

### Fetch one vault path

```yaml
- hosts: localhost
  roles:
    - role: companieshouse.infrastructure.vault_set_fact
      vars:
        vault_set_fact_path: "secret/app-env/database"
        vault_set_fact_name: "app_env_database"
  tasks:
    - name: Use Database Secrets
      ansible.builtin.debug:
        msg: "Database running on {{ app_env_database.host }}, under {{ app_env_database.username }}"
```

### Fetch multiple vault paths

Include the role once per path:

```yaml
- hosts: localhost
  tasks:
    - name: Set Database Facts
      ansible.builtin.include_role:
        name: companieshouse.infrastructure.vault_set_fact
      vars:
        vault_set_fact_path: "secret/app-env/database"
        vault_set_fact_name: "app_env_database"

    - name: Set API Facts
      ansible.builtin.include_role:
        name: companieshouse.infrastructure.vault_set_fact
      vars:
        vault_set_fact_path: "secret/app-env/api"
        vault_set_fact_name: "app_env_api"

    - name: Use Secrets
      ansible.builtin.debug:
        msg: "Database running on {{ app_env_database.host }}, using API token {{ app_env_api.token[:4] }}"
```

### Calling from another role

If you use `vault_set_fact` inside another role with its own env var
validation, set `vault_set_fact_skip_env_check: true` to avoid repeating
validation on every call:

```yaml
- name: Validate Vault AppRole auth env vars are present
  ansible.builtin.assert:
    # env var checks done up-front

- name: Fetch first bundle
  ansible.builtin.include_role:
    name: companieshouse.infrastructure.vault_set_fact
  vars:
    vault_set_fact_path: "{{ base_path }}/config"
    vault_set_fact_name: "config_facts"
    vault_set_fact_skip_env_check: true

- name: Fetch second bundle
  ansible.builtin.include_role:
    name: companieshouse.infrastructure.vault_set_fact
  vars:
    vault_set_fact_path: "{{ base_path }}/credentials"
    vault_set_fact_name: "credential_facts"
    vault_set_fact_skip_env_check: true
```

## Tips

- **Put secrets for a project within one dedicated Vault path** so
fields like (`{ "username": "...", "password": "...", "host": "..." }`)
are fetched and made available with one lookup.
- **Use `include_role` rather than `import_role`**, when looping or conditionally
calling this role so it evaluates at runtime (and not parse time).
