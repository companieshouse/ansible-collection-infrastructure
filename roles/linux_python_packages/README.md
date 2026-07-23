# Role: Linux Python Packages | ansible-collection-infrastructure

Installs a list of Python packages into a **virtualenv** using pip.

## Requirements
- Ansible `>= 2.15.6`
- `python3`
- RHEL 7, 8, or 9, or Amazon Linux 2023
- Network access to PyPI, if not using an internal index

## Variables
| Variable | Default | Description |
|---|---|---|
| `linux_python_packages_list` (required) | - | Python packages (with optional version specifiers) |
| `linux_python_packages_virtualenv` | - | Recommended: Absolute venv path |
| `linux_python_packages_virtualenv_command` | `/usr/bin/python3 -m venv` | Command used to build venv, when using `linux_python_packages_virtualenv` |
| `linux_python_packages_executable` | `""` | Alternative: install into an existing interpreter |
| `linux_python_packages_extra_args` | `""` | Extra pip args, e.g. an internal `--index-url` |
| `linux_python_packages_umask` | `"0022"` | umask applied during install |

Either set linux_python_packages_virtualenv path, or linux_python_packages_executable for an existing interpreter.
You cannot use both simultaneously.

## Usage - virtualenv (recommended)

```yaml
- hosts: all
  roles:
    - role: companieshouse.infrastructure.linux_python_packages
      vars:
        linux_python_packages_virtualenv: /opt/myapp
        linux_python_packages_list:
          - "requests>=2.31"
          - "jmespath>=1.0"
```

## Usage - executable (if needing to install into an existing interpreter)

```yaml
- hosts: all
  roles:
    - role: companieshouse.infrastructure.linux_python_packages
      vars:
        linux_python_packages_executable: /opt/othervenv/bin/pip
        linux_python_packages_list:
          - "requests>=2.31"
          - "jmespath>=1.0"
```
