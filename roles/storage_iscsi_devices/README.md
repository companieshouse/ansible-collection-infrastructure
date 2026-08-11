# Role: Storage iSCSI Devices | ansible-collection-infrastructure
## WIP Released for Testing within CH Projects

Sets up iSCSI using initiator from Hashicorp Vault, target discovery (optional multi-path), login, and boot persistence.

This is a **provisioning**, not a reconciliation role. It can be re-run,
but won't re-identify a host with existing live sessions.

## Requirements

- Ansible `>= 2.15.6`
- `community.hashi_vault`
- `vault_set_fact` (from this collection)
- A RHEL-family host (for `iscsi-initiator-utils` and
  `device-mapper-multipath`)
- An AppRole with read access to the configured Vault path

## Vault schema

A secret with the following fields:

| Field | Type | Description |
|---|---|---|
| `iscsi_initiator_name` | string | Initiator IQN, e.g. `iqn.1994-05.com.redhat:host-01` |
| `iscsi_portal_ips` | list of strings | Portal IPs to point at discovery; should be a native Vault list, not JSON string |

## Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `storage_iscsi_devices_vault_path` | yes | — | Vault KV path, **relative to the engine mount point** |
| `storage_iscsi_devices_vault_engine_mount_point` | yes | — | Mount point of the KV secrets engine |
| `storage_iscsi_devices_vault_engine_version` | yes | — | KV secrets engine version (`1` or `2`) |
| `storage_iscsi_devices_install_packages` | no | `true` | Install initiator and multi-path tooling |
| `storage_iscsi_devices_multipath` | no | `false` | Whether the host reaches LUNs over multi-path |
| `storage_iscsi_devices_node_startup` | no | `automatic` | Value for `node.startup` |
| `storage_iscsi_devices_replacement_timeout` | no | `5` multipath, `120` single path | `node.session.timeo.replacement_timeout`, seconds |
| `storage_iscsi_devices_wipe` | no | `false` | **Destructive:** wipe discovered LUNs with `wipefs` |
| `storage_iscsi_devices_allow_initiator_change` | no | `false` | Permit an IQN change on a host with live sessions |

You can find your engine mount point and version using
`vault secrets list -detailed`; the `Path` column is the mount point,
and a mount with no `version` option is version 1.

## Usage

```yaml
- hosts: iscsi_clients
  roles:
    - role: companieshouse.infrastructure.storage_iscsi_devices
      vars:
        storage_iscsi_devices_vault_engine_mount_point: example-kv
        storage_iscsi_devices_vault_engine_version: 1
        storage_iscsi_devices_vault_path: "iscsi/{{ inventory_hostname }}"
        storage_iscsi_devices_multipath: true
```

## Considerations

- **Wipe is unguarded.** With `storage_iscsi_devices_wipe: true` the role runs
  `wipefs --all` against every visible LUN over iSCSI. This role is intended
  for first-time provisioning, so this is likely the desired outcome, but you are required to set this flag explicitly to true for confirmation.
- **Changing an IQN needs an outage.** Existing sessions keep the old IQN
  across restart. `storage_iscsi_devices_allow_initiator_change: true` logs out existing sessions before re-writing the name.
- **Reboot persistence depends on `node.startup`.** `storage_lvm` and
  `storage_data_vol` mount with `nofail`, so a host that fails to re-establish
  its sessions still boots cleanly, with the filesystems silently absent and
  their mount points writable. Anything writing to those paths writes to the
  root filesystem instead, and is lost once the LUNs return and mount over the
  top.
- **`--check` only validates the inputs.** Read-only tasks still run under
  `--check`, so a dry run will catch a bad Vault schema, a malformed IQN, a
  multi-path mismatch, or an initiator name that would change. Discovery and
  login however are skipped, so it cannot tell you whether the target will accept this initiator. Don't consider a clean `--check` as solid proof that a real run will succeed.
- Portal IPs appear in the output. This is intentional for CH usage, as it is
  run on internal CI/CD and useful for validation. The use of vault is to keep
  those details out of repositories.
- **No CHAP support.** If required for your use case, you'll need to add that
  functionality to compliment this role.
