# Role: Linux Hostname | ansible-collection-infrastructure

Sets the hostname of an EC2 instance, using its tags, to the following format:
`{{ ec2_hostname }}.{{ ec2_zone }}`

This role does assert that both variables are set before doing anything, but
best practice is to use `linux_ec2_tags` beforehand to highlight issues up-front.

The hostname is persisted using `preserve_hostname: true`, and is intended to be
used for distinct individual EC2 instances, not baked into AMIs.

In practice, thoughout CH projects these are EC2 tags set in Terraform, which get
surfaced by the amazon.aws.aws_ec2 inventory plugin's compose block.
