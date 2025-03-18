//VPC Creation
resource "aws_vpc" "vpc" {
  cidr_block           = var.cidr_block
  instance_tenancy     = "default"
  enable_dns_hostnames = "true"
  tags = merge(local.tags,
    {
      Name                  = "${local.resource_group}-vpc"
      "Data Classification" = "Internal"
  })
}
//Elastic IP
resource "aws_eip" "elastic_ip" {
  vpc = true
  tags = merge(local.tags,
    {
      Name                  = "${local.resource_group}-elastic_ip"
      "Data Classification" = "Internal"
  })
}
//Public Subnet
resource "aws_subnet" "public_subnet" {
  vpc_id            = aws_vpc.vpc.id
  count             = length(var.public_subnet_cidr_block)
  cidr_block        = var.public_subnet_cidr_block[count.index]
  availability_zone = var.avaialabity_zones[count.index]
  tags = merge(local.tags,
    {
      Name                  = "${local.resource_group}-public_subnet"
      "Data Classification" = "Internal"

  })
}
//Private Subnet
resource "aws_subnet" "private_subnet" {
  vpc_id            = aws_vpc.vpc.id
  count             = length(var.private_subnet_cidr_block)
  cidr_block        = var.private_subnet_cidr_block[count.index]
  availability_zone = var.avaialabity_zones[count.index]
  tags = merge(local.tags,
    {
      Name                  = "${local.resource_group}-private_subnet"
      "Data Classification" = "Internal"

  })
}
//Internet gateway connected to VPC
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id
  tags = merge(local.tags,
    {
      Name                  = "${local.resource_group}-igw"
      "Data Classification" = "Internal"
  })
}
// Public Routing table 
resource "aws_route_table" "public_route" {
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = merge(local.tags,
  {
      Name                  = "${local.resource_group}-public_route"
      "Data Classification" = "Internal"
  })
}
// Public routing table associated to Public subnets
resource "aws_route_table_association" "public_associate" {
  count          = length(var.public_subnet_cidr_block)
  subnet_id      = aws_subnet.public_subnet[count.index].id
  route_table_id = aws_route_table.public_route.id
}
//Nat Gateway Creation
resource "aws_nat_gateway" "nat_gateway" {
  allocation_id = aws_eip.elastic_ip.id
  subnet_id     = aws_subnet.public_subnet[0].id
  tags = merge(local.tags,
    {
      Name                  = "${local.resource_group}-nat_gateway"
      "Data Classification" = "Internal"
  })
}
// Route table in order to connect private subnet to the NAT Gateway
resource "aws_route_table" "routetable_nat" {
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_nat_gateway.nat_gateway.id
  }
  tags = merge(local.tags,
    {
      Name                  = "${local.resource_group}-routetable_nat"
      "Data Classification" = "Internal"
  })
}
// Private routing table associated to Private subnets
resource "aws_route_table_association" "private_associate" {
  count          = length(var.private_subnet_cidr_block)
  subnet_id      = aws_subnet.private_subnet[count.index].id
  route_table_id = aws_route_table.routetable_nat.id
}

