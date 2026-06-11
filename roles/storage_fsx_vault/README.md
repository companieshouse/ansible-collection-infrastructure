# Role: Storage FSx Vault | ansible-collection-infrastructure

Loads FSx related variables from HashiCorp Vault and sets them as
Ansible facts; intended to be used in conjunction with
`storage_fsx_configure` and makes use of `vault_set_fact` from
this collection.

## Requirements

- Ansible `>= 2.15.6`
- `community.hashi_vault` collection (declared in `galaxy.yml` dependencies)
- A HashiCorp Vault server reachable from the control node
- An AppRole with read access to the paths under `storage_fsx_vault_base_path`

## Environment variables

AppRole authentication requires the following to run:
- `ANSIBLE_HASHI_VAULT_ADDR`
- `ANSIBLE_HASHI_VAULT_ROLE_ID`
- `ANSIBLE_HASHI_VAULT_SECRET_ID`

## Variables and Layout

`storage_fsx_vault_base_path` must be provided, and contain:

| Path | Fields |
|---|---|
| `/configs` | `netapp_hostname`, `cifs_server_name`, `dns_servers` (list), `vserver`, `cifs_domain`, `dc_ou` |
| `/credentials` | `fsxadmin_username`, `fsxadmin_password`, `ad_join_username`, `ad_join_password` |
| `/admins` | `domain_admins` (list) |

Lists must be stored as native Vault lists (e.g. via the API/UI as JSON
arrays), not as JSON-encoded strings.

## Facts set

On success, the role sets the following facts (all as `no_log`):

| Fact | Source | Type |
|---|---|---|
| `storage_fsx_vault_netapp_hostname` | `/configs` → `netapp_hostname` | str |
| `storage_fsx_vault_cifs_server_name` | `/configs` → `cifs_server_name` | str |
| `storage_fsx_vault_dns_servers` | `/configs` → `dns_servers` | list |
| `storage_fsx_vault_vserver` | `/configs` → `vserver` | str |
| `storage_fsx_vault_cifs_domain` | `/configs` → `cifs_domain` | str |
| `storage_fsx_vault_dc_ou` | `/configs` → `dc_ou` | str |
| `storage_fsx_vault_fsxadmin_username` | `/credentials` → `fsxadmin_username` | str |
| `storage_fsx_vault_fsxadmin_password` | `/credentials` → `fsxadmin_password` | str |
| `storage_fsx_vault_ad_join_username` | `/credentials` → `ad_join_username` | str |
| `storage_fsx_vault_ad_join_password` | `/credentials` → `ad_join_password` | str |
| `storage_fsx_vault_domain_admins` | `/admins` → `domain_admins` | list |

## Usage

This role supplies every input `storage_fsx_configure` requires, when invoked,
the vars should be mapped across:

```yaml
- hosts: localhost
  gather_facts: false

  module_defaults:
    group/netapp.ontap.netapp_ontap:
      hostname: "{{ storage_fsx_configure_netapp_hostname }}"
      username: "{{ storage_fsx_configure_netapp_username }}"
      password: "{{ storage_fsx_configure_netapp_password }}"
      https: true
      validate_certs: false
      use_rest: always

  roles:
    - role: companieshouse.infrastructure.storage_fsx_vault
      tags: [vault]
      vars:
        storage_fsx_vault_base_path: "secret/myproject/fsx/myfilesystem"
    - role: companieshouse.infrastructure.storage_fsx_configure
      vars:
        storage_fsx_configure_netapp_hostname: "{{ storage_fsx_vault_netapp_hostname }}"
        storage_fsx_configure_netapp_username: "{{ storage_fsx_vault_fsxadmin_username }}"
        storage_fsx_configure_netapp_password: "{{ storage_fsx_vault_fsxadmin_password }}"
        storage_fsx_configure_vserver: "{{ storage_fsx_vault_vserver }}"
        storage_fsx_configure_cifs_server_name: "{{ storage_fsx_vault_cifs_server_name }}"
        storage_fsx_configure_cifs_domain: "{{ storage_fsx_vault_cifs_domain }}"
        storage_fsx_configure_dns_servers: "{{ storage_fsx_vault_dns_servers }}"
        storage_fsx_configure_dc_admin_user_name: "{{ storage_fsx_vault_ad_join_username }}"
        storage_fsx_configure_dc_admin_password: "{{ storage_fsx_vault_ad_join_password }}"
        storage_fsx_configure_dc_ou: "{{ storage_fsx_vault_dc_ou }}"
        storage_fsx_configure_domain_admins: "{{ storage_fsx_vault_domain_admins }}"
```

If you're providing local vars to `storage_fsx_configure` (e.g.
extra-vars, ansible-vault), you can skip this role using
`--skip-tags vault`.
