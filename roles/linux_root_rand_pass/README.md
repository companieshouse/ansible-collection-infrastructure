# Role: Linux Root Rand Pass | ansible-collection-infrastructure

Sets a random 32-character password on the root account if one is not
already set. This satisfies CIS benchmarks that require root to have a
password set, while ensuring it remains a no-knowledge credential.

Please be careful with this one, the password cannot be recovered.

## Requirements

- Ansible `>= 2.15.6`
- Target host must have `/etc/shadow` (standard on Linux)

## Warning

Only apply this role when you have confirmed alternative access to the
host (sudo via a configured user, SSH/SSM access, cloud provider console,
etc.). The password cannot be retrieved after it is set.

## Usage

```yaml
- hosts: my_servers
  roles:
    - role: companieshouse.infrastructure.linux_root_rand_pass
```
