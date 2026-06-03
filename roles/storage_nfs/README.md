# Role: Storage NFS | ansible-collection-infrastructure
Installs NFS client utilities and mounts one or more NFS exports,
creating mount point directories, updating `/etc/fstab`,
and mounting exports.

## Requirements
- Ansible `>= 2.15.6`
- `ansible.posix` collection (provides `ansible.posix.mount`)
- A RHEL-family host (`ansible_os_family == "RedHat"`)
- Network reachability from the host to the NFS server

## Variables
-  At least one definition is required in `storage_nfs_mounts`

| Field | Required | Default | Description |
|---|---|---|---|
| `server` | yes | — | NFS server hostname or IP |
| `export_path` | yes | — | Path of the export on the NFS server |
| `mount_point` | yes | — | Local path to mount the export at |
| `owner` | no | `root` | Owner of the mount point directory |
| `group` | no | `root` | Group of the mount point directory |
| `mode` | no | `0755` | Mode of the mount point directory |
| `opts` | no | `defaults,_netdev` | NFS mount options |

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
