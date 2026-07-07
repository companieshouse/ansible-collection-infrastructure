## Storage  |  chips-db-ora19-ansible
| Category | Author(s) |
|----------|--------|
| Linux & Storage | [charris-CH](https://github.com/charris-CH), [ls-comh](https://github.com/ls-comh) |

&nbsp;

Discovers EBS volumes by their `Purpose` tag as set in [chips-db-ora19-terraform](https://github.com/companieshouse/chips-db-ora19-terraform/blob/main/groups/chips-db/instance.tf), then resolves those to NVMe block devices, provisioning as mounts:
- checks AWS for attached volumes and retrieves their tags
- matches volume serial to local NVMe via `lsblk`
- for each in `storage_mount_points` partition, create VG/LV, formats (xfs), mount, and add to fstab
- sets `oracle:oinstall` ownership on all mount points
- establishes `storage_devices` to be consumed by [asm role](../asm)

&nbsp;

Mount points are defined per host group in [group_vars](../../group_vars/)

&nbsp;

Variable                    |Default  | Description
----------------------------|:-------:|------------
`storage_debugging_enabled` |`false`  | Enables debug output of resolved devices
