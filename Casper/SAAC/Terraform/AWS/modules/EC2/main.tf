resource "aws_security_group" "casper_sg" {
  
  name_prefix = "CASPER-sg-"
  vpc_id = aws_vpc.casper_vpc.id
  // Add inbound and outbound rules as needed
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/24"]
  }
}

resource "aws_subnet" "casper_subnet" {
  vpc_id     = aws_vpc.casper_vpc.id
  cidr_block = "10.0.1.0/24"  # Replace with your desired subnet CIDR block

  availability_zone       = var.ec2_subnet_region[var.ec2_region][0]
  
  tags = {
    Name = "casper-subnet-A"
  }
}

resource "aws_iam_instance_profile" "casper_profile" {
  name = "casper-instance-profile"
  role = aws_iam_role.casper_role.name
}

resource "aws_iam_role" "casper_role" {
  name = "casper-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_vpc" "casper_vpc" {
  cidr_block = "10.0.0.0/16"  # Replace with your desired VPC CIDR block
  instance_tenancy = "default"

  tags = {
    Name = "CASPER_VPC"
  }
}

resource "aws_instance" "casper_instance" {
  ami = var.ec2_aws_ami[var.ec2_region]
  instance_type = var.ec2_aws_instance

  tags = {
    Name = "CASPER_EC2_Instance"
  }

  vpc_security_group_ids = [aws_security_group.casper_sg.id]
  subnet_id              = aws_subnet.casper_subnet.id

  // 1. Disable source/destination checks (network traffic forwarding)
  source_dest_check = false

  // 2. Use IAM instance profile for permissions
  iam_instance_profile = aws_iam_instance_profile.casper_profile.name

  // 3. Enable detailed monitoring (CloudWatch Metrics)
  monitoring = true

  // 4. Enable EBS encryption for root volume
  root_block_device {
    encrypted = true
  }
}


