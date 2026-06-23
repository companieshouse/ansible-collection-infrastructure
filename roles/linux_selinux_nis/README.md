# Role: Linux SELinux NIS | ansible-collection-infrastructure

Enables the `nis_enabled` SELinux boolean persistently. Required on RHEL-like
hosts that need to talk to NIS, or for some NFS/Kerberos configurations that
SELinux blocks by default.

## Requirements

- Ansible `>= 2.15.6`
- `ansible.posix` collection
- SELinux installed and in enforcing or permissive mode
- `libselinux-python` / `python3-libselinux` (present by default on RHEL-like OS' with SELinu)

## Usage

```yaml
- hosts: my_servers
  roles:
    - role: companieshouse.infrastructure.linux_selinux_nis
```
