# Ansible Role: AWS CLI

An [Ansible Galaxy](https://galaxy.ansible.com/) role for installing or updating [AWS Command Line Interface](https://aws.amazon.com/cli/).

## Role Variables

The role defaults (see [defaults/main.yml](defaults/main.yml)) use Amazon's official installer URL for the 64-bit Linux package:

```yaml
aws_cli_url: https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip
```

To specify a different location for the installer package, override the `aws_cli_url` role variable in your playbook:

```yaml
aws_cli_url: https://...
```

If AWS CLI is already in its default location of `/usr/local/bin/aws` this role will make no changes. To always update to the latest available version of AWS CLI, override the `aws_cli_update` role variable default:

```yaml
aws_cli_update: true
```

> [!TIP]
> The default install path for AWS CLI (`/usr/local/bin/aws`) can be changed by setting the `aws_cli_path` variable.

This role creates a temporary directory under `/tmp` where the AWS CLI installer and associated files are extracted before the AWS CLI `install` script is executed. The temporary directory is removed after the script completes. If the `/tmp` directory on the target host(s) resides on a filesystem that is mounted with the `noexec` option, installation will fail with a 'Permission denied' error as the `install` script cannot be executed in this scenario. Specify an alternative path in this case, using the `aws_cli_temp_dir` role variable, to a directory without execution restrictions:

```yaml
aws_cli_temp_dir: "/home/{{ ansible_user }}"
```

Using the above value, the temporary directory will be created inside `/home/{{ ansible_user }}` rather than `/tmp`, and will be removed at the end of the role.

## Example Requirements File

```yml
---

- name: Provision AWS CLI tool
  hosts: all
  roles:
    - role: companieshouse.general.aws_cli
```

## License

This project is subject to the terms of the [MIT License](LICENSE).
