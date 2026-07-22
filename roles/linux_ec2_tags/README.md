# Role: Linux EC2 Tags | ansible-collection-infrastructure

This role verifies the following have been set:
- ec2_zone
- ec2_environment
- ec2_hostname
- ec2_instance_id

Consider this as a dependency for other roles in this collection. It is intended to
be invoked at the start of runs that touch an EC2 instance (e.g. linux_hostname) which
can save time by validating requiremtns earlier in the run

In practice, thoughout CH projects these are EC2 tags set in Terraform, which get
surfaced by the amazon.aws.aws_ec2 inventory plugin's compose block.
