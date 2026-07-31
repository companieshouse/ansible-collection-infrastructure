# ansible-collection-infrastructure
A collection of Ansible roles used frequently in Companies House infrastructure projects.

## Roles

### Vault

| Role | Description |
|---|---|
| [`vault_set_fact`](roles/vault_set_fact/README.md) | Fetches a HashiCorp Vault secret path and exposes its contents as Ansible facts. |

### Linux

| Role | Description |
|---|---|
| [`linux_ec2_tags`](roles/linux_ec2_tags/README.md) | Validate required EC2 tag-derived inventory variables are set. |
| [`linux_hostname`](roles/linux_hostname/README.md) | Set a Linux host's FQDN from EC2 tag-derived inventory variables. |
| [`linux_python_packages`](roles/linux_python_packages/README.md) | Installs a list of Python packages into a virtualenv using pip. |
| [`linux_reboot`](roles/linux_reboot/README.md) | Reboot a Linux host and wait for it to come back. |
| [`linux_root_rand_pass`](roles/linux_root_rand_pass/README.md) | Set a random, unrecorded password on the root account, if not already set. |

### Storage - WIP Released for Testing within CH Projects

| Role | Description |
|---|---|
| [`storage_data_vol`](roles/storage_data_vol/README.md) | Format and mount a single block device on a Linux host. |
| [`storage_fsx_configure`](roles/storage_fsx_configure/README.md) | Configures an Amazon FSx (NetApp ONTAP) file system. |
| [`storage_fsx_vault`](roles/storage_fsx_vault/README.md) | Loads FSx variables from HashiCorp Vault and sets them as facts (uses `vault_set_fact`). |
| [`storage_iscsi_devices`](roles/storage_iscsi_devices/README.md) | Day 0 iSCSI initiator setup, target discovery and login on a Linux host. |
| [`storage_lvm`](roles/storage_lvm/README.md) | Provision LVM-backed mount points on an EC2 host using EBS `Purpose` tags. |
| [`storage_nfs`](roles/storage_nfs/README.md) | Sets up NFS tools and mounts one or more NFS exports. |

## Requirements

See the individual role READMEs linked above for per-role requirements (control-node Python packages, Ansible collections, and
host-side packages).

## Authors
- [ls-comh](https://github.com/ls-comh)
