# Create an Instance Profile for the AWS-managed role
resource "aws_iam_instance_profile" "managed_instance_profile" {
  name = "managed-instance-profile"
  role = var.role_name
}

resource "aws_launch_template" "instance_template" {
  name          = "instance-template"
  image_id      = var.ami_id
  instance_type = var.engine_node_instance_type

  # Attach Network Interfaces
  network_interfaces {
    associate_public_ip_address = false
    security_groups = var.security_groups
    subnet_id       = var.subnet_id
  }

  # Associate the IAM Instance Profile
  iam_instance_profile {
    name = aws_iam_instance_profile.managed_instance_profile.name
  }

  # Block device mapping for the root volume
  block_device_mappings {
    device_name = "/dev/xvda" # Default root volume device name for most AMIs
    ebs {
      delete_on_termination = true
      volume_size           = var.volume_size
      volume_type           = var.volume_type 
      encrypted             = true 
      kms_key_id            = var.kms_key_arn
    }
  }

  # Metadata Options
  metadata_options {
    http_endpoint               = "enabled"   # Allow metadata access
    http_tokens                 = "required"  # Enforces token usage for metadata requests
  }

  # Applies tags to the EC2 instance
  tag_specifications {
    resource_type = "instance" 
    tags = var.instance_tags
  }

  # Applies tags to the EBS Volume attached with EC2 instance
  tag_specifications {
    resource_type = "volume"
    tags          = var.volume_tags
  }

  tags = var.tags

  # User Data
  user_data = base64encode(<<-EOT
    #!/bin/bash
    sudo yum update -y
    sudo yum install -y java-1.8.0-openjdk
  EOT
  )
}