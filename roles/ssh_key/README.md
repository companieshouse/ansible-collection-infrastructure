# Ansible Role: SSH Key

An [Ansible Galaxy](https://galaxy.ansible.com/) role for retrieving and installing an SSH private key from Hashicorp Vault onto 
an Ansible controller host, primarily for use in ephemeral containers as part of a CI/CD workflow.

## Requirements

- The [hvac](https://pypi.org/project/hvac/) Python module is required as a dependency of the `community.hashi_vault` Ansible col
lection
- The private key should be stored as a base-64 encoded string in a key named `ssh_private_key` at the Vault path specified by th
e variable `ssh_key_vault_path`:

```json
{
  "ssh_private_key" : "d93hGhsh3Zk39..."
}
```

## Role Variables

The role defaults (see `defaults/main.yml`) assume that the key is being installed for the `root` user to a file named `id_rsa` i
n the directory `/home/root/.ssh` and will be created with suitable permissions if the file does not exist.

To skip creation of the parent directory:

```yaml
ssh_key_dir_check: false
```

To configure ownership or permissions of the `.ssh` directory:

```yaml
ssh_key_dir_owner: <user-name>
ssh_key_dir_group: <group-name>
ssh_key_dir_mode: <permissions>
```

To configure ownership or permissions of the key file:

```yaml
ssh_key_owner: <user-name>
ssh_key_group: <group-name>
ssh_key_mode: <permissions>
```
The value of the `ssh_key_dir_owner` variable (default `root`) is used to determine the path to the `.ssh` directory. For the `root` user this will be `/root/.ssh` and for any non-`root` user this will be `/home/{{ ssh_key_dir_owner }}/.ssh`.

To specify a name other than the default `id_rsa` for the key being installed:

```yaml
ssh_key_name: <key-name>
```

To remove a previously installed key:

```yaml
ssh_key_action: remove
```

## Example Requirements File

```yaml
---

collections:
  - name: companieshouse.general
    version: "1.0.0"
```

## Example Playbook

Specify `localhost` in your playbook to target the Ansible _controller_:

```yaml
---

- name: Provision Ansible controller SSH key for remote hosts
  hosts: localhost
  roles:
    - role: companieshouse.general.ssh_key
  vars:
    ssh_key_vault_path: /applications/my-application-config
    ssh_key_name: my-app-key
```

## License

This project is subject to the terms of the [MIT License](LICENSE).
