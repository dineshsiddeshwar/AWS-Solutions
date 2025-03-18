# Get latest AMI ID for Amazon Linux2 OS
data "aws_ami" "approved_amis" { #  Ensure Standalone EC2 service can only use AMIs for approved operating systems
  most_recent = true
  owners      = var.ami_owners #  Ensure your Amazon Machine Images (AMIs) are not accessible to all AWS accounts , restricated to particular account
  filter {
    name   = "name"
    values = var.approved_amis_filter_name #  Ensure Standalone EC2s deployed by AWS Services should use only organizations security hardened AMIs
  }
  filter {
    name   = "root-device-type"
    values = var.approved_amis_filter_root_device_type
  }
  filter {
    name   = "virtualization-type"
    values = var.approved_amis_filter_virtualization_type
  }
  filter {
    name   = "architecture"
    values = var.approved_amis_filter_architecture
  }
}

# AWS EC2 Instance Terraform Module
resource "aws_instance" "ec2_instance" {
  ami                     = data.aws_ami.approved_amis.id
  availability_zone       = var.ec2_availability_zone
  disable_api_termination = true #  Ensure Termination Protection feature is enabled for EC2 instances that are not part of ASGs.

  iam_instance_profile = var.aws_ec2_instance_profile_reader_profile_name
  instance_type        = var.aws_ec2_instance_type
  key_name             = var.aws_ec2_instance_keypair
  // launch_template      = is an alternative way to spin up EC2 https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-templates.html
  subnet_id              = var.aws_ec2_vpc_private_subnet_id #  Ensure EC2 Instances are deployed in private subnets to prevent public accessibility
  vpc_security_group_ids = var.aws_ec2_vpc_private_sgs #  Ensure EC2 enfoces strict inbound access control - The baselined security group blocks common ports

  depends_on = [data.aws_vpc.ec2_vpc] #  Ensure EC2 instances are launched using the EC2-VPC platform instead of outdated EC2 classic platform
  tags       = var.common_tags 
}

#  Ensure EC2 uses Interface VPC Endpoints to communicate privately with public services

resource "aws_vpc_endpoint" "ec2_vpc_endpoint_id" {
  vpc_id              = data.aws_vpc.ec2_vpc.id
  subnet_ids          = [var.aws_ec2_vpc_private_subnet_id]
  service_name        = var.ec2_service_name
  vpc_endpoint_type   = var.ec2_vpc_endpoint_type
  security_group_ids  = var.ec2_vpc_sgs
  private_dns_enabled = true
}

# Attach the EBS volume to the EC2 instance
resource "aws_volume_attachment" "ec2_ebs_volume_attachment" {
  device_name = var.ebs_device_name
  volume_id   = aws_ebs_volume.ec2_attached_ebs_volume.id
  instance_id = aws_instance.ec2_instance.id
}

#  Ensure EC2 access followed the principal of least privilege
resource "aws_iam_role" "ec2_role" {
  name               = "Reader_role"
  assume_role_policy = data.template_file.EC2LeastPrivilegeAccessPolicy.rendered
}

resource "aws_iam_instance_profile" "reader_profile" {
  name = "Reader_profile"
  role = aws_iam_role.ec2_role.name
}

resource "aws_iam_role_policy" "reader_policy" {
  name   = "Reader_policy"
  role   = aws_iam_role.ec2_role.id
  policy = data.template_file.EC2LeastPrivilegeAccessPolicy.rendered
}

#  Ensure EC2 data are encrypted at rest using Organization's Managed Keys (CMK)
resource "aws_ebs_volume" "ec2_attached_ebs_volume" {
  availability_zone = var.ec2_availability_zone
  size              = var.ebs_volume_size
  encrypted         = true
  kms_key_id        = var.ec2_key_arn  # ARN
}

#  Ensure EC2 connections are encrypted in transit using TLS 1.2 
# Requirement is implement through application deployed inside EC2 or WAF or loadbalancer.

#  Ensure EC2 adhers to CG Patch and Vulnerability Management Standards
# requirement  is handled upstream from EC2 Patching Process, for more information follow this link
# TODO: ---- insert link here ----

#  Ensure CloudTrail logging is enabled 
# This should be set up in the cloudtrail resource, cloudtrail is automated and configured
# to pick up new resources on its own
# TODO: ---- insert cloudtrail runbook link here ----

#  Ensure CloudWatch logging enabled 
# Cloudwatch agent should be installed with a startup script, and configuration. There is guidance
# here. Cloudwatch will be implemented based on discussions from compute team
# TODO: ---- Need to discuss with Compute team----

#  Ensure unused EC2 key pairs are decomissioned to follow AWS security bet practices
# Requirement is implemented as part of KMS Runbook
# TODO: ---- insert KMS runbook link here ----

#  Ensure unused Amazon Machine Images (AMIs) are identified and removed
# requirement  is handled upstream from EC2 Patching Process, for more information follow this link
# TODO: ---- insert link here ----

#  Ensure unused AWS Elastic Network Interfaces (ENIs) are removed
# requirement  is handled upstream from EC2 Patching Process, for more information follow this link
# TODO: ---- insert link here ----

# Ensure idle AWS EC2 instances are identified and stopped or terminated to optimize AWS costs
# requirement is handled upstream from EC2 Patching Process, for more information follow this link
# TODO: ---- insert link here ----



