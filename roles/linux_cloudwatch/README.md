# Role: Linux CloudWatch | ansible-collection-infrastructure

Installs the Amazon CloudWatch agent, writes `linux_cloudwatch_config` as its
configuration, and sets the service state.

## Requirements

- Ansible `>= 2.15.6`
- Amazon Linux 2023, or RHEL/Rocky 8, 9, or 10
- Access to `linux_cloudwatch_download_base_url` if using `download` method

### RHEL/Rocky 8

`dnf` on release 8 only works with the system Python 3.6, which ansible-core
dropped in 2.17. Use either:
- ansible-core `>= 2.21` with Python `>= 3.9` on the host (e.g. `python3.12` from AppStream)
- ansible-core `<= 2.16` with the system Python

## Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `linux_cloudwatch_config` | yes | — | Agent configuration, written as YAML; must be non-empty |
| `linux_cloudwatch_service_enabled` | no | `true` | Start the agent at boot |
| `linux_cloudwatch_service_state` | no | `started` | `started` or `stopped`; use `stopped` for AMI builds |
| `linux_cloudwatch_min_version` | no | `""` | Minimum agent version, e.g. `1.300070.0`; an older agent is upgraded |
| `linux_cloudwatch_install_method` | no | `auto` | `auto`, `repo` or `download` |
| `linux_cloudwatch_download_base_url` | no | `https://amazoncloudwatch-agent.s3.amazonaws.com` | Bucket or mirror used by `download` |
| `linux_cloudwatch_download_version` | no | `latest` | `latest`, or a release to pin, e.g. `1.300074.1b2005` (`download` only) |
| `linux_cloudwatch_mode` | no | `ec2` | `ec2`, `onPremise` or `auto`; passed to `amazon-cloudwatch-agent-ctl -m` |

## Usage

```yaml
- hosts: all
  roles:
    - role: companieshouse.infrastructure.linux_cloudwatch
      vars:
        linux_cloudwatch_min_version: "1.300070.0"
        linux_cloudwatch_config:
          agent:
            run_as_user: root
          logs:
            logs_collected:
              journald:
                collect_list:
                  - log_group_name: /aws/ec2/example/journal
                    log_stream_name: "{instance_id}"
                    units:
                      - sshd
```

## Install methods

| Method | Behaviour |
|---|---|
| `auto` | `repo` on Amazon Linux, `download` on RHEL / Rocky |
| `repo` | Installs from the host's repositories |
| `download` | Downloads the RPM from `linux_cloudwatch_download_base_url`, verifies its signature, then installs |

`download` checks the signature against the AWS key fingerprint in `vars/main.yml`
(see [Verifying the signature of the CloudWatch agent package](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/verify-CloudWatch-Agent-Package-Signature.html)).
The RPM is unsigned, so `dnf`'s GPG check is disabled for the install.

## Behaviour

1. Asserts the platform, ansible-core version, and variables are valid
2. Installs agent if it is missing, below `linux_cloudwatch_min_version`, or
   differs from pinned `linux_cloudwatch_download_version`
3. Fails after install if agent is still below `linux_cloudwatch_min_version`
4. Writes configuration to `/etc/amazon-cloudwatch-agent.json`
5. Runs `amazon-cloudwatch-agent-ctl -a fetch-config` if agent's copy is
   missing or differs; a rejected config fails and will be retried on next run
6. Sets service's boot and run state, restarting if config changes

Build suffixes (e.g. `b2005`) are ignored when comparing against
`linux_cloudwatch_min_version`.

## Testing

`molecule/default` needs Docker with systemd-capable containers, and for
Rocky Linux 8 ansible-core `>= 2.21`. It covers each platform and install
methods, including one pinned version and `onPremise` mode.

Images are pinned by digest; refresh with
`docker buildx imagetools inspect <image>:latest`.

Behind a corporate TLS/SSL inspecting proxy, set `MOLECULE_EXTRA_CA_FILE` to
inlcude the proxy's CA certificate.
