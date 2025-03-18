
resource "aws_vpc" "shared_vpc" {
  count = var.vpc_cidr_details["createVPC"].cidr != "" ? 1 : 0

  cidr_block       = var.vpc_cidr_details["createVPC"].cidr
  instance_tenancy = "default"
  enable_dns_support = true
  enable_dns_hostnames = true

  tags = {
    Name = "platform-shared-VPC"
  }

}

resource "aws_subnet" "subnet1a" {
  count = var.vpc_cidr_details["createVPC"].cidr != "" ? 1 : 0

  vpc_id     = aws_vpc.shared_vpc[0].id
  cidr_block = var.vpc_cidr_details["createVPC"].subnets["subnet1a"].Subnet_cidr
  availability_zone = var.vpc_cidr_details["createVPC"].subnets["subnet1a"].AvailabilityZone
  tags = {
    Name = "platform-shared-subnet-1A"
  }
}

resource "aws_subnet" "subnet1b" {
  count = var.vpc_cidr_details["createVPC"].cidr != "" ? 1 : 0

  vpc_id     = aws_vpc.shared_vpc[0].id
  cidr_block = var.vpc_cidr_details["createVPC"].subnets["subnet1b"].Subnet_cidr
  availability_zone = var.vpc_cidr_details["createVPC"].subnets["subnet1b"].AvailabilityZone
  tags = {
    Name = "platform-shared-subnet-1B"
  }
}


resource "aws_vpc_ipv4_cidr_block_association" "secondary_cidr" {
  count = var.isproduction == false ? 1 : 0
  
  vpc_id     = aws_vpc.shared_vpc[0].id
  cidr_block = var.vpc_cidr_details["createVPC"].secondary_cidr
}

resource "aws_subnet" "subnet2a" {
  count = var.isproduction == false ? 1 : 0

  vpc_id     = aws_vpc.shared_vpc[0].id
  cidr_block = var.vpc_cidr_details["createVPC"].subnets["subnet2a"].Subnet_cidr
  availability_zone = var.vpc_cidr_details["createVPC"].subnets["subnet2a"].AvailabilityZone
  tags = {
    Name = "platform-shared-subnet-2A"
  }

}

resource "aws_subnet" "subnet2b" {
  count = var.isproduction == false ? 1 : 0

  vpc_id     = aws_vpc.shared_vpc[0].id
  cidr_block = var.vpc_cidr_details["createVPC"].subnets["subnet2b"].Subnet_cidr
  availability_zone = var.vpc_cidr_details["createVPC"].subnets["subnet2b"].AvailabilityZone
  tags = {
    Name = "platform-shared-subnet-2B"
  }
}

resource "aws_flow_log" "enable_vpc_flowlogs" {
    log_destination      = "arn:aws:s3:::platform-da2-central-vpcflowlogs-${var.env_type}/"
    log_destination_type = "s3"
    traffic_type         = "ALL"
    vpc_id               = aws_vpc.shared_vpc[0].id
    tags = {
    "Name" = "platform-shared-flowlog"
  }
}


