# Role: Linux EC2 Hostname | ansible-collection-infrastructure

A hostname role intended for AMIs, which installs a system service for setting the hostname dynamically (via EC2 tags) upon each boot. This contrasts with `linux_hostname`, which
acts on existing instances, persisting with cloud-init's `preserve_hostname`.

## Requirements

- Ansible `>= 2.15.6`
- Amazon Linux 2023, or RHEL/Rocky 8, 9, or 10
- IMDS reachable at boot, with instance metadata tags enabled
- A full Hostname tag value (see below for Terraform example)

## Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `linux_ec2_hostname_tag_key` | no | `Hostname` | Tag key holding the full hostname |
| `linux_ec2_hostname_before_units` | no | `[amazon-cloudwatch-agent.service]` | System units to order after the hostname unit; `[]` omits `Before` |
| `linux_ec2_hostname_enabled` | no | `true` | Whether unit is enabled to start at boot |
| `linux_ec2_hostname_imds_base_url` | no | `http://169.254.169.254/latest` | Metadata base URL (only override for testing) |

## Terraform (pre-reqs)

Enable metadata and set the Hostname tag:

```hcl
metadata_options {
  http_tokens            = "required"
  instance_metadata_tags = "enabled"
}

tags = {
  Hostname = "example-1.development.example.internal"
}
```

## Usage

```yaml
- hosts: all
  become: true
  roles:
    - role: companieshouse.infrastructure.linux_ec2_hostname
      vars:
        linux_ec2_hostname_before_units:
          - amazon-cloudwatch-agent.service
```

If no tag is supplied the unit defers to cloud-init.

Note: CloudWatch log stream names use `{local_hostname}`, whereas here we use `{hostname}`.

## Testing

`molecule/default` requires Docker with systemd-capable containers for Amazon Linux 2023 and Rocky Linux 8, 9 and 10. A mock metadata service tests valid, absent, and invalid tags. The wider tests cover service unreachable, a custom tag key, check mode, and idempotence.

Images are pinned by digest; refresh with
`docker buildx imagetools inspect <image>:latest`.

Behind a corporate TLS/SSL inspecting proxy, set `MOLECULE_EXTRA_CA_FILE` to
include the proxy's CA certificate.
