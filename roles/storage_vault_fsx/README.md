# Role: Storage Vault FSx | ansible-collection-infrastructure

Loads FSx credentials and variables from HashiCorp Vault and exposes them as Ansible facts under this role's prefix. The consuming playbook maps these onto the `storage_fsx_configure` role's inputs.

All Vault lookups use `no_log: true`.

## Requirements

- Ansible `>= 2.15.6`
- `community.hashi_vault` collection (declared in `galaxy.yml` dependencies)
- A HashiCorp Vault server reachable from the control node
- An AppRole with read access to the paths under `storage_vault_fsx_vault_base_path`

## Variables

All variables are prefixed with `storage_vault_fsx_`. Two inputs must be provided in order to build the `storage_vault_fsx_vault_base_path`:

- `storage_vault_fsx_aws_profile`
- `storage_vault_fsx_fsx_name`

The path is constructed in `defaults/main.yml` as:
```
/applications/{{ storage_vault_fsx_aws_profile }}/amzfsx/{{ storage_vault_fsx_fsx_name }}
```

## Environment variables

AppRole authentication requires all three to be exported:
- `ANSIBLE_HASHI_VAULT_ADDR`
- `ANSIBLE_HASHI_VAULT_ROLE_ID`
- `ANSIBLE_HASHI_VAULT_SECRET_ID`

The role checks these are present before attempting any lookups.

## Vault layout

The role reads three KV2 secrets relative to `storage_vault_fsx_vault_base_path`:

| Path | Fields |
|---|---|
| `/config` | `netapp_hostname`, `cifs_server_name`, `dns_servers` (JSON-encoded list) |
| `/credentials` | `fsxadmin_username`, `fsxadmin_password`, `ad_join_username`, `ad_join_password` |
| `/admins` | `domain_admins` (JSON-encoded list) |

Vault field names are unchanged; only Ansible variable names carry the role prefix.

## Facts set

| Fact | Source |
|---|---|
| `storage_vault_fsx_netapp_hostname` | `/config.netapp_hostname` |
| `storage_vault_fsx_cifs_server_name` | `/config.cifs_server_name` |
| `storage_vault_fsx_dns_servers` | `/config.dns_servers` (parsed from JSON) |
| `storage_vault_fsx_netapp_username` | `/credentials.fsxadmin_username` |
| `storage_vault_fsx_netapp_password` | `/credentials.fsxadmin_password` |
| `storage_vault_fsx_dc_admin_user_name` | `/credentials.ad_join_username` |
| `storage_vault_fsx_dc_admin_password` | `/credentials.ad_join_password` |
| `storage_vault_fsx_fsx_domain_admins` | `/admins.domain_admins` (parsed from JSON) |

## Usage

The playbook is responsible for mapping this role's outputs onto the `storage_fsx_configure` role's inputs:

```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: companieshouse.infrastructure.storage_vault_fsx
      tags: [vault]
      vars:
        storage_vault_fsx_aws_profile: "{{ aws_profile }}"
        storage_vault_fsx_fsx_name: "{{ fsx_name }}"
    - role: companieshouse.infrastructure.storage_fsx_configure
      vars:
        storage_fsx_configure_netapp_hostname: "{{ storage_vault_fsx_netapp_hostname }}"
        storage_fsx_configure_netapp_username: "{{ storage_vault_fsx_netapp_username }}"
        storage_fsx_configure_netapp_password: "{{ storage_vault_fsx_netapp_password }}"
        storage_fsx_configure_cifs_server_name: "{{ storage_vault_fsx_cifs_server_name }}"
        storage_fsx_configure_dns_servers: "{{ storage_vault_fsx_dns_servers }}"
        storage_fsx_configure_dc_admin_user_name: "{{ storage_vault_fsx_dc_admin_user_name }}"
        storage_fsx_configure_dc_admin_password: "{{ storage_vault_fsx_dc_admin_password }}"
        storage_fsx_configure_fsx_domain_admins: "{{ storage_vault_fsx_fsx_domain_admins }}"
```

If you're providing local variables (e.g. extra-vars, ansible-vault), then you can skip this role with `--skip-tags vault`
