# Role: Vault Set Fact | ansible-collection-infrastructure

Fetches a HashiCorp Vault secret path and sets its contents as
Ansible facts. Lookups use `no_log: true` to avoid secrets appearing in output.

Subsequent tasks and roles can make use of individual fields, using
the format `{{ <fact_name>.<field> }}`.

In the event you need to fetch multiple paths, re-use this role with 
relevant `vault_set_fact_path`s and `vault_set_fact_name`s.

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
| `vault_set_fact_path` | yes | — | Vault KV secret path, **relative to the engine mount point** |
| `vault_set_fact_name` | yes | — | Name to register as the Ansible fact. Must be a valid identifier (letters, digits, underscores; not starting with a digit) |
| `vault_set_fact_engine_mount_point` | yes | — | Mount point of the KV secrets engine |
| `vault_set_fact_engine_version` | yes | — | KV secrets engine version (`1` or `2`) |
| `vault_set_fact_skip_env_check` | no | `false` | Skip the env var presence assertion. Auth still requires the vars; useful when a caller validates them once up-front |

You can find your engine mount point and version using
`vault secrets list -detailed`; the `Path` column is the mount point,
and a mount with no `version` option is version 1.

Paths are resolved **relative to the mount point**, so `example-kv` +
`app-env/database` becomes `example-kv/app-env/database`.

## Usage

### Fetch one vault path

```yaml
- hosts: localhost
  roles:
    - role: companieshouse.infrastructure.vault_set_fact
      vars:
        vault_set_fact_engine_mount_point: "example-kv"
        vault_set_fact_engine_version: 2
        vault_set_fact_path: "app-env/database"
        vault_set_fact_name: "app_env_database"
  tasks:
    - name: Use Database Secrets
      ansible.builtin.debug:
        msg: "Database running on {{ app_env_database.host }}, under {{ app_env_database.username }}"
```

### Fetching multiple mounts with different KV versions

```yaml
- hosts: localhost
  # group_vars/all.yml (set defaults for KV2)
  #   vault_set_fact_engine_mount_point: "example-kv"
  #   vault_set_fact_engine_version: 2
  tasks:
    - name: Set Database Facts # KV2
      ansible.builtin.include_role:
        name: companieshouse.infrastructure.vault_set_fact
      vars:
        vault_set_fact_path: "app-env/database"
        vault_set_fact_name: "app_env_database"

    - name: Set API Facts # KV1
      ansible.builtin.include_role:
        name: companieshouse.infrastructure.vault_set_fact
      vars:
        vault_set_fact_engine_mount_point: "legacy-kv"
        vault_set_fact_engine_version: 1
        vault_set_fact_path: "app-env/api"
        vault_set_fact_name: "app_env_api"

    - name: Set Cache Facts # KV2
      ansible.builtin.include_role:
        name: companieshouse.infrastructure.vault_set_fact
      vars:
        vault_set_fact_path: "app-env/cache"
        vault_set_fact_name: "app_env_cache"
```

This relies on `include_role` scoping its `vars` to the
included tasks, so use `include_role` rather than
`import_role` when mixing mounts or versions.

## Tips

- **Put secrets for a project within one dedicated Vault path** so
fields like (`{ "username": "...", "password": "...", "host": "..." }`)
are fetched and made available with one lookup.
- **Use `include_role` rather than `import_role`**, when looping or conditionally
calling this role so it evaluates at runtime (and not parse time).
