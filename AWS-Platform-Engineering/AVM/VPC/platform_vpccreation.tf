data "aws_region" "current" {}

locals {

  env_value = var.env_type == "uat" ? "acceptance" : var.env_type

}
resource "aws_vpc" "create_vpc_in_child_account" {
  for_each  = var.RegionIpDictionary
  
  cidr_block       = each.value.cidr
  instance_tenancy = "default"
  enable_dns_support = true
  enable_dns_hostnames = true

  tags = {
    Name = "platform-VPC"
    platform_donotdelete = "yes"

  }
}

resource "aws_subnet" "create_vpc_subnet_pvt_1" {
  for_each = var.RegionIpDictionary

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.Subnet_cidr_1
  availability_zone = "${data.aws_region.current.name}a"

  tags = {
    Name = "platform-private-subnet-1"
  }
}

resource "aws_subnet" "create_vpc_subnet_pvt_2" {
  for_each = var.RegionIpDictionary

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.Subnet_cidr_2
  availability_zone = "${data.aws_region.current.name}b"

  tags = {
    Name = "platform-private-subnet-2"
  }
}

resource "aws_subnet" "create_vpc_subnet_pub_1" {
  for_each = var.Connectivity == "HYB" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.Subnet_cidr_3
  availability_zone = "${data.aws_region.current.name}a"

  tags = {
    Name = "platform-public-subnet-1"
  }
}

resource "aws_subnet" "create_vpc_subnet_pub_2" {
  for_each = var.Connectivity == "HYB" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.Subnet_cidr_4
  availability_zone = "${data.aws_region.current.name}b"

  tags = {
    Name = "platform-public-subnet-2"
  }
}

resource "aws_flow_log" "enable_vpc_flowlogs" {
    for_each = var.RegionIpDictionary

    log_destination      = "arn:aws:s3:::platform-da2-central-vpcflowlogs-${local.env_value}"
    log_destination_type = "s3"
    traffic_type         = "ALL"
    vpc_id               = aws_vpc.create_vpc_in_child_account[each.key].id
}