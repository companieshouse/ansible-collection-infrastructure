# Role: Storage LVM | ansible-collection-infrastructure

Provisions LVM-backed mount points on an EC2 host, by creating a
partition, physical volume, volume group, logical volume, and
filesystem, then mounts at `/{{ name }}` and persists in
`/etc/fstab`. For each requested mount, the EBS volume requires
a `Purpose` tag to have been set (e.g. using Terraform).

## Requirements

- Ansible `>= 2.15.6`
- `amazon.aws` collection `>= 9.0.0, < 10.0.0` (for `ec2_vol_info`); keep in
  step with the pin in `galaxy.yml`
- `community.general` collection (for `parted`, `lvg`, `lvol`, `filesystem`)
- `ansible.posix` collection (for `ansible.posix.mount`)
- `boto3` and `botocore` on the **control node** (the EBS lookup runs with
  `delegate_to: localhost`, so these are not needed on the target host)
- `lvm2` and `parted` installed on the host
- EBS volumes with a `Purpose` tag matching each entry in `storage_lvm_mount_points`

### Inventory requirements

The `ec2_instance_id` variable must be available as a host variable,
typically composed via the `amazon.aws.aws_ec2` inventory plugin:

```yaml
# inventory/aws_ec2.yml
plugin: amazon.aws.aws_ec2
compose:
  ec2_instance_id: instance_id
```

## Variables

At least one definition is required in `storage_lvm_mount_points`.

| Field | Required | Default | Description |
|---|---|---|---|
| `name` | yes | — | EBS `Purpose` tag value to match (e.g. `u01`); also used as the mount path (`/u01`) |
| `vg` | yes | — | Volume group name |
| `lv` | yes | — | Logical volume name |
| `fstype` | no | `storage_lvm_fstype` | Filesystem type |
| `mount_opts` | no | `storage_lvm_mount_opts` | Mount options passed to `mount(8)` and written to `/etc/fstab` |
| `pe_size` | no | `storage_lvm_pe_size` | Physical extent size for the VG, in MB |
| `owner` | no | `storage_lvm_mount_owner` | Owner of the mount point directory |
| `group` | no | `storage_lvm_mount_group` | Group of the mount point directory |
| `mode` | no | `storage_lvm_mount_mode` | Mode of the mount point directory |

Role-level variables:

| Variable | Required | Default | Description |
|---|---|---|---|
| `storage_lvm_mount_points` | yes | — | List of mount definitions; must be non-empty |
| `storage_lvm_aws_region` | no | *(unset)* | AWS region used when querying ec2_vol_info (e.g. eu-west-1) |
| `storage_lvm_debugging_enabled` | no | `false` | Emit verbose debug output |
| `storage_lvm_fstype` | no | `xfs` | Default filesystem type |
| `storage_lvm_mount_opts` | no | `defaults,nofail` | Default mount options |
| `storage_lvm_pe_size` | no | `4` | Default physical extent size, MB |
| `storage_lvm_mount_owner` | no | `root` | Default mount directory owner |
| `storage_lvm_mount_group` | no | `root` | Default mount directory group |
| `storage_lvm_mount_mode` | no | `0755` | Default mount directory mode |

Note: `owner`/`group`/`mode` only apply to the mount point directory,
they will *not* change permissions for the mounted data.

## Terraform

Each EBS volume must have a `Purpose` tag matching the `name` field of
the corresponding `storage_lvm_mount_points` entry:

```hcl
resource "aws_ebs_volume" "u01" {
  availability_zone = aws_instance.db[0].availability_zone
  size              = 200

  tags = {
    Purpose = "u01"
  }
}
```

## Usage

```yaml
- hosts: ec2_servers
  roles:
    - role: companieshouse.infrastructure.storage_lvm
      vars:
        storage_lvm_mount_points:
          - name: u01
            vg: vol.oracle.u01
            lv: lv.oracle_u01
            pe_size: 16
            owner: oracle
            group: oinstall
            mode: "0755"
          - name: u02
            vg: vol.oracle.u02
            lv: lv.oracle_u02
            pe_size: 16
            owner: oracle
            group: oinstall
            mode: "0755"
```

## Safety guards

The run will not proceed if a mount is found to meet one of the following:
- the target path is already mounted, but was not caught in pre-flight
- the EBS volume ID cannot be resolved to a kernel device
- the resolved device is the system disk
- the partition belongs to a volume group other than the one requested
