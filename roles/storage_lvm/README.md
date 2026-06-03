# Role: Storage LVM | ansible-collection-infrastructure

Provisions LVM-backed mount points on an EC2 host. It creates a
partition, physical volume, volume group, logical volume, and
filesystem, then mounts it at `/{{ name }}` and persists in
`/etc/fstab`. For each requested mount, the EBS volume requires
a `Purpose` tag to have been set (e.g. using Terraform). 

## Requirements

- Ansible `>= 2.15.6`
- `amazon.aws` collection `>= 8.0.0` (for `ec2_vol_info`)
- `community.general` collection (for `parted`, `lvg`, `lvol`, `filesystem`)
- `ansible.posix` collection (for `ansible.posix.mount`)
- `lvm2` and `parted` installed on the host
- EBS volumes with a `Purpose` tag matching each entry in `storage_lvm_mount_points`

### Environment variables

| Variable | Description |
|---|---|
| `AWS_REGION` | The AWS region used to query EBS volume information |

In practice, this is often set automatically in pipelines, but If not
(or running locally), export before invoking `ansible-playbook`.

If not explicitly set, the role falls back to `eu-west-2`.

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

## Idempotency

If all entries in `storage_lvm_mount_points` are already mounted,
the role skips provisioning after the pre-flight checks.
