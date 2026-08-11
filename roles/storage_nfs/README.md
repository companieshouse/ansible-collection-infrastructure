# Role: Storage NFS | ansible-collection-infrastructure
## WIP Released for Testing within CH Projects

Installs NFS client utilities and mounts one or more NFS exports,
creating mount point directories, updating `/etc/fstab`,
and mounting exports.

## Requirements

- Ansible `>= 2.15.6`
- `ansible.posix` collection (provides `ansible.posix.mount`)
- A RHEL-family host (`ansible_os_family == "RedHat"`)
- Network reachability from the host to the NFS server

## Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `storage_nfs_mounts` | yes | — | List of mount definitions; must be non-empty |
| `storage_nfs_mount_owner` | no | `root` | Default owner for mount point directories |
| `storage_nfs_mount_group` | no | `root` | Default group for mount point directories |
| `storage_nfs_mount_mode` | no | `0755` | Default permissions for mount point directories |
| `storage_nfs_mount_opts` | no | `defaults,_netdev` | Default NFS mount options |

Each entry in `storage_nfs_mounts` takes:

| Field | Required | Default | Description |
|---|---|---|---|
| `server` | yes | — | NFS server hostname or IP |
| `export_path` | yes | — | Path of the export on the NFS server |
| `mount_point` | yes | — | Local absolute path to mount the export at |
| `owner` | no | `storage_nfs_mount_owner` | Owner of the mount point directory |
| `group` | no | `storage_nfs_mount_group` | Group of the mount point directory |
| `mode` | no | `storage_nfs_mount_mode` | Mode of the mount point directory |
| `opts` | no | `storage_nfs_mount_opts` | NFS mount options |

Note: `owner`/`group`/`mode` apply to the local mount-point
directory, they will *not* change permissions on the mounted data.

## Usage

```yaml
- hosts: localhost
  roles:
    - role: companieshouse.infrastructure.storage_nfs
      vars:
        storage_nfs_mounts:
          - server: nfs.example.co.uk
            export_path: /exports/home
            mount_point: /home/shared
          - server: nfs.example.co.uk
            export_path: /exports/data
            mount_point: /mnt/data
            opts: "defaults,noatime"
```

If you want to fetch definitions from vault, use the `vault_set_fact`
role and pass the established facts to `storage_nfs` e.g.
```yaml
- hosts: localhost
  tasks:
    - name: Fetch NFS mount definitions from Vault
      ansible.builtin.include_role:
        name: companieshouse.infrastructure.vault_set_fact
      vars:
        vault_set_fact_path: "secret/app/nfs"
        vault_set_fact_name: "app_nfs"
  roles:
    - role: companieshouse.infrastructure.storage_nfs
      vars:
        storage_nfs_mounts: "{{ app_nfs.mounts }}"
```
