# ansible-collection-infrastructure
An Ansible Galaxy collection comprising infrastructure Ansible roles and playbooks for use in Companies House projects.

## Authors
- [samh241](https://github.com/samh241)
- [ls-comh](https://github.com/ls-comh)


#########################################


The code is **idempotent**, **ansible‑lint clean**, and **safe to re‑run in CI/Concourse**.

This playbook automates the **quarterly AFD‑Postcode (PCPlus) data update**
on EC2 hosts.

It is designed to be:
- Idempotent (safe to re‑run)
- ansible‑lint compliant
- Safe against partial failures



## What the playbook does

1. Ensures `/opt/pcplus` exists
2. Verifies AWS CLI availability on the host
3. Creates a staging directory (`data_new`)
4. Validates the current quarter dataset exists in S3
5. Copies the current quarter data from S3
6. Ensures old nested backup paths are removed
7. Backs up the existing `data` directory
8. Promotes `data_new` to active `data`
9. Validates and fetches `pcplus.lic` from S3
10. Enforces correct permissions



# S3 layout expected

text
s3://<bucket>/pcplus/
├── <YYYY_QN>/
│   └── data/
└── pcplus.lic


## Behaviour on re‑runs

*   Existing backups are not overwritten
*   Nested `data_old/data` paths are cleaned before promotion
*   If S3 artefacts are missing, the play fails early with a clear message


Safety notes

This playbook **never deletes active data without a backup**.
Promotion and backup are guarded to prevent data loss on retries.

