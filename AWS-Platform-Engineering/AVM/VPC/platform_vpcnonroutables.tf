resource "aws_vpc_ipv4_cidr_block_association" "non_routable_extension" {
  for_each = var.IsNonRoutable == "Yes" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = var.SSMParameters.NonRoutableCIDR
}

resource "aws_subnet" "vpc_nonRoutable_subnet_1" {
  for_each = var.IsNonRoutable == "Yes" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = var.SSMParameters.NonRoutableSubnetAZ1
  availability_zone = "${data.aws_region.current.name}a"

  tags = {
    Name ="platform-vpc-subnet-non-routable"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.non_routable_extension ]
}

resource "aws_subnet" "vpc_nonRoutable_subnet_2" {
  for_each = var.IsNonRoutable == "Yes" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = var.SSMParameters.NonRoutableSubnetAZ2
  availability_zone = "${data.aws_region.current.name}b"

  tags = {
    Name ="platform-vpc-subnet-non-routable"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.non_routable_extension ]
}

resource "aws_nat_gateway" "private_nat_1" {
  for_each = var.IsNonRoutable == "Yes" ? var.RegionIpDictionary : tomap({})

  connectivity_type = "private"
  subnet_id         = aws_subnet.create_vpc_subnet_pvt_1[each.key].id

  tags = {
    Name = "nat-gateway-nonroutable"
  }
}


resource "aws_nat_gateway" "private_nat_2" {
  for_each = var.IsNonRoutable == "Yes" ? var.RegionIpDictionary : tomap({})

  connectivity_type = "private"
  subnet_id         = aws_subnet.create_vpc_subnet_pvt_2[each.key].id

  tags = {
    Name = "nat-gateway-nonroutable"
  }
}

resource "aws_route_table" "nonroutable_1" {
  for_each = var.IsNonRoutable == "Yes" ? var.RegionIpDictionary : tomap({})

  vpc_id = aws_vpc.create_vpc_in_child_account[each.key].id
  tags = {
    Name = "platform-route-table-nonroutablesubnet"
  }
}


resource "aws_route_table" "nonroutable_2" {
  for_each = var.IsNonRoutable == "Yes" ? var.RegionIpDictionary : tomap({})

  vpc_id = aws_vpc.create_vpc_in_child_account[each.key].id
  tags = {
    Name = "platform-route-table-nonroutablesubnet"
  }
}

resource "aws_route_table_association" "assocaite_to_non_routable_subnet_1" {
  for_each = var.IsNonRoutable == "Yes" ? var.RegionIpDictionary : tomap({})

  subnet_id      = aws_subnet.vpc_nonRoutable_subnet_1[each.key].id
  route_table_id = aws_route_table.nonroutable_1[each.key].id
}

resource "aws_route_table_association" "assocaite_to_non_routable_subnet_2" {
  for_each = var.IsNonRoutable == "Yes" ? var.RegionIpDictionary : tomap({})

  subnet_id      = aws_subnet.vpc_nonRoutable_subnet_2[each.key].id
  route_table_id = aws_route_table.nonroutable_2[each.key].id
}

resource "aws_route" "route_to_non_routable_subnet_1" {
  for_each = var.IsNonRoutable == "Yes" ? var.RegionIpDictionary : tomap({})

  route_table_id            = aws_route_table.nonroutable_1[each.key].id 
  destination_cidr_block    = "0.0.0.0/0"
  nat_gateway_id            = aws_nat_gateway.private_nat_1[each.key].id

}

resource "aws_route" "route_to_non_routable_subnet_2" {
  for_each = var.IsNonRoutable == "Yes" ? var.RegionIpDictionary : tomap({})

  route_table_id            = aws_route_table.nonroutable_2[each.key].id 
  destination_cidr_block    = "0.0.0.0/0"
  nat_gateway_id            = aws_nat_gateway.private_nat_2[each.key].id
}


