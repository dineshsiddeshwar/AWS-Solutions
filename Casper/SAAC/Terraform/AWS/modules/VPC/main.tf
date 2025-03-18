resource "aws_security_group" "vpc_sg" {
  name_prefix = "CASPER-sg-"
  vpc_id      = aws_vpc.casper_vpc.id
  // Add inbound and outbound rules as needed 
  ingress {
    from_port   = var.vpc_security_group_values[0].from_port
    to_port     = var.vpc_security_group_values[0].to_port
    protocol    = var.vpc_security_group_values[0].protocol
    cidr_blocks = var.vpc_security_group_values[0].cidr_block
  }
  egress {
    from_port   = var.vpc_security_group_values[1].from_port
    to_port     = var.vpc_security_group_values[1].to_port
    protocol    = var.vpc_security_group_values[1].protocol
    cidr_blocks = var.vpc_security_group_values[1].cidr_block
  }
}

resource "aws_vpc_ipam" "casper_vpc_ipam" {
  operating_regions {
    region_name = var.vpc_deployment_region
  }
}

resource "aws_vpc_ipam_pool" "casper_vpc_ipam_pool" {
  address_family = var.network_address_type
  ipam_scope_id  = aws_vpc_ipam.casper_vpc_ipam.private_default_scope_id
  locale         = var.vpc_deployment_region
}

resource "aws_vpc_ipam_pool_cidr" "casper" {
  ipam_pool_id = aws_vpc_ipam_pool.casper_vpc_ipam_pool.id
  cidr         = "172.20.0.0/16"
}

resource "aws_vpc" "casper_vpc" {
  cidr_block       = "172.20.0.0/16"
  instance_tenancy = "default"

  tags = {
    Name = "CASPER_VPC"
  }
  ipv4_ipam_pool_id   = aws_vpc_ipam_pool.casper_vpc_ipam_pool.id
  depends_on = [
    aws_vpc_ipam_pool_cidr.casper
  ]
}
