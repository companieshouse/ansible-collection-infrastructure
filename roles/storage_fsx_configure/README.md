# Role: Storage FSx Configure | ansible-collection-infrastructure

Configures an [Amazon FSx (NetApp ONTAP)](https://aws.amazon.com/fsx/netapp-ontap/)
file system including:
- DNS
- CIFS server with encrypted DC connections to Active Directory
- domain admin user reconciliation (fsxadmin role)

## Requirements

- Ansible `>= 2.15.6`
- Python: `requests` and `netapp-lib`
- Networking: Control node <-> FSx management, SVM <-> AD
- AD account with Computer Object creation rights for the OU

Collection dependencies (`community.hashi_vault`, `netapp.ontap`) as declared
in this collection's `galaxy.yml`.

## Variables

All inputs are required and validated via `meta/argument_specs.yml`; the
role will refuse to run with anything missing. All are supplied by
`storage_fsx_vault` when the two roles are used together.

| Variable | Type | Description |
|---|---|---|
| `storage_fsx_configure_netapp_hostname` | str | FSx management endpoint hostname (ONTAP REST API) |
| `storage_fsx_configure_netapp_username` | str | fsxadmin username for the cluster |
| `storage_fsx_configure_netapp_password` | str | fsxadmin password for the cluster |
| `storage_fsx_configure_vserver` | str | Name of the storage VM to configure |
| `storage_fsx_configure_cifs_server_name` | str | NetBIOS-style name for the CIFS computer object in AD |
| `storage_fsx_configure_cifs_domain` | str | Active Directory domain to join |
| `storage_fsx_configure_dns_servers` | list | DNS servers for the SVM; must be non-empty |
| `storage_fsx_configure_dc_admin_user_name` | str | AD account with rights to join computers to the domain |
| `storage_fsx_configure_dc_admin_password` | str | Password for the AD join account |
| `storage_fsx_configure_dc_ou` | str | DN of the OU where the CIFS computer object lives |
| `storage_fsx_configure_domain_admins` | list | Domain usernames (sAMAccountName) to grant the fsxadmin role |

## Usage

`storage_fsx_vault` supplies every input this role requires; unless
you are supplying local vars, these must be mapped across e.g.

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

All vars are expected, and the role will not proceed if one is missing.

To use this role without `storage_fsx_vault`, use tag `--skip-tags vault`
and supply all variables locally e.g. extra-vars, group_vars, ansible-vault. 

## CIFS server renames

The role won't rename an existing CIFS server. To run this with a new name,
get rid of the old AD computer object first.
