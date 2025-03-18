resource "aws_vpc" "casper_vpc" {
  cidr_block = "10.0.0.0/16"  # Replace with your desired VPC CIDR block
  instance_tenancy = "default"

  tags = {
    Name = "CASPER_VPC"
  }
}

resource "aws_security_group" "lb_sg" {
  name_prefix = "CASPER-sg-"
  vpc_id = aws_vpc.casper_vpc.id
  // Add inbound and outbound rules as needed 
  ingress {
    from_port   = var.elbv2_security_group_values[0].from_port
    to_port     = var.elbv2_security_group_values[0].to_port
    protocol    = var.elbv2_security_group_values[0].protocol
    cidr_blocks = var.elbv2_security_group_values[0].cidr_block
  }
  egress {
    from_port   = var.elbv2_security_group_values[1].from_port
    to_port     = var.elbv2_security_group_values[1].to_port
    protocol    = var.elbv2_security_group_values[1].protocol
    cidr_blocks = var.elbv2_security_group_values[1].cidr_block
  }
}

resource "aws_subnet" "elb_subnet_a" {

  cidr_block              = "10.0.1.0/24"
  vpc_id                  = aws_vpc.casper_vpc.id
  availability_zone       = var.elbv2_subnet_region[var.elbv2_region][0]
  
  tags = {
    Name = "elb-subnet-A"
  }
}

resource "aws_subnet" "elb_subnet_b" {

  cidr_block              = "10.0.2.0/24"
  vpc_id                  = aws_vpc.casper_vpc.id
  availability_zone       = var.elbv2_subnet_region[var.elbv2_region][1]
  

  tags = {
    Name = "elb-subnet-B"
  }
}

resource "aws_s3_bucket" "lb_logs" {
    bucket = var.elbv2_s3_bucket

    tags = {
        Name =  "casper bucket"
        Environment = "production"
    }
}

resource "aws_s3_bucket_acl" "elbv2_log_bucket" {
  bucket = aws_s3_bucket.lb_logs.id
  // keeping the logs private in S3 bucket
  acl    = "private"
}

resource "aws_lb" "casper" {
  name               = "casper-lb-terraform"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb_sg.id]
  subnets            = [aws_subnet.elb_subnet_a.id, aws_subnet.elb_subnet_b.id]

  enable_deletion_protection = true

  access_logs {
    bucket  = aws_s3_bucket.lb_logs.id
    prefix  = "casper-lb"
    enabled = true
  }

  tags = {
    Environment = "production"
  }
}