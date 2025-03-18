resource "aws_vpc_ipv4_cidr_block_association" "extend_vpc_1" {
 for_each = var.extension_index == "1" || var.extension_index == "2" || var.extension_index == "3" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_cidr_1
}

resource "aws_vpc_ipv4_cidr_block_association" "extend_vpc_2" {
 for_each = var.extension_index == "2" || var.extension_index == "3" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_cidr_2
}

resource "aws_vpc_ipv4_cidr_block_association" "extend_vpc_3" {
 for_each = var.extension_index == "3" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_cidr_3
}

resource "aws_subnet" "vpc_extend_1_subnet_1" {
  for_each = var.extension_index == "1" || var.extension_index == "2" || var.extension_index == "3" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_1_subnet_cidr_1
  availability_zone = "${data.aws_region.current.name}a"

  tags = {
    Name ="platform-private-extend-1-subnet-1"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.extend_vpc_1 ]
}

resource "aws_subnet" "vpc_extend_1_subnet_2" {
  for_each = var.extension_index == "1" || var.extension_index == "2" || var.extension_index == "3" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_1_subnet_cidr_2
  availability_zone = "${data.aws_region.current.name}b"

  tags = {
    Name ="platform-private-extend-1-subnet-2"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.extend_vpc_1 ]
}

resource "aws_subnet" "vpc_extend_1_subnet_3" {
  for_each = (var.extension_index == "1" || var.extension_index == "2" || var.extension_index == "3") && var.Connectivity == "HYB" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_1_subnet_cidr_3
  availability_zone = "${data.aws_region.current.name}a"

  tags = {
    Name ="platform-public-extend-1-subnet-1"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.extend_vpc_1 ]
}

resource "aws_subnet" "vpc_extend_1_subnet_4" {
  for_each = (var.extension_index == "1" || var.extension_index == "2" || var.extension_index == "3") && var.Connectivity == "HYB" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_1_subnet_cidr_4
  availability_zone = "${data.aws_region.current.name}b"

  tags = {
    Name ="platform-public-extend-1-subnet-2"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.extend_vpc_1 ]
}


resource "aws_subnet" "vpc_extend_2_subnet_1" {
  for_each = var.extension_index == "2" || var.extension_index == "3" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_2_subnet_cidr_1
  availability_zone = "${data.aws_region.current.name}a"

  tags = {
    Name ="platform-private-extend-2-subnet-1"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.extend_vpc_2 ]
}

resource "aws_subnet" "vpc_extend_2_subnet_2" {
  for_each = var.extension_index == "2" || var.extension_index == "3" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_2_subnet_cidr_2
  availability_zone = "${data.aws_region.current.name}b"

  tags = {
    Name ="platform-private-extend-2-subnet-2"
  }

 depends_on = [ aws_vpc_ipv4_cidr_block_association.extend_vpc_2 ]
}

resource "aws_subnet" "vpc_extend_2_subnet_3" {
  for_each = (var.extension_index == "2" || var.extension_index == "3") && var.Connectivity == "HYB" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_2_subnet_cidr_3
  availability_zone = "${data.aws_region.current.name}a"

  tags = {
    Name ="platform-public-extend-2-subnet-1"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.extend_vpc_2 ]
}

resource "aws_subnet" "vpc_extend_2_subnet_4" {
  for_each = (var.extension_index == "2" || var.extension_index == "3") && var.Connectivity == "HYB" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_2_subnet_cidr_4
  availability_zone = "${data.aws_region.current.name}b"

  tags = {
    Name ="platform-public-extend-2-subnet-2"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.extend_vpc_2 ]
}


resource "aws_subnet" "vpc_extend_3_subnet_1" {
  for_each = var.extension_index == "3" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_3_subnet_cidr_1
  availability_zone = "${data.aws_region.current.name}a"

  tags = {
    Name ="platform-private-extend-3-subnet-1"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.extend_vpc_3 ]
}

resource "aws_subnet" "vpc_extend_3_subnet_2" {
  for_each = var.extension_index == "3" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_3_subnet_cidr_2
  availability_zone = "${data.aws_region.current.name}b"

  tags = {
    Name ="platform-private-extend-3-subnet-2"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.extend_vpc_3 ]
}

resource "aws_subnet" "vpc_extend_3_subnet_3" {
  for_each = var.extension_index == "3" && var.Connectivity == "HYB" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_3_subnet_cidr_3
  availability_zone = "${data.aws_region.current.name}a"

  tags = {
    Name ="platform-public-extend-3-subnet-1"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.extend_vpc_3 ]
}

resource "aws_subnet" "vpc_extend_3_subnet_4" {
  for_each = var.extension_index == "3" && var.Connectivity == "HYB" ? var.RegionIpDictionary : tomap({})

  vpc_id     = aws_vpc.create_vpc_in_child_account[each.key].id
  cidr_block = each.value.extend_3_subnet_cidr_4
  availability_zone = "${data.aws_region.current.name}b"

  tags = {
    Name ="platform-public-extend-3-subnet-2"
  }

  depends_on = [ aws_vpc_ipv4_cidr_block_association.extend_vpc_3 ]
}