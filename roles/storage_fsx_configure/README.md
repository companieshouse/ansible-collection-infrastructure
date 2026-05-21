# Role: Storage FSx Configure | ansible-collection-infrastructure

Configures an [Amazon FSx for NetApp ONTAP](https://aws.amazon.com/fsx/netapp-ontap/)
file system:
DNS,
AD-joined CIFS server with encrypted DC connections,
and domain admin user reconciliation.

## Requirements

- Ansible `>= 2.15.6`
- Python: `requests`, `netapp-lib`
- Control node must reach the FSx management endpoint; the SVM must reach AD
- AD account with rights to create computer objects in the target OU

Collection dependencies (`community.hashi_vault`, `netapp.ontap`) are declared in `galaxy.yml`.

## Variables

All variables are prefixed with `storage_fsx_configure_`. Defined in [`meta/argument_specs.yml`](meta/argument_specs.yml). View with:
```
ansible-doc -t role companieshouse.infrastructure.storage_fsx_configure
```

Required:
- `storage_fsx_configure_netapp_hostname`
- `storage_fsx_configure_netapp_username`
- `storage_fsx_configure_netapp_password`
- `storage_fsx_configure_vserver`
- `storage_fsx_configure_cifs_server_name`
- `storage_fsx_configure_cifs_domain`
- `storage_fsx_configure_dns_servers`
- `storage_fsx_configure_dc_admin_user_name`
- `storage_fsx_configure_dc_admin_password`
- `storage_fsx_configure_dc_ou`
- `storage_fsx_configure_fsx_domain_admins`

## Usage

The `storage_vault_fsx` role sets outputs under its own prefix, which the playbook then maps to this role's inputs:

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

Without the `storage_vault_fsx` role, you need to supply variables yourself e.g. extra-vars, group_vars, ansible-vault. The storage_fsx_configure argument-spec validation will fail loudly if anything is missing.


## CIFS server renames

The role won't rename an existing CIFS server. To rename, clean up the old object in AD, then
set your desired `storage_fsx_configure_cifs_server_name`.
