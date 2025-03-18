provider "aws" {
  region = "us-west-1"
}

data "aws_ami" "Amazon_Linux" {
  most_recent = true
  owners = ["amazon"]

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

resource "aws_launch_configuration" "capser_launch_configuration" {
  name = "ASG002_launch_config"
  image_id = data.aws_ami.Amazon_Linux.image_id
  instance_type = "t2.nano"

  metadata_options {
    http_endpoint = "enabled"
    http_tokens = "required"
  }
  
}

output "Launch_configuration_name" {
  description = "Amazon Linux imageID"
  value = aws_launch_configuration.capser_launch_configuration.name
}

