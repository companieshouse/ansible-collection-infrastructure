# Role: Storage Data Vol | ansible-collection-infrastructure

Formats and mounts an explicitly named block device under a specific path,
often used for data volumes.

For LVM-backed mounts resolved via EBS `Purpose` tags, look at `storage_lvm`.

## Requirements

- Ansible `>= 2.15.6`
- `community.general` collection (for `filesystem`)
- `ansible.posix` collection (for `mount`)
- `lsof` and `psmisc` (for device-busy check)

## Variables

Defined in [`meta/argument_specs.yml`](meta/argument_specs.yml). View with:
```
ansible-doc -t role companieshouse.infrastructure.storage_data_vol
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `storage_data_vol_mount_point` | yes | — | Absolute path to mount the device |
| `storage_data_vol_device_name` | yes | — | Absolute path of the block device |
| `storage_data_vol_filesystem_type` | no | `xfs` | Filesystem type for newly-formatted devices |
| `storage_data_vol_mount_opts` | no | `defaults,nofail` | Mount options passed to `mount(8)` and written to `/etc/fstab` |

## Usage

```yaml
- hosts: my_web_servers
  roles:
    - role: companieshouse.infrastructure.storage_data_vol
      vars:
        storage_data_vol_mount_point: /opt
        storage_data_vol_device_name: /dev/nvme1n1
```

## Behaviour

1. Waits up to 300 seconds for the device to appear
2. Confirms the device is genuinely attached, not just a path that exists
3. Checks if the device already has a filesystem; if so, leaves it alone
4. Refuses to proceed if the device has a partition table, but no filesystem
5. Otherwise, creates a filesystem of the requested type
6. Creates the mount point directory if missing, owned `root:root`
7. Mounts the device by UUID with `storage_data_vol_mount_opts`

The mount is added to `/etc/fstab` by UUID, so it persists across reboots and
survives NVMe enumeration order changing between boots.

## Warning: Device names can vary

Block device names depend on instance type, kernel boot order, and how
volumes are attached. `/dev/nvme1n1` may be the data volume on one instance and root on another. The role will format the device explicitly set. Picking the wrong device may **destroy data on the system disk**.

If you're unsure which device to target, either:

- Use `storage_lvm`, which resolves EBS volumes via a `Purpose` tags, or
- Verify the device with `lsblk` on the target host before running the role.

The partition-table check heads off the most common mistake here, but is not
infallible; a blank, unpartitioned disk will be formatted.
